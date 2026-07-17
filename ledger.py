"""Reality Divergence Ledger — Moment of Drift & sovereign audit trail.

When the Hard Circuit Breaker trips, this ledger permanently records the
millisecond of divergence, opens the Human Governance Window, and forks
system reality along Path A (Compliance) or Path B (Failure to Act).

Cryptographic binding via ``generate_sovereign_intelligence_segment()``
produces an indivisible SHA-256 Holistic Audit Segment across four
co-equal components: User Input, System Context, Avatar Output, and
Systemic Interpretation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
import uuid
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from breaker import (
    HardCircuitBreaker,
    IntegrityVerdict,
    SystemState,
    TelemetrySample,
    evaluate_system_integrity,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Governance paths & window
# ---------------------------------------------------------------------------


class GovernancePath(str, Enum):
    """Outcome of the Human Governance Window."""

    PENDING = "PENDING"
    PATH_A_COMPLIANCE = "Path A (Compliance)"
    PATH_B_FAILURE_TO_ACT = "Path B (Failure to Act)"


class DriftStatus(str, Enum):
    """Lifecycle status of a Moment of Drift Record."""

    OPEN = "OPEN"
    RESOLVED_COMPLIANCE = "RESOLVED_COMPLIANCE"
    RESOLVED_FAILURE = "RESOLVED_FAILURE"
    REALITY_FORKED = "REALITY_FORKED"


# Default Human Governance Window duration (milliseconds).
DEFAULT_GOVERNANCE_WINDOW_MS: int = 30_000

# Isolated black-box audit vault (workspace-local designated directory).
SECURE_AUDIT_VAULT_DIR: Path = (
    Path(__file__).resolve().parent / "secure_audit_vault"
)

# Shield confirmation emitted after every successful hard write.
SYSTEM_PROTECTION_SHIELD_MSG = (
    "SYSTEM PROTECTION SHIELD ACTIVE: Un-erasable forensic history written "
    "to isolated disk storage."
)

# Primary audit artifact extension (text SIR blueprint; PDF companion optional).
AUDIT_FILE_EXTENSION = ".txt"


def resolve_audit_log_dir() -> Path:
    """Return the writable isolated audit directory for sovereign receipts.

    Designated vault: ``secure_audit_vault/`` inside the workspace.
    """
    SECURE_AUDIT_VAULT_DIR.mkdir(parents=True, exist_ok=True)
    probe = SECURE_AUDIT_VAULT_DIR / ".write_probe"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink(missing_ok=True)
    return SECURE_AUDIT_VAULT_DIR


AUDIT_LOG_DIR: Path = SECURE_AUDIT_VAULT_DIR


class DivergenceUIStatus(str, Enum):
    """Column-3 foreground status for timeline divergence handling."""

    PENDING = "PENDING"
    COMPLIANT = "COMPLIANT"
    OVERRIDE_HAZARD = "OVERRIDE_HAZARD"


# ---------------------------------------------------------------------------
# Moment of Drift Record
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MomentOfDriftRecord:
    """Permanent stamp that human responsibility has been engaged.

    The ``trip_timestamp_ms`` field is the authoritative millisecond the
    circuit breaker transitioned ACTIVE → OVERRIDE.
    """

    record_id: str
    trip_timestamp_ms: int
    human_responsibility_engaged: bool
    breach_summary: tuple[dict[str, Any], ...]
    pre_drift_snapshot: dict[str, Any]
    governance_window_ms: int
    window_deadline_ms: int
    path: GovernancePath = GovernancePath.PENDING
    status: DriftStatus = DriftStatus.OPEN
    operator_id: str | None = None
    intervention_timestamp_ms: int | None = None
    intervention_input: str | None = None
    override_declared: bool = False
    forked_reality_id: str | None = None
    notes: str = ""


@dataclass(frozen=True, slots=True)
class RealityFork:
    """Mutated data trajectory produced by ``compute_new_reality()``."""

    fork_id: str
    parent_drift_id: str
    forked_at_ms: int
    path: GovernancePath
    pre_drift_readout: dict[str, Any]
    post_drift_readout: dict[str, Any]
    trajectory_mutation: dict[str, Any]
    divergence_score: float


@dataclass(frozen=True, slots=True)
class HolisticAuditSegment:
    """Indivisible sovereign intelligence segment with SHA-256 binding."""

    segment_id: str
    created_at_ms: int
    user_input: dict[str, Any]
    system_context: dict[str, Any]
    avatar_output: dict[str, Any]
    systemic_interpretation: dict[str, Any]
    canonical_payload: str
    block_hash: str  # SHA-256 hex digest — absolute tamper-proof trail

    @property
    def hash(self) -> str:
        """Alias for cryptographic block hash (sovereign report identity)."""
        return self.block_hash

    def verify(self) -> bool:
        """Recompute the block hash; returns True iff the segment is intact."""
        recomputed = _sha256_hex(self.canonical_payload)
        return recomputed == self.block_hash


@dataclass(frozen=True, slots=True)
class SovereignReportDossier:
    """Sovereign Report format ready for isolated-disk hard commit."""

    segment: HolisticAuditSegment
    hash: str
    binary_payload: bytes
    filename: str
    written: bool = False

    @property
    def report_dossier(self) -> HolisticAuditSegment:
        return self.segment


@dataclass(frozen=True, slots=True)
class TimelineDivergenceResult:
    """Outcome of ``handle_timeline_divergence`` dual-tranche dispatch."""

    path: str
    ui_status: DivergenceUIStatus
    fork_id: str | None
    background_export_started: bool
    audit_filename: str | None = None
    notes: str = ""


# ---------------------------------------------------------------------------
# Reality Divergence Ledger
# ---------------------------------------------------------------------------


class RealityDivergenceLedger:
    """Append-only ledger for drift moments, governance, and reality forks.

    Thread-safe. Records are never mutated in place; resolution produces a
    successor record (or an updated frozen replacement stored by id).
    """

    __slots__ = (
        "_lock",
        "_records",
        "_forks",
        "_audit_segments",
        "_active_drift_id",
        "_governance_window_ms",
        "_authenticated_operators",
        "_breaker",
    )

    def __init__(
        self,
        *,
        governance_window_ms: int = DEFAULT_GOVERNANCE_WINDOW_MS,
        authenticated_operators: Sequence[str] | None = None,
        breaker: HardCircuitBreaker | None = None,
    ) -> None:
        self._lock = threading.Lock()
        self._records: dict[str, MomentOfDriftRecord] = {}
        self._forks: dict[str, RealityFork] = {}
        self._audit_segments: list[HolisticAuditSegment] = []
        self._active_drift_id: str | None = None
        self._governance_window_ms = max(1, int(governance_window_ms))
        self._authenticated_operators: set[str] = set(authenticated_operators or ())
        self._breaker = breaker

    # -- accessors -----------------------------------------------------------

    @property
    def active_drift(self) -> MomentOfDriftRecord | None:
        with self._lock:
            if self._active_drift_id is None:
                return None
            return self._records.get(self._active_drift_id)

    @property
    def records(self) -> tuple[MomentOfDriftRecord, ...]:
        with self._lock:
            return tuple(self._records.values())

    @property
    def forks(self) -> tuple[RealityFork, ...]:
        with self._lock:
            return tuple(self._forks.values())

    @property
    def audit_segments(self) -> tuple[HolisticAuditSegment, ...]:
        with self._lock:
            return tuple(self._audit_segments)

    def register_operator(self, operator_id: str) -> None:
        """Authorize an operator for Path A intervention."""
        if not operator_id or not str(operator_id).strip():
            raise ValueError("operator_id must be a non-empty string")
        with self._lock:
            self._authenticated_operators.add(str(operator_id).strip())

    def is_authenticated(self, operator_id: str) -> bool:
        with self._lock:
            return operator_id in self._authenticated_operators

    # -- Moment of Drift -----------------------------------------------------

    def record_moment_of_drift(
        self,
        verdict: IntegrityVerdict,
        *,
        pre_drift_snapshot: Mapping[str, Any] | None = None,
        governance_window_ms: int | None = None,
    ) -> MomentOfDriftRecord:
        """Permanently log the millisecond the circuit breaker tripped.

        Explicitly stamps that human responsibility has been engaged.
        """
        window_ms = (
            int(governance_window_ms)
            if governance_window_ms is not None
            else self._governance_window_ms
        )
        trip_ms = int(verdict.evaluated_at_ms)
        record = MomentOfDriftRecord(
            record_id=_new_id("drift"),
            trip_timestamp_ms=trip_ms,
            human_responsibility_engaged=True,
            breach_summary=tuple(
                {
                    "variable": b.variable,
                    "observed": b.observed,
                    "threshold": b.threshold,
                    "source_id": b.source_id,
                    "tick": b.tick,
                }
                for b in verdict.breaches
            ),
            pre_drift_snapshot=dict(pre_drift_snapshot or _snapshot_from_verdict(verdict)),
            governance_window_ms=window_ms,
            window_deadline_ms=trip_ms + window_ms,
            path=GovernancePath.PENDING,
            status=DriftStatus.OPEN,
            notes="Human responsibility engaged at circuit-breaker trip.",
        )
        with self._lock:
            self._records[record.record_id] = record
            self._active_drift_id = record.record_id
        logger.critical(
            "MOMENT_OF_DRIFT id=%s trip_ms=%s human_responsibility=ENGAGED",
            record.record_id,
            trip_ms,
        )
        return record

    # -- Human Governance Window --------------------------------------------

    def governance_window_remaining_ms(
        self,
        *,
        now_ms: int | None = None,
    ) -> int:
        """Milliseconds remaining in the active Human Governance Window."""
        drift = self.active_drift
        if drift is None or drift.status is not DriftStatus.OPEN:
            return 0
        now = _now_ms() if now_ms is None else int(now_ms)
        return max(0, drift.window_deadline_ms - now)

    def submit_intervention(
        self,
        operator_id: str,
        intervention_input: str,
        *,
        now_ms: int | None = None,
    ) -> MomentOfDriftRecord:
        """Authenticated operator intervention within the governance window.

        On valid input inside the window → Path A (Compliance) and breaker
        recovery is authorized.
        """
        now = _now_ms() if now_ms is None else int(now_ms)
        with self._lock:
            if not operator_id or operator_id not in self._authenticated_operators:
                raise PermissionError(
                    f"Operator '{operator_id}' is not authenticated for governance."
                )
            if self._active_drift_id is None:
                raise RuntimeError("No open Moment of Drift to intervene upon.")
            current = self._records[self._active_drift_id]
            if current.status is not DriftStatus.OPEN:
                raise RuntimeError(
                    f"Drift {current.record_id} is already resolved ({current.status.value})."
                )
            if now > current.window_deadline_ms:
                raise TimeoutError(
                    "Human Governance Window has closed; use tick_governance_window()."
                )
            if not intervention_input or not str(intervention_input).strip():
                raise ValueError("intervention_input must be a non-empty valid directive.")

            resolved = MomentOfDriftRecord(
                record_id=current.record_id,
                trip_timestamp_ms=current.trip_timestamp_ms,
                human_responsibility_engaged=True,
                breach_summary=current.breach_summary,
                pre_drift_snapshot=current.pre_drift_snapshot,
                governance_window_ms=current.governance_window_ms,
                window_deadline_ms=current.window_deadline_ms,
                path=GovernancePath.PATH_A_COMPLIANCE,
                status=DriftStatus.RESOLVED_COMPLIANCE,
                operator_id=operator_id,
                intervention_timestamp_ms=now,
                intervention_input=str(intervention_input).strip(),
                override_declared=False,
                forked_reality_id=current.forked_reality_id,
                notes="Path A (Compliance) — authenticated intervention accepted.",
            )
            self._records[resolved.record_id] = resolved

        # Authorize breaker recovery outside the lock to avoid re-entrancy hazards.
        if self._breaker is not None:
            self._breaker.acknowledge_recovery()
        logger.info(
            "PATH_A_COMPLIANCE drift=%s operator=%s",
            resolved.record_id,
            operator_id,
        )
        return resolved

    def declare_warning_override(
        self,
        *,
        operator_id: str | None = None,
        now_ms: int | None = None,
    ) -> MomentOfDriftRecord:
        """Explicit warning override → Path B (Failure to Act)."""
        now = _now_ms() if now_ms is None else int(now_ms)
        return self._resolve_path_b(
            reason="Warning explicitly overridden.",
            operator_id=operator_id,
            now_ms=now,
            override_declared=True,
        )

    def tick_governance_window(
        self,
        *,
        now_ms: int | None = None,
    ) -> MomentOfDriftRecord | None:
        """Tracking loop tick for the Human Governance Window.

        If the window expires with no valid human input, automatically
        triggers Path B (Failure to Act).
        """
        now = _now_ms() if now_ms is None else int(now_ms)
        with self._lock:
            if self._active_drift_id is None:
                return None
            current = self._records[self._active_drift_id]
            if current.status is not DriftStatus.OPEN:
                return current
            if now <= current.window_deadline_ms:
                return current  # still within window — no action

        return self._resolve_path_b(
            reason="No human input detected within governance window.",
            operator_id=None,
            now_ms=now,
            override_declared=False,
        )

    def _resolve_path_b(
        self,
        *,
        reason: str,
        operator_id: str | None,
        now_ms: int,
        override_declared: bool,
    ) -> MomentOfDriftRecord:
        with self._lock:
            if self._active_drift_id is None:
                raise RuntimeError("No open Moment of Drift for Path B resolution.")
            current = self._records[self._active_drift_id]
            if current.status is not DriftStatus.OPEN:
                return current
            resolved = MomentOfDriftRecord(
                record_id=current.record_id,
                trip_timestamp_ms=current.trip_timestamp_ms,
                human_responsibility_engaged=True,
                breach_summary=current.breach_summary,
                pre_drift_snapshot=current.pre_drift_snapshot,
                governance_window_ms=current.governance_window_ms,
                window_deadline_ms=current.window_deadline_ms,
                path=GovernancePath.PATH_B_FAILURE_TO_ACT,
                status=DriftStatus.RESOLVED_FAILURE,
                operator_id=operator_id,
                intervention_timestamp_ms=now_ms,
                intervention_input=None,
                override_declared=override_declared,
                forked_reality_id=current.forked_reality_id,
                notes=f"Path B (Failure to Act) — {reason}",
            )
            self._records[resolved.record_id] = resolved

        logger.critical(
            "PATH_B_FAILURE_TO_ACT drift=%s reason=%s",
            resolved.record_id,
            reason,
        )
        return resolved

    # -- Reality fork --------------------------------------------------------

    def compute_new_reality(
        self,
        *,
        drift_id: str | None = None,
        live_telemetry: Sequence[TelemetrySample | Mapping[str, Any]] | None = None,
        cost_avoidance_projection: Mapping[str, float] | None = None,
    ) -> RealityFork:
        """Fork the timeline from the pre-drift intersection point.

        Produces a fundamentally mutated data trajectory and a different
        system readout compared to the pre-drift snapshot. On Path B the
        engine is reactivated under the compromised / hazardous parameters.
        """
        with self._lock:
            target_id = drift_id or self._active_drift_id
            if target_id is None or target_id not in self._records:
                raise KeyError("No Moment of Drift available for reality fork.")
            drift = self._records[target_id]
            if drift.status is DriftStatus.OPEN:
                raise RuntimeError(
                    "Cannot fork reality while governance window is still OPEN."
                )

        pre = deepcopy(dict(drift.pre_drift_snapshot))
        path = drift.path
        mutation = _mutate_trajectory(
            pre,
            path=path,
            live_telemetry=live_telemetry,
            cost_avoidance_projection=cost_avoidance_projection,
        )
        post_readout = mutation["post_drift_readout"]
        divergence_score = float(mutation["divergence_score"])

        # Path B: reactivate engine under compromised / hazardous parameters.
        if path is GovernancePath.PATH_B_FAILURE_TO_ACT and self._breaker is not None:
            # Leave breaker in OVERRIDE (hazardous latch) while marking engine
            # reactivation under compromised parameters in the readout.
            if self._breaker.system_state is not SystemState.OVERRIDE:
                self._breaker.force_override_manual()
            post_readout["engine_reactivated_under_hazard"] = True
            post_readout["system_state"] = SystemState.OVERRIDE.value
        elif path is GovernancePath.PATH_A_COMPLIANCE:
            post_readout["engine_recovered"] = True
            post_readout["system_state"] = SystemState.ACTIVE.value
            if self._breaker is not None:
                self._breaker.acknowledge_recovery()

        fork = RealityFork(
            fork_id=_new_id("fork"),
            parent_drift_id=drift.record_id,
            forked_at_ms=_now_ms(),
            path=path,
            pre_drift_readout=pre,
            post_drift_readout=post_readout,
            trajectory_mutation=mutation["trajectory_mutation"],
            divergence_score=divergence_score,
        )

        with self._lock:
            self._forks[fork.fork_id] = fork
            updated = MomentOfDriftRecord(
                record_id=drift.record_id,
                trip_timestamp_ms=drift.trip_timestamp_ms,
                human_responsibility_engaged=drift.human_responsibility_engaged,
                breach_summary=drift.breach_summary,
                pre_drift_snapshot=drift.pre_drift_snapshot,
                governance_window_ms=drift.governance_window_ms,
                window_deadline_ms=drift.window_deadline_ms,
                path=drift.path,
                status=DriftStatus.REALITY_FORKED,
                operator_id=drift.operator_id,
                intervention_timestamp_ms=drift.intervention_timestamp_ms,
                intervention_input=drift.intervention_input,
                override_declared=drift.override_declared,
                forked_reality_id=fork.fork_id,
                notes=drift.notes,
            )
            self._records[updated.record_id] = updated

        logger.warning(
            "REALITY_FORK id=%s parent=%s path=%s divergence=%.4f",
            fork.fork_id,
            drift.record_id,
            path.value,
            divergence_score,
        )
        return fork


# ---------------------------------------------------------------------------
# Sovereign Intelligence Segment (cryptographic binding)
# ---------------------------------------------------------------------------


def generate_sovereign_intelligence_segment(
    session_data: Mapping[str, Any] | None = None,
    *,
    user_input: Mapping[str, Any] | None = None,
    system_context: Mapping[str, Any] | None = None,
    avatar_output: Mapping[str, Any] | None = None,
    systemic_interpretation: Mapping[str, Any] | None = None,
    ledger: RealityDivergenceLedger | None = None,
) -> HolisticAuditSegment:
    """Compile a Holistic Audit Segment with co-equal cryptographic binding.

    Four components are bound with equal weight into a single canonical
    payload, then hashed with SHA-256 to produce an absolute, tamper-proof
    audit trail for system protection and independent liability verification.

    Accepts either explicit quadrant kwargs **or** a ``session_data`` mapping
    containing the four co-equal keys (Sovereign Report format).

    Components
    ----------
    user_input:
        Conversations / supplied operator data.
    system_context:
        Digital twin state at the audit boundary.
    avatar_output:
        Verbal declarations / directives issued by the system avatar.
    systemic_interpretation:
        Underlying mathematical math / cost-avoidance projections.
    """
    quadrants = _resolve_session_quadrants(
        session_data,
        user_input=user_input,
        system_context=system_context,
        avatar_output=avatar_output,
        systemic_interpretation=systemic_interpretation,
    )
    # Co-equal weight: each component occupies a named top-level key with
    # identical structural standing in the canonical serialization.
    envelope: dict[str, Any] = {
        "schema": "sovereign_intelligence_segment.v1",
        "weighting": {
            "user_input": 1.0,
            "system_context": 1.0,
            "avatar_output": 1.0,
            "systemic_interpretation": 1.0,
        },
        "components": {
            "user_input": _canonicalize_component(quadrants["user_input"]),
            "system_context": _canonicalize_component(quadrants["system_context"]),
            "avatar_output": _canonicalize_component(quadrants["avatar_output"]),
            "systemic_interpretation": _canonicalize_component(
                quadrants["systemic_interpretation"]
            ),
        },
    }
    canonical_payload = _canonical_json(envelope)
    block_hash = _sha256_hex(canonical_payload)
    segment = HolisticAuditSegment(
        segment_id=_new_id("sis"),
        created_at_ms=_now_ms(),
        user_input=dict(envelope["components"]["user_input"]),
        system_context=dict(envelope["components"]["system_context"]),
        avatar_output=dict(envelope["components"]["avatar_output"]),
        systemic_interpretation=dict(
            envelope["components"]["systemic_interpretation"]
        ),
        canonical_payload=canonical_payload,
        block_hash=block_hash,
    )
    if ledger is not None:
        with ledger._lock:  # noqa: SLF001 — intentional append to ledger store
            ledger._audit_segments.append(segment)
    logger.info(
        "SOVEREIGN_SEGMENT id=%s hash=%s",
        segment.segment_id,
        segment.block_hash,
    )
    return segment


def _resolve_session_quadrants(
    session_data: Mapping[str, Any] | None,
    *,
    user_input: Mapping[str, Any] | None,
    system_context: Mapping[str, Any] | None,
    avatar_output: Mapping[str, Any] | None,
    systemic_interpretation: Mapping[str, Any] | None,
) -> dict[str, Mapping[str, Any]]:
    """Merge session_data + explicit kwargs into the four co-equal quadrants."""
    data = dict(session_data or {})
    return {
        "user_input": user_input
        if user_input is not None
        else dict(data.get("user_input") or data.get("conversation") or {}),
        "system_context": system_context
        if system_context is not None
        else dict(data.get("system_context") or data.get("digital_twin") or {}),
        "avatar_output": avatar_output
        if avatar_output is not None
        else dict(data.get("avatar_output") or data.get("avatar_voice") or {}),
        "systemic_interpretation": systemic_interpretation
        if systemic_interpretation is not None
        else dict(
            data.get("systemic_interpretation")
            or data.get("mathematical_interpretation")
            or {}
        ),
    }


# ---------------------------------------------------------------------------
# Dual-tranche Path B: silent background sovereign export
# ---------------------------------------------------------------------------


def write_to_isolated_disk(filename: str | Path, binary_payload: bytes) -> Path:
    """Hard-commit a binary payload to the isolated audit storage node."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create where possible — refuse silent overwrite of an audit seal.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(str(path), flags, 0o600)
    except FileExistsError:
        # Idempotent re-seal with identical bytes is permitted; diverge → error.
        existing = path.read_bytes()
        if existing != binary_payload:
            raise FileExistsError(
                f"Audit seal already exists with different payload: {path}"
            ) from None
        return path
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(binary_payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return path


def format_sovereign_intelligence_report(
    segment: HolisticAuditSegment,
    *,
    path_label: str | None = None,
) -> str:
    """Render the stark official Sovereign Intelligence Report layout blueprint.

    Four co-equal quadrants are printed in fixed order with the SHA-256 seal
    as the absolute cryptographic binding across the entire dossier.
    """
    path_line = path_label or (
        (segment.systemic_interpretation or {}).get("path")
        or (segment.avatar_output or {}).get("directive")
        or "UNDECLARED"
    )
    divider = "=" * 72
    thin = "-" * 72
    sections = [
        divider,
        "SOVEREIGN INTELLIGENCE REPORT",
        "Holistic Audit Segment — Absolute Cryptographic Binding",
        divider,
        f"Segment ID      : {segment.segment_id}",
        f"Created (ms)    : {segment.created_at_ms}",
        f"Governance Path : {path_line}",
        f"Schema          : sovereign_intelligence_segment.v1",
        f"Integrity Check : {'VERIFIED' if segment.verify() else 'FAILED'}",
        thin,
        "QUADRANT I  — USER INPUT",
        _canonical_json(segment.user_input),
        thin,
        "QUADRANT II — SYSTEM CONTEXT (Digital Twin)",
        _canonical_json(segment.system_context),
        thin,
        "QUADRANT III — AVATAR OUTPUT (Verbal Declarations / Directives)",
        _canonical_json(segment.avatar_output),
        thin,
        "QUADRANT IV — SYSTEMIC INTERPRETATION (Math / Cost-Avoidance)",
        _canonical_json(segment.systemic_interpretation),
        thin,
        "SHA-256 BLOCK HASH (UN-ALTERABLE SEAL)",
        segment.block_hash,
        divider,
        "STATUS: SEALED — TAMPER-PROOF FORENSIC AUDIT TRAIL",
        divider,
        "",
    ]
    return "\n".join(sections)


def _build_sovereign_pdf(segment: HolisticAuditSegment) -> bytes:
    """Minimal PDF companion placeholder embedding the sovereign hash receipt."""
    lines = [
        "SOVEREIGN INTELLIGENCE REPORT (PDF PLACEHOLDER)",
        f"Segment: {segment.segment_id}",
        f"Created (ms): {segment.created_at_ms}",
        f"SHA-256: {segment.block_hash}",
        "Quadrants: User Input | System Context | Avatar Output | Systemic Interpretation",
        f"Verified: {segment.verify()}",
        "Schema: sovereign_intelligence_segment.v1",
        "STATUS: SEALED — TAMPER-PROOF AUDIT TRAIL",
        "Primary artifact: AUDIT_[SHA256].txt in secure_audit_vault/",
    ]
    content_lines = []
    y = 750
    for line in lines:
        safe = (
            line.replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )
        content_lines.append(f"BT /F1 9 Tf 40 {y} Td ({safe}) Tj ET")
        y -= 16
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects: list[bytes] = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        (
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
        ),
        (
            f"4 0 obj<< /Length {len(stream)} >>stream\n".encode("ascii")
            + stream
            + b"\nendstream\nendobj\n"
        ),
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>endobj\n",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(out))
        out.extend(obj)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)


def compile_sovereign_report_dossier(
    session_data: Mapping[str, Any],
    *,
    ledger: RealityDivergenceLedger | None = None,
    as_text: bool = True,
) -> SovereignReportDossier:
    """Compile the four co-equal quadrants into the Sovereign Report format.

    Primary artifact is ``AUDIT_{SHA256}.txt`` (official SIR blueprint).
    Set ``as_text=False`` to emit the PDF placeholder companion instead.
    """
    segment = generate_sovereign_intelligence_segment(
        session_data,
        ledger=ledger,
    )
    audit_dir = resolve_audit_log_dir()
    if as_text:
        report_body = format_sovereign_intelligence_report(segment)
        binary_payload = report_body.encode("utf-8")
        filename = str(audit_dir / f"AUDIT_{segment.hash}{AUDIT_FILE_EXTENSION}")
    else:
        binary_payload = _build_sovereign_pdf(segment)
        filename = str(audit_dir / f"AUDIT_{segment.hash}.pdf")
    return SovereignReportDossier(
        segment=segment,
        hash=segment.hash,
        binary_payload=binary_payload,
        filename=filename,
        written=False,
    )


def execute_silent_background_export(
    session_data: Mapping[str, Any],
    *,
    ledger: RealityDivergenceLedger | None = None,
    dossier: SovereignReportDossier | None = None,
    daemon: bool = True,
    triggered_at_ms: int | None = None,
) -> threading.Thread:
    """Fire an isolated background thread for absolute system protection.

    Spawned at the exact millisecond Path B is triggered. Compiles the full
    Holistic Audit Segment into the Sovereign Intelligence Report blueprint and
    hard-commits ``AUDIT_{SHA256}.txt`` under ``secure_audit_vault/`` without
    blocking the foreground telemetry / UI tranche.
    """
    frozen = json.loads(json.dumps(dict(session_data), default=str))
    prebuilt = dossier
    trip_ms = int(triggered_at_ms if triggered_at_ms is not None else _now_ms())

    def _worker() -> None:
        try:
            report = prebuilt or compile_sovereign_report_dossier(
                frozen, ledger=ledger, as_text=True
            )
            path = write_to_isolated_disk(report.filename, report.binary_payload)
            # Clean console confirmation — absolute forensic seal.
            print(SYSTEM_PROTECTION_SHIELD_MSG, flush=True)
            print(
                f"  → vault={path}  hash={report.hash}  "
                f"triggered_ms={trip_ms}  bytes={len(report.binary_payload)}",
                flush=True,
            )
            logger.critical(
                "SILENT_AUDIT_EXPORT path=%s hash=%s triggered_ms=%s bytes=%d",
                path,
                report.hash,
                trip_ms,
                len(report.binary_payload),
            )
        except Exception:  # noqa: BLE001 — never crash the UI tranche
            logger.exception("Silent background audit export failed")

    thread = threading.Thread(
        target=_worker,
        name="sovereign-silent-audit-export",
        daemon=daemon,
    )
    thread.start()
    return thread


def export_sovereign_report_sync(
    session_data: Mapping[str, Any],
    *,
    ledger: RealityDivergenceLedger | None = None,
    write_vault: bool = False,
) -> SovereignReportDossier:
    """Foreground/manual export path — compile SIR without blocking telemetry.

    Returns the dossier (text blueprint + hash). Optionally hard-writes to
    ``secure_audit_vault/`` when ``write_vault`` is True.
    """
    dossier = compile_sovereign_report_dossier(
        session_data, ledger=ledger, as_text=True
    )
    if write_vault:
        write_to_isolated_disk(dossier.filename, dossier.binary_payload)
        print(SYSTEM_PROTECTION_SHIELD_MSG, flush=True)
        return SovereignReportDossier(
            segment=dossier.segment,
            hash=dossier.hash,
            binary_payload=dossier.binary_payload,
            filename=dossier.filename,
            written=True,
        )
    return dossier


def build_session_data_from_lab(
    lab: Any,
    *,
    path: str,
    intervention: str | None = None,
    operator_id: str | None = None,
) -> dict[str, Any]:
    """Assemble the four co-equal quadrants from a live kinetic lab state."""
    breaker = getattr(lab, "circuit_breaker", None)
    ledger = getattr(lab, "divergence_ledger", None)
    drift = ledger.active_drift if ledger is not None else None
    fork = ledger.forks[-1] if ledger is not None and ledger.forks else None
    return {
        "user_input": {
            "operator_id": operator_id,
            "intervention": intervention,
            "path_selection": path,
            "conversation": intervention
            or ("Path B — warning bypass / governance timeout"),
        },
        "system_context": build_system_context_from_kinetic(lab, breaker=breaker),
        "avatar_output": {
            "verbal_declaration": (
                "HARD CIRCUIT BREAKER TRIP — human governance window engaged."
                if drift is not None
                else "System nominal."
            ),
            "directive": path,
            "drift_id": getattr(drift, "record_id", None),
            "fork_id": getattr(fork, "fork_id", None),
        },
        "systemic_interpretation": {
            "path": path,
            "breach_summary": list(getattr(drift, "breach_summary", ()) or ()),
            "divergence_score": getattr(fork, "divergence_score", None),
            "cost_avoidance_projection": (
                (getattr(fork, "post_drift_readout", {}) or {}).get(
                    "cost_avoidance_projection"
                )
                if fork is not None
                else {}
            ),
            "trip_timestamp_ms": getattr(drift, "trip_timestamp_ms", None),
        },
        "ui": {
            "column_3_status": DivergenceUIStatus.PENDING.value,
        },
    }


def apply_path_selection_to_lab(
    lab: Any,
    path_selection: str,
    *,
    operator_id: str = "lab_operator",
    intervention: str | None = None,
) -> dict[str, Any]:
    """Resolve Path A / Path B against the live ledger bound to ``lab``."""
    ledger = getattr(lab, "divergence_ledger", None)
    if ledger is None:
        raise RuntimeError("Lab has no divergence ledger bound.")

    key = path_selection.strip().upper().replace(" ", "_")
    if key in {"PATH_A", "PATH_A_COMPLIANCE", "A", "COMPLIANCE"}:
        if ledger.active_drift and ledger.active_drift.status.value == "OPEN":
            ledger.register_operator(operator_id)
            ledger.submit_intervention(
                operator_id,
                intervention or "Supervised load reduction — Path A compliance.",
            )
        if ledger.active_drift and ledger.active_drift.forked_reality_id is None:
            if ledger.active_drift.status.value != "OPEN":
                ledger.compute_new_reality()
        lab.integrity_override = False
        path = "PATH_A"
    elif key in {"PATH_B", "PATH_B_FAILURE_TO_ACT", "B", "OVERRIDE", "FAILURE"}:
        if ledger.active_drift and ledger.active_drift.status.value == "OPEN":
            ledger.declare_warning_override(operator_id=operator_id)
        if ledger.active_drift and ledger.active_drift.forked_reality_id is None:
            if ledger.active_drift.status.value != "OPEN":
                ledger.compute_new_reality()
        # Reactivate under compromised / hazardous parameters.
        lab.integrity_override = False
        path = "PATH_B"
    else:
        raise ValueError(f"Unknown path_selection: {path_selection!r}")

    return build_session_data_from_lab(
        lab,
        path=path,
        intervention=intervention,
        operator_id=operator_id,
    )


def handle_timeline_divergence(
    session_data: MutableMapping[str, Any] | Mapping[str, Any],
    path_selection: str,
    *,
    ledger: RealityDivergenceLedger | None = None,
    ui_updater: Any | None = None,
    start_background_export: bool = True,
) -> TimelineDivergenceResult:
    """Dispatch Path A / Path B timeline divergence.

    Path A — remain in the standard loop; foreground UI marked COMPLIANT
    while awaiting further manual UI requests.

    Path B — dual-tranche execution:
      1. Foreground UI reflects mutated reality (OVERRIDE_HAZARD)
      2. Isolated background thread hard-commits AUDIT_{SHA256}.txt
         into secure_audit_vault/ (zero latency on the live telemetry loop)
    """
    data: dict[str, Any] = dict(session_data)
    key = path_selection.strip().upper().replace(" ", "_")
    if key in {"PATH_A", "PATH_A_COMPLIANCE", "A", "COMPLIANCE"}:
        status = DivergenceUIStatus.COMPLIANT
        if ui_updater is not None:
            ui_updater(data, status=status.value)
        else:
            data.setdefault("ui", {})["column_3_status"] = status.value
        if isinstance(session_data, dict):
            session_data.setdefault("ui", {})["column_3_status"] = status.value
        return TimelineDivergenceResult(
            path="PATH_A",
            ui_status=status,
            fork_id=(data.get("avatar_output") or {}).get("fork_id"),
            background_export_started=False,
            notes="Path A — COMPLIANT; awaiting manual UI request in standard loop.",
        )

    if key in {"PATH_B", "PATH_B_FAILURE_TO_ACT", "B", "OVERRIDE", "FAILURE"}:
        # Exact millisecond Path B (Failure to Act / Manual Override) fires.
        triggered_at_ms = _now_ms()
        status = DivergenceUIStatus.OVERRIDE_HAZARD
        if ui_updater is not None:
            ui_updater(data, status=status.value)
        else:
            data.setdefault("ui", {})["column_3_status"] = status.value
        if isinstance(session_data, dict):
            session_data.setdefault("ui", {})["column_3_status"] = status.value
            session_data.setdefault("systemic_interpretation", {})[
                "path_b_triggered_ms"
            ] = triggered_at_ms
        data.setdefault("systemic_interpretation", {})[
            "path_b_triggered_ms"
        ] = triggered_at_ms

        export_started = False
        audit_filename = None
        if start_background_export:
            # Spawn immediately — compile + hard-write run entirely off-thread
            # so the primary live telemetry loop incurs no export latency.
            execute_silent_background_export(
                data,
                ledger=ledger,
                triggered_at_ms=triggered_at_ms,
            )
            export_started = True
            # Deterministic vault path pattern (hash finalized inside worker).
            audit_filename = str(
                resolve_audit_log_dir() / f"AUDIT_*{AUDIT_FILE_EXTENSION}"
            )

        return TimelineDivergenceResult(
            path="PATH_B",
            ui_status=status,
            fork_id=(data.get("avatar_output") or {}).get("fork_id"),
            background_export_started=export_started,
            audit_filename=audit_filename,
            notes=(
                f"Path B — dual-tranche at ms={triggered_at_ms}: "
                "UI OVERRIDE_HAZARD + silent secure_audit_vault export."
            ),
        )

    raise ValueError(f"Unknown path_selection: {path_selection!r}")


def build_system_context_from_kinetic(
    state: Any,
    *,
    breaker: HardCircuitBreaker | None = None,
) -> dict[str, Any]:
    """Project kinetic lab state into a digital-twin system context dict."""
    athletes = getattr(state, "athletes", ()) or ()
    context: dict[str, Any] = {
        "tick": int(getattr(state, "tick", 0) or 0),
        "running": bool(getattr(state, "running", False)),
        "shear_alerts": int(getattr(state, "shear_alerts", 0) or 0),
        "asymmetry_alerts": int(getattr(state, "asymmetry_alerts", 0) or 0),
        "unlocked_nodes": sorted(
            str(n) for n in (getattr(state, "unlocked_nodes", set()) or set())
        ),
        "athletes": [
            {
                "name": str(getattr(a, "name", "")),
                "state": str(
                    getattr(getattr(a, "state", None), "value", getattr(a, "state", ""))
                ),
                "shear_peak_n": float(getattr(a, "shear_peak_n", 0.0) or 0.0),
                "asymmetry_pct": float(getattr(a, "asymmetry_pct", 0.0) or 0.0),
                "tissue_debt": float(getattr(a, "tissue_debt", 0.0) or 0.0),
            }
            for a in athletes
        ],
    }
    if breaker is not None:
        context["breaker"] = {
            "system_state": breaker.system_state.value,
            "binary": breaker.binary,
            "trip_count": breaker.trip_count,
        }
    return context


def bind_breaker_to_ledger(
    breaker: HardCircuitBreaker,
    ledger: RealityDivergenceLedger,
    *,
    snapshot_provider: Any | None = None,
) -> None:
    """Wire breaker trip callbacks into Moment of Drift recording.

    ``snapshot_provider`` may be a callable returning a mapping, or a kinetic
    lab state object consumed by ``build_system_context_from_kinetic``.
    """

    def _on_trip(verdict: IntegrityVerdict) -> None:
        if callable(snapshot_provider):
            snapshot = snapshot_provider()
        elif snapshot_provider is not None:
            snapshot = build_system_context_from_kinetic(
                snapshot_provider, breaker=breaker
            )
        else:
            snapshot = _snapshot_from_verdict(verdict)
        ledger.record_moment_of_drift(verdict, pre_drift_snapshot=snapshot)

    breaker._on_trip = _on_trip  # noqa: SLF001 — intentional binding hook
    ledger._breaker = breaker  # noqa: SLF001


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def _sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization for cryptographic binding."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_json_default,
    )


def _json_default(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    raise TypeError(f"Object of type {type(obj)!r} is not JSON serializable")


def _canonicalize_component(component: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-copy and normalize a component for co-equal binding."""
    return json.loads(_canonical_json(dict(component)))


def _snapshot_from_verdict(verdict: IntegrityVerdict) -> dict[str, Any]:
    return {
        "evaluated_at_ms": verdict.evaluated_at_ms,
        "system_state": verdict.system_state.value,
        "binary": verdict.binary,
        "breach_count": len(verdict.breaches),
        "breaches": [asdict(b) for b in verdict.breaches],
    }


def _mutate_trajectory(
    pre_drift: Mapping[str, Any],
    *,
    path: GovernancePath,
    live_telemetry: Sequence[TelemetrySample | Mapping[str, Any]] | None,
    cost_avoidance_projection: Mapping[str, float] | None,
) -> dict[str, Any]:
    """Produce a mutated trajectory distinct from the pre-drift intersection."""
    post: MutableMapping[str, Any] = deepcopy(dict(pre_drift))
    mutation: dict[str, Any] = {
        "path": path.value,
        "mutation_ops": [],
    }

    # Scale factors diverge by governance path — Path B retains hazard bias.
    if path is GovernancePath.PATH_A_COMPLIANCE:
        shear_scale = 0.72
        asym_scale = 0.65
        debt_scale = 0.55
        mutation["mutation_ops"].append("compliance_load_attenuation")
    else:
        shear_scale = 1.18
        asym_scale = 1.25
        debt_scale = 1.35
        mutation["mutation_ops"].append("hazard_parameter_reactivation")

    athletes = post.get("athletes")
    if isinstance(athletes, list):
        mutated_athletes = []
        for athlete in athletes:
            if not isinstance(athlete, dict):
                mutated_athletes.append(athlete)
                continue
            entry = dict(athlete)
            entry["shear_peak_n"] = round(
                float(entry.get("shear_peak_n", 0.0)) * shear_scale, 3
            )
            entry["asymmetry_pct"] = round(
                float(entry.get("asymmetry_pct", 0.0)) * asym_scale, 3
            )
            entry["tissue_debt"] = round(
                float(entry.get("tissue_debt", 0.0)) * debt_scale, 3
            )
            entry["trajectory_epoch"] = "post_drift"
            mutated_athletes.append(entry)
        post["athletes"] = mutated_athletes
        mutation["mutation_ops"].append("athlete_channel_rescaling")

    # Live telemetry intersection shifts the readout away from pre-drift.
    if live_telemetry:
        verdict = evaluate_system_integrity(live_telemetry, {})
        post["live_integrity"] = {
            "system_state": verdict.system_state.value,
            "binary": verdict.binary,
            "breach_count": len(verdict.breaches),
        }
        mutation["mutation_ops"].append("live_telemetry_rebinding")

    costs = dict(cost_avoidance_projection or {})
    if not costs:
        costs = {
            "injury_cost_avoided_usd": 0.0,
            "availability_hours_preserved": 0.0,
            "liability_exposure_index": 1.0,
        }
    if path is GovernancePath.PATH_B_FAILURE_TO_ACT:
        costs = {
            k: round(float(v) * (0.4 if "avoided" in k or "preserved" in k else 1.6), 4)
            for k, v in costs.items()
        }
        mutation["mutation_ops"].append("cost_avoidance_collapse")
    else:
        costs = {
            k: round(float(v) * (1.25 if "avoided" in k or "preserved" in k else 0.7), 4)
            for k, v in costs.items()
        }
        mutation["mutation_ops"].append("cost_avoidance_realization")
    post["cost_avoidance_projection"] = costs
    post["reality_epoch"] = "forked"
    post["pre_drift_intersection_cleared"] = True

    divergence_score = _compute_divergence(pre_drift, post)
    return {
        "post_drift_readout": dict(post),
        "trajectory_mutation": mutation,
        "divergence_score": divergence_score,
    }


def _compute_divergence(pre: Mapping[str, Any], post: Mapping[str, Any]) -> float:
    """Scalar divergence between pre-drift and post-drift readouts."""
    pre_s = _canonical_json(pre)
    post_s = _canonical_json(post)
    if pre_s == post_s:
        return 0.0
    # Hash-distance proxy: normalized nibble Hamming distance of SHA-256 digests.
    a = bytes.fromhex(_sha256_hex(pre_s))
    b = bytes.fromhex(_sha256_hex(post_s))
    bits = sum(bin(x ^ y).count("1") for x, y in zip(a, b))
    return round(bits / (len(a) * 8), 6)


__all__ = [
    "AUDIT_FILE_EXTENSION",
    "AUDIT_LOG_DIR",
    "DEFAULT_GOVERNANCE_WINDOW_MS",
    "DivergenceUIStatus",
    "DriftStatus",
    "GovernancePath",
    "HolisticAuditSegment",
    "MomentOfDriftRecord",
    "RealityDivergenceLedger",
    "RealityFork",
    "SECURE_AUDIT_VAULT_DIR",
    "SYSTEM_PROTECTION_SHIELD_MSG",
    "SovereignReportDossier",
    "TimelineDivergenceResult",
    "apply_path_selection_to_lab",
    "bind_breaker_to_ledger",
    "build_session_data_from_lab",
    "build_system_context_from_kinetic",
    "compile_sovereign_report_dossier",
    "execute_silent_background_export",
    "export_sovereign_report_sync",
    "format_sovereign_intelligence_report",
    "generate_sovereign_intelligence_segment",
    "handle_timeline_divergence",
    "resolve_audit_log_dir",
    "write_to_isolated_disk",
]
