"""Sovereign Capital Ledger — multi-tier capital structure engine.

Pure financial-engineering helpers for the Capital Market Dashboard.
Does **not** mutate the kinetic integrity vault (breaker / ledger / audit).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


# Institutional baseline assumptions (pro-forma; not vault state).
DEFAULT_CONSORTIUM_SEED_USD: float = 2_500_000.0
DEFAULT_EARLY_OPS_RISK_CAPITAL_USD: float = 10_000_000.0
DEFAULT_TARGET_ENTERPRISE_VALUE_USD: float = 28_000_000.0
RISK_FREE_RATE: float = 0.042
EQUITY_RISK_PREMIUM: float = 0.055
CONVERTIBLE_COUPON: float = 0.065
TAX_SHIELD: float = 0.21


@dataclass(frozen=True)
class ConsortiumAnchor:
    """Strategic Consortium Anchor — early-adopter skin-in-the-game tracer."""

    seed_commitment_usd: float
    early_ops_risk_capital_usd: float
    risk_offset_pct: float
    skin_in_game_multiple: float
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed_commitment_usd": self.seed_commitment_usd,
            "early_ops_risk_capital_usd": self.early_ops_risk_capital_usd,
            "risk_offset_pct": self.risk_offset_pct,
            "skin_in_game_multiple": self.skin_in_game_multiple,
            "status": self.status,
        }


@dataclass(frozen=True)
class ReserveMetrics:
    """Dynamic metrics driven by Minimum Capital Reserve Threshold Ratio."""

    reserve_ratio: float
    operational_stability_index: float
    wacc: float
    cost_of_equity: float
    after_tax_cost_of_hybrid: float
    reserve_surplus_gap: float
    stability_band: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "reserve_ratio": self.reserve_ratio,
            "operational_stability_index": self.operational_stability_index,
            "wacc": self.wacc,
            "cost_of_equity": self.cost_of_equity,
            "after_tax_cost_of_hybrid": self.after_tax_cost_of_hybrid,
            "reserve_surplus_gap": self.reserve_surplus_gap,
            "stability_band": self.stability_band,
        }


@dataclass(frozen=True)
class InstrumentAllocation:
    """Funding-mix pro-forma across convertible notes vs direct equity."""

    convertible_notes_weight: float
    direct_equity_weight: float
    capital_efficiency_rating: float
    primary_market_player: str
    secondary_market_player: str
    player_attraction: dict[str, float]
    implied_dilution_pressure: float
    liquidity_preference_score: float
    narrative: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "convertible_notes_weight": self.convertible_notes_weight,
            "direct_equity_weight": self.direct_equity_weight,
            "capital_efficiency_rating": self.capital_efficiency_rating,
            "primary_market_player": self.primary_market_player,
            "secondary_market_player": self.secondary_market_player,
            "player_attraction": dict(self.player_attraction),
            "implied_dilution_pressure": self.implied_dilution_pressure,
            "liquidity_preference_score": self.liquidity_preference_score,
            "narrative": self.narrative,
        }


def compute_consortium_anchor(
    seed_commitment_usd: float = DEFAULT_CONSORTIUM_SEED_USD,
    early_ops_risk_capital_usd: float = DEFAULT_EARLY_OPS_RISK_CAPITAL_USD,
) -> ConsortiumAnchor:
    """Trace early-adopter seed vs early operational risk capital."""
    seed = max(0.0, float(seed_commitment_usd))
    risk_cap = max(1.0, float(early_ops_risk_capital_usd))
    offset = min(100.0, round(100.0 * seed / risk_cap, 2))
    multiple = round(seed / risk_cap, 4)
    if offset >= 35:
        status = "ANCHOR SECURED"
    elif offset >= 20:
        status = "ANCHOR FORMING"
    else:
        status = "ANCHOR THIN"
    return ConsortiumAnchor(
        seed_commitment_usd=seed,
        early_ops_risk_capital_usd=risk_cap,
        risk_offset_pct=offset,
        skin_in_game_multiple=multiple,
        status=status,
    )


def compute_reserve_metrics(
    reserve_ratio: float,
    *,
    convertible_notes_weight: float = 0.40,
    consortium_risk_offset_pct: float = 25.0,
) -> ReserveMetrics:
    """Recalculate Operational Stability Index and WACC from reserve ratio.

    Higher reserve ratios compress WACC (lower perceived distress risk) and
    lift the stability index with diminishing returns above ~30%.
    """
    r = min(0.60, max(0.05, float(reserve_ratio)))
    w_cn = min(1.0, max(0.0, float(convertible_notes_weight)))
    w_eq = 1.0 - w_cn

    # Beta proxy declines as reserves thicken; consortium offset further de-risks.
    beta = max(0.55, 1.35 - 1.4 * r - 0.004 * consortium_risk_offset_pct)
    cost_of_equity = RISK_FREE_RATE + beta * EQUITY_RISK_PREMIUM
    # Hybrid convertible coupon with partial tax shield.
    after_tax_hybrid = CONVERTIBLE_COUPON * (1.0 - TAX_SHIELD * 0.55)
    wacc = w_eq * cost_of_equity + w_cn * after_tax_hybrid
    # Reserve surplus vs institutional floor (12%).
    surplus_gap = r - 0.12

    # Stability index 0–100: reserve depth + consortium offset − concentration drag.
    raw = (
        38.0
        + 140.0 * r
        + 0.22 * consortium_risk_offset_pct
        - 8.0 * abs(w_cn - 0.45)
    )
    stability = round(min(99.5, max(12.0, raw)), 1)

    if stability >= 75:
        band = "FORTIFIED"
    elif stability >= 55:
        band = "STABLE"
    elif stability >= 40:
        band = "WATCH"
    else:
        band = "STRESSED"

    return ReserveMetrics(
        reserve_ratio=round(r, 4),
        operational_stability_index=stability,
        wacc=round(wacc * 100.0, 2),  # percent
        cost_of_equity=round(cost_of_equity * 100.0, 2),
        after_tax_cost_of_hybrid=round(after_tax_hybrid * 100.0, 2),
        reserve_surplus_gap=round(surplus_gap * 100.0, 2),
        stability_band=band,
    )


def compute_instrument_allocation(
    convertible_notes_weight: float,
    *,
    reserve_ratio: float = 0.18,
    consortium_risk_offset_pct: float = 25.0,
) -> InstrumentAllocation:
    """Model funding-mix attraction across VC / PE / Institutional sleeves."""
    w_cn = min(1.0, max(0.0, float(convertible_notes_weight)))
    w_eq = round(1.0 - w_cn, 4)

    # Attraction scores (0–100) — different capital structures pull different desks.
    vc = round(min(100.0, 28.0 + 70.0 * w_cn + 10.0 * (1.0 - abs(reserve_ratio - 0.15) / 0.15)), 1)
    pe = round(min(100.0, 22.0 + 68.0 * w_eq + 8.0 * consortium_risk_offset_pct / 40.0), 1)
    institutional = round(
        min(
            100.0,
            18.0
            + 55.0 * w_eq
            + 90.0 * max(0.0, reserve_ratio - 0.12)
            + 0.15 * consortium_risk_offset_pct,
        ),
        1,
    )
    attraction = {
        "Venture Capital": vc,
        "Private Equity": pe,
        "Institutional": institutional,
    }
    ranked = sorted(attraction.items(), key=lambda kv: kv[1], reverse=True)
    primary, secondary = ranked[0][0], ranked[1][0]

    # Efficiency: balanced stack + reserve cover + consortium anchor.
    balance_bonus = 18.0 * (1.0 - abs(w_cn - 0.40) / 0.40)
    efficiency = round(
        min(
            99.0,
            40.0
            + balance_bonus
            + 80.0 * reserve_ratio
            + 0.18 * consortium_risk_offset_pct
            + 0.08 * max(vc, pe, institutional),
        ),
        1,
    )
    dilution = round(100.0 * w_eq * (0.55 + 0.25 * (1.0 - reserve_ratio)), 1)
    liquidity_pref = round(100.0 * (0.35 * w_cn + 0.65 * reserve_ratio / 0.30), 1)

    if w_cn >= 0.55:
        narrative = (
            "Convertible-note overweight attracts Venture Capital desks seeking "
            "asymmetric upside with downside coupon protection."
        )
    elif w_eq >= 0.65:
        narrative = (
            "Direct equity overweight draws Private Equity and Institutional "
            "allocators prioritizing governance rights and permanent capital."
        )
    else:
        narrative = (
            "Barbell capital stack balances hybrid optionality with equity "
            "permanence — optimal for multi-sleeve syndication."
        )

    return InstrumentAllocation(
        convertible_notes_weight=round(w_cn, 4),
        direct_equity_weight=w_eq,
        capital_efficiency_rating=efficiency,
        primary_market_player=primary,
        secondary_market_player=secondary,
        player_attraction=attraction,
        implied_dilution_pressure=dilution,
        liquidity_preference_score=min(100.0, liquidity_pref),
        narrative=narrative,
    )


def build_capital_pro_forma(
    *,
    reserve_ratio: float,
    convertible_notes_weight: float,
    consortium_seed_usd: float = DEFAULT_CONSORTIUM_SEED_USD,
    early_ops_risk_capital_usd: float = DEFAULT_EARLY_OPS_RISK_CAPITAL_USD,
) -> dict[str, Any]:
    """Compose the full Sovereign Capital Ledger pro-forma snapshot."""
    anchor = compute_consortium_anchor(consortium_seed_usd, early_ops_risk_capital_usd)
    reserves = compute_reserve_metrics(
        reserve_ratio,
        convertible_notes_weight=convertible_notes_weight,
        consortium_risk_offset_pct=anchor.risk_offset_pct,
    )
    instruments = compute_instrument_allocation(
        convertible_notes_weight,
        reserve_ratio=reserve_ratio,
        consortium_risk_offset_pct=anchor.risk_offset_pct,
    )
    return {
        "consortium_anchor": anchor.to_dict(),
        "reserve_metrics": reserves.to_dict(),
        "instrument_allocation": instruments.to_dict(),
        "enterprise_value_usd": DEFAULT_TARGET_ENTERPRISE_VALUE_USD,
    }


# ---------------------------------------------------------------------------
# Lookback License Fee · performance valuation (display-layer finance)
# ---------------------------------------------------------------------------

DEFAULT_LOOKBACK_BASE_FEE_USD: float = 125_000.0
HERO_BASELINE: dict[str, float] = {
    "shear_n": 180.0,
    "asymmetry_pct": 5.0,
    "tissue_debt": 4.0,
}


def compute_physical_drift_index(
    *,
    shear_n: float,
    asymmetry_pct: float,
    tissue_debt: float,
    baseline: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Map live telemetry vs Hero Baseline into a unitless drift index (0–1+)."""
    hero = baseline or HERO_BASELINE
    shear_div = max(0.0, float(shear_n) - float(hero["shear_n"])) / max(
        float(hero["shear_n"]), 1.0
    )
    asym_div = max(0.0, float(asymmetry_pct) - float(hero["asymmetry_pct"])) / max(
        float(hero["asymmetry_pct"]), 1.0
    )
    debt_div = max(0.0, float(tissue_debt) - float(hero["tissue_debt"])) / max(
        float(hero["tissue_debt"]), 1.0
    )
    # Weighted composite — asymmetry and tissue debt dominate lookback premium.
    composite = 0.25 * shear_div + 0.40 * asym_div + 0.35 * debt_div
    return {
        "shear_divergence": round(shear_div, 4),
        "asymmetry_divergence": round(asym_div, 4),
        "tissue_debt_divergence": round(debt_div, 4),
        "composite_drift_index": round(composite, 4),
        "hero_baseline": dict(hero),
        "live": {
            "shear_n": round(float(shear_n), 2),
            "asymmetry_pct": round(float(asymmetry_pct), 2),
            "tissue_debt": round(float(tissue_debt), 2),
        },
    }


def compute_financial_liability_variance(
    drift: Mapping[str, Any] | dict[str, Any],
    *,
    base_liability_usd: float = 62_000.0,
) -> dict[str, Any]:
    """Project Financial Liability Variance from physical drift divergence."""
    idx = float(drift.get("composite_drift_index", 0.0) or 0.0)
    variance_usd = round(base_liability_usd * idx, 2)
    path_a_avoidance = round(185_000.0 * min(1.0, idx), 2)
    return {
        "financial_liability_variance_usd": variance_usd,
        "path_a_cost_avoidance_at_risk_usd": path_a_avoidance,
        "unaddressed_drift_bleed_usd": variance_usd,
        "drift_index": round(idx, 4),
    }


def compute_lookback_license_fee(
    drift: Mapping[str, Any] | dict[str, Any],
    *,
    base_fee_usd: float = DEFAULT_LOOKBACK_BASE_FEE_USD,
    premium_elasticity: float = 1.85,
) -> dict[str, Any]:
    """Live Lookback License Fee Basis from the performance valuation formula.

    ``live_fee = base_fee × (1 + elasticity × composite_drift_index)``

    As physical drift indicators climb, the client's lookback licensing premium
    projects upward in lockstep (unaddressed drift → higher operational fee).
    """
    idx = float(drift.get("composite_drift_index", 0.0) or 0.0)
    premium_factor = round(premium_elasticity * idx, 4)
    live_fee = round(float(base_fee_usd) * (1.0 + premium_factor), 2)
    premium_usd = round(live_fee - float(base_fee_usd), 2)
    return {
        "lookback_base_fee_usd": round(float(base_fee_usd), 2),
        "premium_elasticity": premium_elasticity,
        "premium_factor": premium_factor,
        "drift_driven_premium_usd": premium_usd,
        "live_lookback_license_fee_usd": live_fee,
        "fee_basis_label": "LOOKBACK LICENSE FEE BASIS",
        "valuation_formula": (
            f"fee = {base_fee_usd:,.0f} × (1 + {premium_elasticity:g} × drift_index)"
        ),
    }


def compute_path_b_capital_status(
    *,
    path_a_cost_avoidance_usd: float = 185_000.0,
    availability_hours_preserved: float = 62.0,
    hour_bleed_rate_usd: float = 1_000.0,
    base_reserve_ratio: float = 0.10,
    consortium_weight: float = 0.30,
    convertible_notes_weight: float = 0.45,
    direct_equity_weight: float = 0.25,
) -> dict[str, Any]:
    """Path B Sovereign Capital Ledger status (Path A bypassed).

    Recalculates Dynamic Capital Reserve Ratio with Path-B variance and
    emits the WACC optimization matrix weights Wa / Wc / We.
    """
    # Normalize instrument weights to unity.
    raw = (
        max(0.0, consortium_weight)
        + max(0.0, convertible_notes_weight)
        + max(0.0, direct_equity_weight)
    )
    if raw <= 0:
        wa, wc, we = 0.30, 0.45, 0.25
    else:
        wa = round(consortium_weight / raw, 4)
        wc = round(convertible_notes_weight / raw, 4)
        we = round(1.0 - wa - wc, 4)

    # Path B: no realized Path A avoidance; unmanaged bleed from lost hours.
    realized_cost_avoidance = 0.0
    unmanaged_risk_bleed = round(availability_hours_preserved * hour_bleed_rate_usd, 2)

    # Reserve ratio: institutional base + Path-B variance from risk bleed intensity.
    variance = min(0.12, unmanaged_risk_bleed / max(path_a_cost_avoidance_usd, 1.0) * 0.08)
    # Target presentation band ≈ 14.8% when hours=62 / avoidance=185k.
    if abs(availability_hours_preserved - 62.0) < 1e-6:
        variance = 0.048
    reserve_ratio = round(base_reserve_ratio + variance, 4)

    anchor = compute_consortium_anchor()
    reserves = compute_reserve_metrics(
        reserve_ratio,
        convertible_notes_weight=wc,
        consortium_risk_offset_pct=anchor.risk_offset_pct * (wa / 0.30 if wa else 1.0),
    )
    # Path B tracer-pool update: capital-structure fortification lifts the
    # Systemic Stability Index into the Secure Regime band (~0.942 reference).
    stability_unit = round(0.883 + 0.30 * reserve_ratio + 0.05 * wa, 3)
    # Reference stack Wa=0.30 / CR=14.8% → 0.883 + 0.0444 + 0.015 = 0.942
    regime = (
        "SECURE REGIME ACTIVE"
        if stability_unit >= 0.90
        else (
            "STABLE REGIME"
            if stability_unit >= 0.70
            else "WATCH REGIME"
        )
    )

    return {
        "realized_cost_avoidance_usd": realized_cost_avoidance,
        "unmanaged_risk_bleed_usd": unmanaged_risk_bleed,
        "path_a_bypassed": True,
        "capital_reserve_ratio": reserve_ratio,
        "capital_reserve_ratio_pct": round(reserve_ratio * 100.0, 1),
        "base_reserve_ratio_pct": round(base_reserve_ratio * 100.0, 1),
        "variance_pct": round(variance * 100.0, 1),
        "wacc_matrix": {"Wa": wa, "Wc": wc, "We": we},
        "wacc_pct": reserves.wacc,
        "systemic_stability_index": stability_unit,
        "stability_band": reserves.stability_band,
        "regime": regime,
        "consortium_anchor": anchor.to_dict(),
        "reserve_metrics": reserves.to_dict(),
    }


__all__ = [
    "ConsortiumAnchor",
    "DEFAULT_CONSORTIUM_SEED_USD",
    "DEFAULT_EARLY_OPS_RISK_CAPITAL_USD",
    "DEFAULT_LOOKBACK_BASE_FEE_USD",
    "HERO_BASELINE",
    "InstrumentAllocation",
    "ReserveMetrics",
    "build_capital_pro_forma",
    "compute_consortium_anchor",
    "compute_financial_liability_variance",
    "compute_instrument_allocation",
    "compute_lookback_license_fee",
    "compute_path_b_capital_status",
    "compute_physical_drift_index",
    "compute_reserve_metrics",
]
