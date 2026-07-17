"""Hard Circuit Breaker — zero-latency binary integrity referee.

Absolute step-function safety substrate for the kinetic universal engine.
When any core telemetry channel breaches its safety baseline, system state
transitions instantaneously from ACTIVE (1) to OVERRIDE (0). No gradual
adjustment curves are permitted.

Integrates with ``kinetic_simulation.AthleteChannel`` / ``KineticLabState``
telemetry fields: shear, deceleration asymmetry, and structural degradation
(tissue debt).
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping, MutableSequence, Sequence

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core binary state
# ---------------------------------------------------------------------------


class SystemState(str, Enum):
    """Binary system integrity state — no intermediate values."""

    ACTIVE = "ACTIVE"      # binary 1
    OVERRIDE = "OVERRIDE"  # binary 0


# Binary encoding of SystemState for zero-latency loop consumers.
STATE_BINARY: dict[SystemState, int] = {
    SystemState.ACTIVE: 1,
    SystemState.OVERRIDE: 0,
}


# ---------------------------------------------------------------------------
# Telemetry & threshold contracts
# ---------------------------------------------------------------------------

# Canonical core-variable keys aligned with kinetic research nodes.
CORE_VARIABLES: tuple[str, ...] = (
    "kinetic_shear",
    "deceleration_asymmetry",
    "structural_degradation_rate",
)


@dataclass(frozen=True, slots=True)
class SafetyThresholds:
    """Immutable safety baselines for core kinetic variables.

    Defaults mirror Kinetic Lab flag thresholds so the breaker and the
    acquisition engine share a single integrity surface.
    """

    kinetic_shear: float = 430.0           # N  (node_1_1 shear flag)
    deceleration_asymmetry: float = 12.0   # %  (node_1_2 asym flag)
    structural_degradation_rate: float = 14.0  # tissue debt (node_1_3)


@dataclass(frozen=True, slots=True)
class TelemetrySample:
    """Single-tick telemetry packet for integrity evaluation.

    Field aliases map directly onto ``AthleteChannel`` attributes so callers
    can construct samples without ad-hoc translation layers.
    """

    kinetic_shear: float = 0.0
    deceleration_asymmetry: float = 0.0
    structural_degradation_rate: float = 0.0
    source_id: str = ""
    tick: int = 0

    @classmethod
    def from_athlete(
        cls,
        *,
        shear_peak_n: float,
        asymmetry_pct: float,
        tissue_debt: float,
        source_id: str = "",
        tick: int = 0,
    ) -> TelemetrySample:
        """Build a sample from kinetic ``AthleteChannel`` field values."""
        return cls(
            kinetic_shear=float(shear_peak_n),
            deceleration_asymmetry=float(asymmetry_pct),
            structural_degradation_rate=float(tissue_debt),
            source_id=source_id,
            tick=tick,
        )


@dataclass(frozen=True, slots=True)
class BreachRecord:
    """Immutable record of a single threshold breach."""

    variable: str
    observed: float
    threshold: float
    source_id: str
    tick: int
    timestamp_ms: int


@dataclass(frozen=True, slots=True)
class IntegrityVerdict:
    """Result of an absolute integrity evaluation pass."""

    system_state: SystemState
    binary: int
    breached: bool
    breaches: tuple[BreachRecord, ...]
    evaluated_at_ms: int

    @property
    def is_override(self) -> bool:
        return self.system_state is SystemState.OVERRIDE


@dataclass(frozen=True, slots=True)
class EdgeAlertPayload:
    """Read-only alert parameters pushed to stateless edge endpoints."""

    system_state: str
    binary: int
    breach_count: int
    breached_variables: tuple[str, ...]
    timestamp_ms: int
    message: str
    read_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Edge dispatch
# ---------------------------------------------------------------------------

EdgeHandler = Callable[[EdgeAlertPayload], None]


def _default_edge_sink(payload: EdgeAlertPayload) -> None:
    """Fallback sink — structured log for visual terminals / actuators."""
    logger.warning(
        "EDGE_ALERT %s",
        json.dumps(payload.to_dict(), separators=(",", ":"), sort_keys=True),
    )


def dispatch_edge_command(
    payload: EdgeAlertPayload,
    *,
    endpoints: Sequence[EdgeHandler] | None = None,
) -> int:
    """Push read-only alert parameters to stateless edge endpoints.

    Each endpoint receives an immutable ``EdgeAlertPayload``. Handlers must
    treat the payload as read-only; this function never mutates system state.

    Returns
    -------
    int
        Count of endpoints that accepted the dispatch without raising.
    """
    handlers: Sequence[EdgeHandler] = (
        tuple(endpoints) if endpoints else (_default_edge_sink,)
    )
    delivered = 0
    for handler in handlers:
        try:
            handler(payload)
            delivered += 1
        except Exception:  # noqa: BLE001 — edge sinks must not abort the breaker
            logger.exception("Edge endpoint dispatch failed: %s", getattr(handler, "__name__", handler))
    return delivered


# ---------------------------------------------------------------------------
# Hard Circuit Breaker
# ---------------------------------------------------------------------------


class HardCircuitBreaker:
    """Zero-latency binary tracking state loop.

    System state is strictly binary:
      * ``1`` / ``ACTIVE``   — all core variables within safety baselines
      * ``0`` / ``OVERRIDE`` — any breach triggers an absolute step to OVERRIDE

    State transitions are instantaneous. There is no hysteresis, ramp, or
    soft-limit curve.
    """

    __slots__ = (
        "_state",
        "_lock",
        "_thresholds",
        "_edge_endpoints",
        "_last_verdict",
        "_trip_count",
        "_on_trip",
    )

    def __init__(
        self,
        thresholds: SafetyThresholds | None = None,
        *,
        edge_endpoints: MutableSequence[EdgeHandler] | None = None,
        on_trip: Callable[[IntegrityVerdict], None] | None = None,
    ) -> None:
        self._state: SystemState = SystemState.ACTIVE
        self._lock = threading.Lock()
        self._thresholds = thresholds or SafetyThresholds()
        self._edge_endpoints: list[EdgeHandler] = list(edge_endpoints or [])
        self._last_verdict: IntegrityVerdict | None = None
        self._trip_count: int = 0
        self._on_trip = on_trip

    # -- accessors -----------------------------------------------------------

    @property
    def system_state(self) -> SystemState:
        with self._lock:
            return self._state

    @property
    def binary(self) -> int:
        return STATE_BINARY[self.system_state]

    @property
    def thresholds(self) -> SafetyThresholds:
        return self._thresholds

    @property
    def trip_count(self) -> int:
        with self._lock:
            return self._trip_count

    @property
    def last_verdict(self) -> IntegrityVerdict | None:
        with self._lock:
            return self._last_verdict

    def register_edge_endpoint(self, handler: EdgeHandler) -> None:
        """Attach a stateless edge consumer for OVERRIDE broadcasts."""
        self._edge_endpoints.append(handler)

    # -- binary tracking loop -----------------------------------------------

    def tracking_loop_tick(
        self,
        telemetry_batch: Sequence[TelemetrySample | Mapping[str, Any]],
    ) -> IntegrityVerdict:
        """Single iteration of the zero-latency binary tracking loop.

        Evaluates the full batch; any breach forces OVERRIDE for the loop.
        """
        return evaluate_system_integrity(
            telemetry_batch,
            self._thresholds,
            breaker=self,
        )

    # -- state machine (absolute step-function) -----------------------------

    def _force_override(self, verdict: IntegrityVerdict) -> None:
        """Absolute ACTIVE(1) → OVERRIDE(0) step. No gradual transition."""
        with self._lock:
            previous = self._state
            self._state = SystemState.OVERRIDE
            self._last_verdict = verdict
            if previous is SystemState.ACTIVE:
                self._trip_count += 1
                just_tripped = True
            else:
                just_tripped = False

        if just_tripped:
            payload = EdgeAlertPayload(
                system_state=SystemState.OVERRIDE.value,
                binary=0,
                breach_count=len(verdict.breaches),
                breached_variables=tuple(b.variable for b in verdict.breaches),
                timestamp_ms=verdict.evaluated_at_ms,
                message=(
                    "HARD CIRCUIT BREAKER TRIP — system integrity compromised. "
                    "Human governance window engaged."
                ),
            )
            dispatch_edge_command(payload, endpoints=self._edge_endpoints or None)
            if self._on_trip is not None:
                try:
                    self._on_trip(verdict)
                except Exception:  # noqa: BLE001
                    logger.exception("on_trip callback failed")

    def acknowledge_recovery(self) -> SystemState:
        """Authorized recovery path — restores ACTIVE after Path A compliance.

        Only callable after human governance has cleared the trip. Does not
        auto-clear; the ledger owns that authorization gate.
        """
        with self._lock:
            self._state = SystemState.ACTIVE
            return self._state

    def force_override_manual(self) -> SystemState:
        """Explicit OVERRIDE latch (warning override / Path B precursor)."""
        now_ms = _now_ms()
        verdict = IntegrityVerdict(
            system_state=SystemState.OVERRIDE,
            binary=0,
            breached=True,
            breaches=(),
            evaluated_at_ms=now_ms,
        )
        self._force_override(verdict)
        return SystemState.OVERRIDE


# ---------------------------------------------------------------------------
# Public referee API
# ---------------------------------------------------------------------------


def evaluate_system_integrity(
    telemetry_data: (
        TelemetrySample
        | Mapping[str, Any]
        | Sequence[TelemetrySample | Mapping[str, Any]]
    ),
    thresholds: SafetyThresholds | Mapping[str, float],
    *,
    breaker: HardCircuitBreaker | None = None,
) -> IntegrityVerdict:
    """Uncompromising algorithmic referee for kinetic system integrity.

    If **any** core variable breaches its safety baseline, the verdict is an
    absolute step to ``System_State = "OVERRIDE"`` (binary 0). There is no
    soft-limit, proportional response, or gradual adjustment curve.

    Parameters
    ----------
    telemetry_data:
        One sample, a mapping, or a sequence of samples/mappings.
    thresholds:
        ``SafetyThresholds`` or a mapping of core-variable ceilings.
    breaker:
        Optional live breaker instance to latch on trip.

    Returns
    -------
    IntegrityVerdict
        Immutable evaluation result including breach records.
    """
    evaluated_at_ms = _now_ms()
    limits = _coerce_thresholds(thresholds)
    samples = _normalize_telemetry(telemetry_data)
    breaches: list[BreachRecord] = []

    for sample in samples:
        for variable in CORE_VARIABLES:
            observed = float(getattr(sample, variable))
            ceiling = float(getattr(limits, variable))
            if observed > ceiling:
                breaches.append(
                    BreachRecord(
                        variable=variable,
                        observed=observed,
                        threshold=ceiling,
                        source_id=sample.source_id,
                        tick=sample.tick,
                        timestamp_ms=evaluated_at_ms,
                    )
                )

    breached = len(breaches) > 0
    # Absolute step-function: any breach → OVERRIDE (0); else ACTIVE (1).
    state = SystemState.OVERRIDE if breached else SystemState.ACTIVE
    verdict = IntegrityVerdict(
        system_state=state,
        binary=STATE_BINARY[state],
        breached=breached,
        breaches=tuple(breaches),
        evaluated_at_ms=evaluated_at_ms,
    )

    if breached and breaker is not None:
        breaker._force_override(verdict)  # noqa: SLF001 — intentional latch
    elif breaker is not None:
        with breaker._lock:  # noqa: SLF001
            breaker._last_verdict = verdict

    return verdict


def telemetry_from_kinetic_lab(state: Any) -> list[TelemetrySample]:
    """Project a ``KineticLabState`` into breaker telemetry samples.

    Accepts the live kinetic lab object without importing the module at
    load time, preserving isolation while staying structurally integrated.
    """
    athletes = getattr(state, "athletes", ()) or ()
    tick = int(getattr(state, "tick", 0) or 0)
    samples: list[TelemetrySample] = []
    for athlete in athletes:
        samples.append(
            TelemetrySample.from_athlete(
                shear_peak_n=float(getattr(athlete, "shear_peak_n", 0.0) or 0.0),
                asymmetry_pct=float(getattr(athlete, "asymmetry_pct", 0.0) or 0.0),
                tissue_debt=float(getattr(athlete, "tissue_debt", 0.0) or 0.0),
                source_id=str(getattr(athlete, "name", "")),
                tick=tick,
            )
        )
    return samples


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _now_ms() -> int:
    return int(time.time() * 1000)


def _coerce_thresholds(
    thresholds: SafetyThresholds | Mapping[str, float],
) -> SafetyThresholds:
    if isinstance(thresholds, SafetyThresholds):
        return thresholds
    return SafetyThresholds(
        kinetic_shear=float(thresholds.get("kinetic_shear", 430.0)),
        deceleration_asymmetry=float(
            thresholds.get("deceleration_asymmetry", 12.0)
        ),
        structural_degradation_rate=float(
            thresholds.get("structural_degradation_rate", 14.0)
        ),
    )


def _normalize_telemetry(
    telemetry_data: (
        TelemetrySample
        | Mapping[str, Any]
        | Sequence[TelemetrySample | Mapping[str, Any]]
    ),
) -> list[TelemetrySample]:
    if isinstance(telemetry_data, TelemetrySample):
        return [telemetry_data]
    if isinstance(telemetry_data, Mapping):
        return [_mapping_to_sample(telemetry_data)]
    if isinstance(telemetry_data, Sequence) and not isinstance(
        telemetry_data, (str, bytes)
    ):
        out: list[TelemetrySample] = []
        for item in telemetry_data:
            if isinstance(item, TelemetrySample):
                out.append(item)
            elif isinstance(item, Mapping):
                out.append(_mapping_to_sample(item))
            else:
                raise TypeError(
                    f"Unsupported telemetry element type: {type(item)!r}"
                )
        return out
    raise TypeError(f"Unsupported telemetry_data type: {type(telemetry_data)!r}")


def _mapping_to_sample(data: Mapping[str, Any]) -> TelemetrySample:
    return TelemetrySample(
        kinetic_shear=float(data.get("kinetic_shear", data.get("shear_peak_n", 0.0))),
        deceleration_asymmetry=float(
            data.get("deceleration_asymmetry", data.get("asymmetry_pct", 0.0))
        ),
        structural_degradation_rate=float(
            data.get(
                "structural_degradation_rate",
                data.get("tissue_debt", 0.0),
            )
        ),
        source_id=str(data.get("source_id", data.get("name", ""))),
        tick=int(data.get("tick", 0) or 0),
    )


__all__ = [
    "CORE_VARIABLES",
    "STATE_BINARY",
    "BreachRecord",
    "EdgeAlertPayload",
    "HardCircuitBreaker",
    "IntegrityVerdict",
    "SafetyThresholds",
    "SystemState",
    "TelemetrySample",
    "dispatch_edge_command",
    "evaluate_system_integrity",
    "telemetry_from_kinetic_lab",
]
