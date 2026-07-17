#!/usr/bin/env python3
"""simulate_drift.py — Synthetic end-to-end Path B + Sovereign Capital harness.

Operational log format:
  1. Initialize synthetic target (nominal envelope)
  2. Inject critical vector anomaly → hard breaker OVERRIDE
  3. Governance timeout → Path B mutation + capital ledger status
  4. Black-box forensic PDF/TXT seal into secure_audit_vault/

Usage
-----
    python3 simulate_drift.py
"""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Keep harness stdout clean — silence substrate loggers; harness prints its own trail.
logging.disable(logging.CRITICAL)
for _name in ("breaker", "ledger", "report_generator"):
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
from capital_market import compute_path_b_capital_status
from ledger import (
    GovernancePath,
    RealityDivergenceLedger,
    SECURE_AUDIT_VAULT_DIR,
    SYSTEM_PROTECTION_SHIELD_MSG,
    bind_breaker_to_ledger,
    generate_sovereign_intelligence_segment,
    handle_timeline_divergence,
)


# ---------------------------------------------------------------------------
# Terminal presentation
# ---------------------------------------------------------------------------


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")


def ops(msg: str) -> None:
    print(f"[{_ts()}] {msg}")


def capital_status_block(status: dict[str, Any], pdf_rel: str, master_hash: str) -> None:
    wm = status["wacc_matrix"]
    print()
    print("=" * 80)
    print("                    SOVEREIGN CAPITAL LEDGER STATUS UPDATE                     ")
    print("=" * 80)
    print(
        f"[+] Realized Cost Avoidance:  ${status['realized_cost_avoidance_usd']:,.2f} "
        f"(Path A Bypassed)"
    )
    print(
        f"[-] Unmanaged Risk Bleed:     ${status['unmanaged_risk_bleed_usd']:,.2f} "
        f"[UPDATING TRACER POOL]"
    )
    print(
        f"[*] Dynamic Capital Reserve Ratio (CR): Recalculated to "
        f"{status['capital_reserve_ratio_pct']:.1f}% "
        f"(Base + {status['variance_pct']:.1f}% Variance)"
    )
    print(
        f"[*] WACC Optimization Matrix:  "
        f"Wa={wm['Wa']:.2f} (Consortium) | "
        f"Wc={wm['Wc']:.2f} (Notes) | "
        f"We={wm['We']:.2f} (Equity)"
    )
    print(
        f"[*] Systemic Stability Index: {status['systemic_stability_index']:.3f} "
        f"-> {status['regime']}"
    )
    print()
    print(
        "[+] SYSTEM PROTECTION SHIELD ACTIVE: Writing forensic PDF data "
        "to isolated disk..."
    )
    print(f"[+] SUCCESS: {pdf_rel} generated successfully.")
    print(f"[+] MASTER SEGMENT HASH: SHA256:{master_hash}")
    print("=" * 80)
    print()


# ---------------------------------------------------------------------------
# Synthetic target
# ---------------------------------------------------------------------------


@dataclass
class HighRiskAthleteProfile:
    """Mock high-risk athlete / industrial kinetic asset."""

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
    """Sudden anomaly time series that breaches safety baselines."""
    series: list[TelemetrySample] = []
    start_force = target.force_n
    start_asym = target.asymmetry_pct
    start_debt = target.tissue_debt

    for i in range(1, steps + 1):
        t = i / steps
        force = start_force + (peak_force_n - start_force) * t
        asym = start_asym + (peak_asymmetry_pct - start_asym) * t
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
    # Quiet the ledger's own shield print; harness emits the capital status block.
    import builtins

    _orig_print = print

    def _filtered_print(*args: Any, **kwargs: Any) -> None:
        text = " ".join(str(a) for a in args)
        if text.startswith("SYSTEM PROTECTION SHIELD ACTIVE"):
            return
        if text.startswith("  → vault=") or text.startswith("  → pdf="):
            return
        _orig_print(*args, **kwargs)

    edge_dispatch_log: list[EdgeAlertPayload] = []

    def edge_sink(payload: EdgeAlertPayload) -> None:
        edge_dispatch_log.append(payload)

    # ------------------------------------------------------------------
    # Operational prologue
    # ------------------------------------------------------------------
    ops("INITIALIZING SYNTHETIC TARGET... NOMINAL ENVELOPE SECURED.")

    target = HighRiskAthleteProfile()
    target.record()
    thresholds = SafetyThresholds()
    breaker = HardCircuitBreaker(thresholds, edge_endpoints=[edge_sink])
    ledger = RealityDivergenceLedger(
        governance_window_ms=50,
        breaker=breaker,
    )
    bind_breaker_to_ledger(
        breaker,
        ledger,
        snapshot_provider=lambda: target.snapshot(),
    )

    baseline_verdict = evaluate_system_integrity(
        target.to_sample(),
        thresholds,
        breaker=breaker,
    )
    assert baseline_verdict.binary == 1
    assert baseline_verdict.system_state is SystemState.ACTIVE

    pre_drift_metrics = {
        "force_n": target.force_n,
        "asymmetry_pct": target.asymmetry_pct,
        "tissue_debt": target.tissue_debt,
    }

    # ------------------------------------------------------------------
    # Inject critical vector anomaly
    # ------------------------------------------------------------------
    series = build_acute_drift_series(target)
    compromised = series[-1]
    ops(
        f"CRITICAL VECTOR ANOMALY INJECTED: FORCE={compromised.kinetic_shear:g}N, "
        f"ASYMMETRY={compromised.deceleration_asymmetry:g}%"
    )

    prior_binary = breaker.binary
    verdict = evaluate_system_integrity(series, thresholds, breaker=breaker)
    assert verdict.system_state is SystemState.OVERRIDE
    assert verdict.binary == 0
    assert edge_dispatch_log
    ops(
        f"BREAKER OVERRIDE ACTIVE: System State {prior_binary} -> State {verdict.binary}."
    )

    # ------------------------------------------------------------------
    # Governance window → Path B
    # ------------------------------------------------------------------
    drift = ledger.active_drift
    assert drift is not None
    assert drift.human_responsibility_engaged is True
    ops("TIMELINE DRIFT RECORD CAPTURED. GOVERNANCE WINDOW OPENED...")

    time.sleep(0.08)
    path_b = ledger.tick_governance_window()
    assert path_b is not None
    assert path_b.path is GovernancePath.PATH_B_FAILURE_TO_ACT
    ops("NO HUMAN INTERVENTION DETECTED. EXECUTING PATH B MUTATION.")

    path_a_avoidance = 185_000.0
    availability_hours = 62.0
    fork = ledger.compute_new_reality(
        live_telemetry=[compromised],
        cost_avoidance_projection={
            "injury_cost_avoided_usd": path_a_avoidance,
            "availability_hours_preserved": availability_hours,
            "liability_exposure_index": 0.85,
        },
    )
    assert fork.divergence_score > 0
    assert fork.post_drift_readout != fork.pre_drift_readout
    assert breaker.system_state is SystemState.OVERRIDE

    # Path B capital ledger status (Wa/Wc/We matrix)
    capital_status = compute_path_b_capital_status(
        path_a_cost_avoidance_usd=path_a_avoidance,
        availability_hours_preserved=availability_hours,
        consortium_weight=0.30,
        convertible_notes_weight=0.45,
        direct_equity_weight=0.25,
        base_reserve_ratio=0.10,
    )
    assert capital_status["realized_cost_avoidance_usd"] == 0.0
    assert capital_status["unmanaged_risk_bleed_usd"] == 62_000.0
    assert abs(capital_status["capital_reserve_ratio_pct"] - 14.8) < 1e-6

    session_data = {
        "user_input": {
            "conversation": (
                "Automated Path B harness — zero operator intervention. "
                "Warning window allowed to expire without authenticated input."
            ),
            "operator_id": None,
            "intervention_supplied": False,
            "scenario": "simulate_drift.PathB",
        },
        "system_context": {
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
            "capital_ledger": capital_status,
        },
        "avatar_output": {
            "verbal_declaration": (
                "HARD CIRCUIT BREAKER TRIP — system integrity compromised. "
                "Human governance window engaged."
            ),
            "directive": "Path B (Failure to Act) — engine reactivated under hazard.",
            "edge_alert": edge_dispatch_log[-1].to_dict() if edge_dispatch_log else {},
        },
        "systemic_interpretation": {
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
            "path": "PATH_B",
            "capital_status": capital_status,
        },
    }

    builtins.print = _filtered_print  # type: ignore[assignment]
    try:
        divergence = handle_timeline_divergence(
            session_data, "PATH_B", ledger=ledger
        )
        # Wait for txt+pdf hard-commit (PDF compile can exceed 350ms).
        deadline = time.time() + 3.0
        pdf_path = None
        vault_path = None
        while time.time() < deadline:
            vault_files = sorted(
                SECURE_AUDIT_VAULT_DIR.glob("AUDIT_*.txt"),
                key=lambda p: p.stat().st_mtime,
            )
            if vault_files:
                vault_path = vault_files[-1]
                candidate = vault_path.with_suffix(".pdf")
                if candidate.exists() and candidate.stat().st_size > 0:
                    pdf_path = candidate
                    break
            time.sleep(0.05)
    finally:
        builtins.print = _orig_print  # type: ignore[assignment]

    assert divergence.background_export_started
    assert vault_path is not None, "Expected immutable AUDIT_*.txt in secure_audit_vault/"
    vault_hash = vault_path.stem.removeprefix("AUDIT_")
    if pdf_path is None:
        # Foreground fallback — never leave Path B without a sealed PDF.
        from report_generator import compile_pdf

        pdf_bytes = compile_pdf(session_data, segment=None)
        # Prefer sealed segment hash for naming when available.
        segment = generate_sovereign_intelligence_segment(session_data, ledger=ledger)
        pdf_bytes = compile_pdf(session_data, segment=segment)
        pdf_path = vault_path.with_suffix(".pdf")
        pdf_path.write_bytes(pdf_bytes)
        vault_hash = segment.block_hash
    else:
        segment = generate_sovereign_intelligence_segment(session_data, ledger=ledger)

    assert pdf_path.exists(), f"Expected companion PDF {pdf_path}"
    assert pdf_path.read_bytes()[:4] == b"%PDF"
    assert segment.verify() is True
    # Hash in filename may be from background segment; prefer live seal for MASTER line.
    master_hash = segment.block_hash

    pdf_rel = f"secure_audit_vault/{pdf_path.name}"
    short_name = f"secure_audit_vault/AUDIT_{master_hash[:10]}...pdf"
    capital_status_block(capital_status, short_name, master_hash)

    ops(f"PATH B COMPLETE · divergence={fork.divergence_score} · vault={pdf_rel}")
    ops(SYSTEM_PROTECTION_SHIELD_MSG)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"\nASSERTION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except Exception as exc:  # noqa: BLE001
        print(f"\nHARNESS ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
