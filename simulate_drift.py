#!/usr/bin/env python3
"""simulate_drift.py — Synthetic end-to-end harness for breaker + ledger.

Exercises the Hard Circuit Breaker and Reality Divergence Ledger through a
full Path B (Failure to Act) timeline:

  1. Initialize a high-risk athlete mock inside safe lab boundaries
  2. Inject acute drift (475 N / 16% asymmetry) → OVERRIDE trip
  3. Expire the Human Governance Window → Path B reality fork
  4. Export a SHA-256 Sovereign Intelligence Segment receipt

Usage
-----
    python3 simulate_drift.py
"""

from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Any

# Keep harness stdout clean — silence substrate loggers; harness prints its own trail.
logging.disable(logging.CRITICAL)
for _name in ("breaker", "ledger"):
    logging.getLogger(_name).disabled = True
    logging.getLogger(_name).propagate = False

from breaker import (
    EdgeAlertPayload,
    HardCircuitBreaker,
    SafetyThresholds,
    SystemState,
    TelemetrySample,
    evaluate_system_integrity,
)
from ledger import (
    GovernancePath,
    RealityDivergenceLedger,
    bind_breaker_to_ledger,
    generate_sovereign_intelligence_segment,
)


# ---------------------------------------------------------------------------
# Terminal presentation helpers
# ---------------------------------------------------------------------------

DIVIDER = "─" * 72


def banner(title: str) -> None:
    print()
    print(DIVIDER)
    print(f"  {title}")
    print(DIVIDER)


def log(msg: str) -> None:
    print(f"  · {msg}")


def dump_json(label: str, payload: Any) -> None:
    print(f"\n  [{label}]")
    print(
        json.dumps(payload, indent=2, sort_keys=True, default=str)
    )


# ---------------------------------------------------------------------------
# 1. Synthetic target model
# ---------------------------------------------------------------------------


@dataclass
class HighRiskAthleteProfile:
    """Mock high-risk athlete / industrial kinetic asset.

    Baseline metrics sit safely inside Kinetic Lab boundaries
    (shear < 430 N, asymmetry < 12%, tissue debt < 14).
    """

    athlete_id: str = "HR-ATHLETE-07"
    name: str = "J. Williams"
    role: str = "cutting specialist"
    force_n: float = 350.0
    asymmetry_pct: float = 5.0
    tissue_debt: float = 4.5
    tick: int = 0
    history: list[dict[str, float]] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "athlete_id": self.athlete_id,
            "name": self.name,
            "role": self.role,
            "force_n": self.force_n,
            "asymmetry_pct": self.asymmetry_pct,
            "tissue_debt": self.tissue_debt,
            "tick": self.tick,
            "athletes": [
                {
                    "name": self.name,
                    "shear_peak_n": self.force_n,
                    "asymmetry_pct": self.asymmetry_pct,
                    "tissue_debt": self.tissue_debt,
                    "state": "loading",
                }
            ],
        }

    def to_sample(self) -> TelemetrySample:
        return TelemetrySample(
            kinetic_shear=self.force_n,
            deceleration_asymmetry=self.asymmetry_pct,
            structural_degradation_rate=self.tissue_debt,
            source_id=self.athlete_id,
            tick=self.tick,
        )

    def record(self) -> None:
        self.history.append(
            {
                "tick": float(self.tick),
                "force_n": self.force_n,
                "asymmetry_pct": self.asymmetry_pct,
                "tissue_debt": self.tissue_debt,
            }
        )


def build_acute_drift_series(
    target: HighRiskAthleteProfile,
    *,
    peak_force_n: float = 475.0,
    peak_asymmetry_pct: float = 16.0,
    steps: int = 5,
) -> list[TelemetrySample]:
    """Generate a sudden anomaly time series that breaches safety baselines.

    Linear ramp from baseline → acute spike (475 N / 16% asymmetry).
    """
    series: list[TelemetrySample] = []
    start_force = target.force_n
    start_asym = target.asymmetry_pct
    start_debt = target.tissue_debt

    for i in range(1, steps + 1):
        t = i / steps
        force = start_force + (peak_force_n - start_force) * t
        asym = start_asym + (peak_asymmetry_pct - start_asym) * t
        # Tissue debt rises with the acute event but stays secondary.
        debt = start_debt + (9.0 - start_debt) * t
        target.tick += 1
        target.force_n = round(force, 2)
        target.asymmetry_pct = round(asym, 2)
        target.tissue_debt = round(debt, 2)
        target.record()
        series.append(target.to_sample())

    return series


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


def main() -> int:
    print()
    print("=" * 72)
    print("  SIMULATE_DRIFT — Synthetic Path B Verification Harness")
    print("  Modules under test: breaker.py · ledger.py")
    print("=" * 72)

    edge_dispatch_log: list[EdgeAlertPayload] = []

    def edge_sink(payload: EdgeAlertPayload) -> None:
        edge_dispatch_log.append(payload)
        log(
            f"EDGE DISPATCH → state={payload.system_state} "
            f"binary={payload.binary} breaches={payload.breach_count} "
            f"vars={list(payload.breached_variables)}"
        )

    # ------------------------------------------------------------------
    # STEP 1 — Initialize synthetic run
    # ------------------------------------------------------------------
    banner("STEP 1 · INITIALIZE SYNTHETIC RUN")

    target = HighRiskAthleteProfile()
    target.record()
    thresholds = SafetyThresholds()
    breaker = HardCircuitBreaker(thresholds, edge_endpoints=[edge_sink])
    ledger = RealityDivergenceLedger(
        governance_window_ms=50,  # short window for automated Path B
        breaker=breaker,
    )
    bind_breaker_to_ledger(
        breaker,
        ledger,
        snapshot_provider=lambda: target.snapshot(),
    )

    log(f"Target: {target.name} ({target.athlete_id}) — {target.role}")
    log(
        f"Baseline: force={target.force_n} N · "
        f"asymmetry={target.asymmetry_pct}% · "
        f"tissue_debt={target.tissue_debt}"
    )
    log(
        f"Safety ceilings: shear≤{thresholds.kinetic_shear} N · "
        f"asym≤{thresholds.deceleration_asymmetry}% · "
        f"debt≤{thresholds.structural_degradation_rate}"
    )
    log(f"Breaker binary state: {breaker.binary} ({breaker.system_state.value})")

    baseline_verdict = evaluate_system_integrity(
        target.to_sample(),
        thresholds,
        breaker=breaker,
    )
    assert baseline_verdict.binary == 1
    assert baseline_verdict.system_state is SystemState.ACTIVE
    log("Baseline integrity check: PASS — System_State=ACTIVE (1)")

    pre_drift_metrics = {
        "force_n": target.force_n,
        "asymmetry_pct": target.asymmetry_pct,
        "tissue_debt": target.tissue_debt,
    }

    # ------------------------------------------------------------------
    # STEP 2 — Inject instant drift
    # ------------------------------------------------------------------
    banner("STEP 2 · INJECT INSTANT DRIFT")

    series = build_acute_drift_series(target)
    log(f"Injected anomaly series ({len(series)} samples):")
    for sample in series:
        log(
            f"  tick={sample.tick:02d}  force={sample.kinetic_shear:6.2f} N  "
            f"asym={sample.deceleration_asymmetry:5.2f}%  "
            f"debt={sample.structural_degradation_rate:5.2f}"
        )

    compromised = series[-1]
    log(
        f"Peak breach packet → force={compromised.kinetic_shear} N "
        f"(>{thresholds.kinetic_shear}) · "
        f"asym={compromised.deceleration_asymmetry}% "
        f"(>{thresholds.deceleration_asymmetry})"
    )
    log("Passing compromised stream into evaluate_system_integrity()…")

    prior_binary = breaker.binary
    verdict = evaluate_system_integrity(
        series,  # full compromised stream
        thresholds,
        breaker=breaker,
    )

    log(f"System_State transition: {prior_binary} → {verdict.binary}")
    log(f"System_State label:      {verdict.system_state.value}")
    log(f"Breaches detected:       {len(verdict.breaches)}")
    for breach in verdict.breaches:
        log(
            f"  ! {breach.variable}: observed={breach.observed} "
            f"threshold={breach.threshold} source={breach.source_id}"
        )

    assert verdict.system_state is SystemState.OVERRIDE
    assert verdict.binary == 0
    assert breaker.system_state is SystemState.OVERRIDE
    assert edge_dispatch_log, "Expected edge command dispatch on OVERRIDE"

    log("CONFIRMED: System_State dropped 1 → 0 (OVERRIDE) — absolute step-function")
    log(f"CONFIRMED: edge command dispatched ({len(edge_dispatch_log)} payload(s))")
    dump_json("edge_alert_payload", edge_dispatch_log[-1].to_dict())

    # ------------------------------------------------------------------
    # STEP 3 — Fork the timeline (Path B)
    # ------------------------------------------------------------------
    banner("STEP 3 · FORK THE TIMELINE (PATH B EXERCISE)")

    drift = ledger.active_drift
    assert drift is not None, "Moment of Drift should be recorded on trip"
    log(f"Moment of Drift Record id:     {drift.record_id}")
    log(f"Trip timestamp (ms):           {drift.trip_timestamp_ms}")
    log(f"Human responsibility engaged:  {drift.human_responsibility_engaged}")
    log(f"Governance window (ms):        {drift.governance_window_ms}")
    log(f"Window deadline (ms):          {drift.window_deadline_ms}")
    assert drift.human_responsibility_engaged is True

    log("Simulating human governance timeout (zero operator input)…")
    time.sleep(0.08)  # exceed governance_window_ms=50
    path_b = ledger.tick_governance_window()
    assert path_b is not None
    assert path_b.path is GovernancePath.PATH_B_FAILURE_TO_ACT
    log(f"Governance outcome:            {path_b.path.value}")
    log(f"Drift status:                  {path_b.status.value}")
    log(f"Notes:                         {path_b.notes}")

    log("Reactivating system container under unmanaged / hazardous state…")
    log("Invoking ledger.compute_new_reality()…")
    fork = ledger.compute_new_reality(
        live_telemetry=[compromised],
        cost_avoidance_projection={
            "injury_cost_avoided_usd": 185_000.0,
            "availability_hours_preserved": 62.0,
            "liability_exposure_index": 0.85,
        },
    )

    log(f"Reality fork id:               {fork.fork_id}")
    log(f"Parent drift id:               {fork.parent_drift_id}")
    log(f"Divergence score:              {fork.divergence_score}")
    log(f"Engine reactivated under hazard: "
        f"{fork.post_drift_readout.get('engine_reactivated_under_hazard')}")
    assert fork.divergence_score > 0
    assert fork.post_drift_readout != fork.pre_drift_readout
    assert breaker.system_state is SystemState.OVERRIDE

    dump_json("pre_drift_metrics", pre_drift_metrics)
    dump_json(
        "mutated_post_drift_readout",
        {
            "athletes": fork.post_drift_readout.get("athletes"),
            "cost_avoidance_projection": fork.post_drift_readout.get(
                "cost_avoidance_projection"
            ),
            "system_state": fork.post_drift_readout.get("system_state"),
            "reality_epoch": fork.post_drift_readout.get("reality_epoch"),
            "trajectory_mutation": fork.trajectory_mutation,
            "divergence_score": fork.divergence_score,
        },
    )
    log("CONFIRMED: post-drift readout differs from pre-drift intersection")

    # ------------------------------------------------------------------
    # STEP 4 — Export sovereign ledger receipt
    # ------------------------------------------------------------------
    banner("STEP 4 · EXPORT THE SOVEREIGN LEDGER RECEIPT")

    segment = generate_sovereign_intelligence_segment(
        user_input={
            "conversation": (
                "Automated Path B harness — zero operator intervention. "
                "Warning window allowed to expire without authenticated input."
            ),
            "operator_id": None,
            "intervention_supplied": False,
            "scenario": "simulate_drift.PathB",
        },
        system_context={
            "digital_twin": target.snapshot(),
            "breaker": {
                "system_state": breaker.system_state.value,
                "binary": breaker.binary,
                "trip_count": breaker.trip_count,
            },
            "drift_record_id": drift.record_id,
            "trip_timestamp_ms": drift.trip_timestamp_ms,
            "fork_id": fork.fork_id,
            "governance_path": path_b.path.value,
        },
        avatar_output={
            "verbal_declaration": (
                "HARD CIRCUIT BREAKER TRIP — system integrity compromised. "
                "Human governance window engaged."
            ),
            "directive": "Path B (Failure to Act) — engine reactivated under hazard.",
            "edge_alert": edge_dispatch_log[-1].to_dict() if edge_dispatch_log else {},
        },
        systemic_interpretation={
            "breach_math": [
                {
                    "variable": b.variable,
                    "observed": b.observed,
                    "threshold": b.threshold,
                    "overshoot": round(b.observed - b.threshold, 4),
                }
                for b in verdict.breaches
            ],
            "cost_avoidance_projection": fork.post_drift_readout.get(
                "cost_avoidance_projection"
            ),
            "divergence_score": fork.divergence_score,
            "pre_drift_metrics": pre_drift_metrics,
            "peak_telemetry": {
                "force_n": compromised.kinetic_shear,
                "asymmetry_pct": compromised.deceleration_asymmetry,
                "tissue_debt": compromised.structural_degradation_rate,
            },
        },
        ledger=ledger,
    )

    log(f"Segment id:     {segment.segment_id}")
    log(f"Created at ms:  {segment.created_at_ms}")
    log(f"Verify():       {segment.verify()}")
    assert segment.verify() is True
    assert len(segment.block_hash) == 64

    print()
    print("  ╔══════════════════════════════════════════════════════════════════╗")
    print("  ║  SOVEREIGN AUDIT TRAIL — SHA-256 BLOCK HASH (SEALED)            ║")
    print("  ╚══════════════════════════════════════════════════════════════════╝")
    print()
    print(f"  {segment.block_hash}")
    print()
    log("CONFIRMED: Holistic Audit Segment sealed — tamper-proof receipt exported")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    banner("HARNESS SUMMARY")
    log(f"Baseline → OVERRIDE:     {prior_binary} → {verdict.binary}")
    log(f"Edge dispatches:         {len(edge_dispatch_log)}")
    log(f"Governance path:         {path_b.path.value}")
    log(f"Reality divergence:      {fork.divergence_score}")
    log(f"Sovereign hash:          {segment.block_hash[:16]}…{segment.block_hash[-16:]}")
    log("Result:                   ALL CHECKS PASSED")
    print()
    print("=" * 72)
    print("  simulate_drift.py complete.")
    print("=" * 72)
    print()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"\n  ASSERTION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except Exception as exc:  # noqa: BLE001
        print(f"\n  HARNESS ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
