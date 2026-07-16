"""Polymorphic vault profiles — University Operations and AAT Phoenix."""

from __future__ import annotations

from typing import Any, TypedDict


class ResearchNode(TypedDict):
    id: str
    label: str
    credit_cost: int
    short_name: str
    summary: str
    unlock_yield: str


class MetricSlot(TypedDict):
    key: str
    label: str
    unit: str
    baseline: float
    unlocked_boost: float
    node_id: str


class ThemeTokens(TypedDict):
    bg: str
    card: str
    border: str
    accent: str
    accent_soft: str
    text: str
    muted: str


THEME: ThemeTokens = {
    "bg": "#020617",  # slate-950
    "card": "#0f172a",  # slate-900
    "border": "#1e293b",  # slate-800
    "accent": "#10b981",  # emerald-500
    "accent_soft": "rgba(16, 185, 129, 0.15)",
    "text": "#f8fafc",
    "muted": "#94a3b8",
}

# Both data profiles retained; the Streamlit shell binds to one active key at a time.
VAULT_PROFILES: dict[str, dict[str, Any]] = {
    "university_operations": {
        "key": "university_operations",
        "selector_label": "University Operations Vault",
        "tenant_identity": "University Operations Vault",
        "target_domain": "UNIVERSITY INTERCOLLEGIATE ATHLETICS",
        "active_sector_code": "SEC_01_KINETIC",
        "infrastructure_label": "Intercollegiate Athletics Ops",
        "initial_credits": 450,
        "theme": {
            "bg_color": "bg-slate-950",
            "card_color": "bg-slate-900",
            "border_color": "border-slate-800",
            "accent_color": "emerald-500",
        },
        "research_nodes": [
            {
                "id": "node_1_1",
                "label": "Node 1.1: Dynamic Interface Shear Stress Mapping",
                "credit_cost": 5,
                "short_name": "Shear Stress Mapping",
                "summary": (
                    "Map plantar and contact-surface shear vectors during cut, plant, "
                    "and push-off so coaching staff can see where force leaks into the "
                    "medial/lateral chain."
                ),
                "unlock_yield": (
                    "Live shear heatmaps, peak medial shear (N), and cut-angle stress "
                    "flags for practice and game-day readiness."
                ),
            },
            {
                "id": "node_1_2",
                "label": "Node 1.2: Pelvic Tilt & Deceleration Chain Asymmetry",
                "credit_cost": 8,
                "short_name": "Decel Chain Asymmetry",
                "summary": (
                    "Quantify anterior/posterior pelvic tilt and left–right deceleration "
                    "timing so soft-tissue load is attributed to the correct kinetic chain."
                ),
                "unlock_yield": (
                    "Asymmetry index, pelvic tilt degrees, and braking-impulse imbalance "
                    "for return-to-play and weekly load boards."
                ),
            },
            {
                "id": "node_1_3",
                "label": "Node 1.3: Cellular Longevity & Micro-Tear Chronology",
                "credit_cost": 12,
                "short_name": "Micro-Tear Chronology",
                "summary": (
                    "Chronologize micro-tear accumulation against recovery windows so "
                    "staff can separate productive overload from lingering tissue debt."
                ),
                "unlock_yield": (
                    "Tissue debt score, projected clear-window (hrs), and cumulative "
                    "micro-tear chronology across the training microcycle."
                ),
            },
        ],
        "metrics": [
            {
                "key": "shear_peak",
                "label": "Peak shear",
                "unit": "N",
                "baseline": 0.0,
                "unlocked_boost": 412.0,
                "node_id": "node_1_1",
            },
            {
                "key": "decel_asym",
                "label": "Decel asymmetry",
                "unit": "%",
                "baseline": 0.0,
                "unlocked_boost": 11.4,
                "node_id": "node_1_2",
            },
            {
                "key": "micro_tear",
                "label": "Micro-tear debt",
                "unit": "idx",
                "baseline": 0.0,
                "unlocked_boost": 7.8,
                "node_id": "node_1_3",
            },
        ],
        "verdicts": {
            "node_1_1": (
                "Interface shear concentrates on the plant-foot medial edge during the "
                "final cut. Peak vector is actionable for footwear and COD coaching."
            ),
            "node_1_2": (
                "Pelvic tilt and deceleration timing diverge left–right under braking. "
                "Chain load should be attributed before progressing high-speed exposures."
            ),
            "node_1_3": (
                "Micro-tear chronology shows productive overload with a residual clear "
                "window still open inside the current microcycle."
            ),
        },
        "sentinel": {
            "node_1_1": {
                "location": "Medial plantar shear · plant foot",
                "description": (
                    "Shear spike exceeded operational band on the change-of-direction hinge. "
                    "Moderate cutting volume until surface interface re-checks clean."
                ),
                "timeline": "T+0h: flag · T+12h: shear re-map · T+36h: conditional release",
            },
            "node_1_2": {
                "location": "Pelvic–hamstring decel couple",
                "description": (
                    "Deceleration chain asymmetry breached readiness tolerance. "
                    "Redistribute braking intent before next contested session."
                ),
                "timeline": "T+0h: alert S&C · T+6h: asymmetry re-measure · T+24h: escalate if Δ>12%",
            },
            "node_1_3": {
                "location": "Soft-tissue micro-tear ledger",
                "description": (
                    "Tissue debt chronology indicates incomplete recovery stacking. "
                    "Hold high-eccentric blocks until the clear window reopens."
                ),
                "timeline": "T+0h: pause overload · T+18h: recovery screen · T+48h: full release if clear",
            },
        },
        "roster_replacements": [
            {"name": "Davis", "fit_pct": 94, "risk_pct": 12, "risk_band": "Low"},
            {"name": "Miller", "fit_pct": 78, "risk_pct": 38, "risk_band": "Medium"},
            {"name": "Henderson", "fit_pct": 62, "risk_pct": 5, "risk_band": "Low"},
        ],
    },
    "aat_phoenix": {
        "key": "aat_phoenix",
        "selector_label": "AAT Phoenix / Asset Infrastructure",
        "tenant_identity": "AAT Phoenix · Elite Movement Unit",
        "target_domain": "KINETIC BIOMECHANICS · PERFORMANCE VAULT",
        "active_sector_code": "SEC_ASSET_INFRA",
        "infrastructure_label": "Asset Infrastructure",
        "initial_credits": 100,
        "theme": {
            "bg_color": "bg-slate-950",
            "card_color": "bg-slate-900",
            "border_color": "border-slate-800",
            "accent_color": "emerald-500",
        },
        "research_nodes": [
            {
                "id": "hamstring_load",
                "label": "Hamstring Load Vector",
                "credit_cost": 12,
                "short_name": "Hamstring Load",
                "summary": (
                    "Resolve posterior-chain tension through swing and plant so eccentric "
                    "capacity and distal junction stress are visible to medical and S&C."
                ),
                "unlock_yield": (
                    "Hamstring load vector, eccentric peak timing, and distal junction "
                    "flags for high-speed exposure clearance."
                ),
            },
            {
                "id": "thermal_map",
                "label": "Thermal Tissue Gradient Map",
                "credit_cost": 15,
                "short_name": "Thermal Map",
                "summary": (
                    "Track regional thermal gradients across load-bearing tissue so "
                    "inflammation and recovery heat signatures inform asset rotation."
                ),
                "unlock_yield": (
                    "Thermal delta (°C), hotspot coordinates, and cool-down trajectory "
                    "for infrastructure readiness boards."
                ),
            },
            {
                "id": "vibration_signature",
                "label": "Structural Vibration Signature",
                "credit_cost": 18,
                "short_name": "Vibration Signature",
                "summary": (
                    "Capture vibration harmonics through contact and braking so asset "
                    "infrastructure can detect instability before macroscopic failure."
                ),
                "unlock_yield": (
                    "Dominant frequency (Hz), amplitude envelope, and instability "
                    "sentinel for downstream self-heal dispatch."
                ),
            },
        ],
        "metrics": [
            {
                "key": "hamstring_load",
                "label": "Hamstring load",
                "unit": "N·m",
                "baseline": 0.0,
                "unlocked_boost": 186.0,
                "node_id": "hamstring_load",
            },
            {
                "key": "thermal_delta",
                "label": "Thermal delta",
                "unit": "°C",
                "baseline": 0.0,
                "unlocked_boost": 2.4,
                "node_id": "thermal_map",
            },
            {
                "key": "vibration_hz",
                "label": "Vibration peak",
                "unit": "Hz",
                "baseline": 0.0,
                "unlocked_boost": 48.5,
                "node_id": "vibration_signature",
            },
        ],
        "verdicts": {
            "hamstring_load": (
                "Posterior chain tension peaks late in the swing phase; eccentric "
                "capacity is within band but residual tightness concentrates at the "
                "distal musculotendinous junction."
            ),
            "thermal_map": (
                "Thermal gradients show elevated recovery heat on the plant-leg "
                "posterior chain. Cool-down trajectory is intact but hotspot dwell "
                "exceeds quiet baseline."
            ),
            "vibration_signature": (
                "Structural vibration harmonics remain coherent through contact. "
                "Amplitude envelope rises under braking without crossing the "
                "instability sentinel."
            ),
        },
        "sentinel": {
            "hamstring_load": {
                "location": "Distal biceps femoris · plant leg",
                "description": (
                    "Eccentric tension spike detected on the final deceleration cut. "
                    "Sentinel recommends immediate load moderation before next high-speed exposure."
                ),
                "timeline": "T+0h: flag · T+24h: soft-tissue screen · T+48h: clearance or escalate",
            },
            "thermal_map": {
                "location": "Posterior chain thermal hotspot",
                "description": (
                    "Regional heat signature persists beyond expected cool-down. "
                    "Asset rotation advised until thermal delta normalizes."
                ),
                "timeline": "T+0h: hold overload · T+8h: thermal re-scan · T+24h: conditional release",
            },
            "vibration_signature": {
                "location": "Contact-phase vibration envelope",
                "description": (
                    "Instability harmonic breached infrastructure sentinel during braking. "
                    "Cascade self-heal across sports medicine, equipment, and personal vault."
                ),
                "timeline": "T+0h: lock COD drills · T+12h: vibration re-audit · T+36h: full release if clean",
            },
        },
        "roster_replacements": [
            {"name": "Davis", "fit_pct": 94, "risk_pct": 12, "risk_band": "Low"},
            {"name": "Miller", "fit_pct": 78, "risk_pct": 38, "risk_band": "Medium"},
            {"name": "Henderson", "fit_pct": 62, "risk_pct": 5, "risk_band": "Low"},
        ],
    },
}

DEFAULT_PROFILE_KEY = "university_operations"

PROFILE_ORDER = (
    "university_operations",
    "aat_phoenix",
)


def profile_keys() -> list[str]:
    return [key for key in PROFILE_ORDER if key in VAULT_PROFILES]


def get_profile(profile_key: str) -> dict[str, Any]:
    if profile_key not in VAULT_PROFILES:
        raise KeyError(f"Unknown vault profile: {profile_key}")
    return VAULT_PROFILES[profile_key]


def research_nodes(profile_key: str) -> list[ResearchNode]:
    return list(get_profile(profile_key)["research_nodes"])


def metric_slots(profile_key: str) -> list[MetricSlot]:
    return list(get_profile(profile_key)["metrics"])


def total_unlock_cost(profile_key: str) -> int:
    return sum(int(node["credit_cost"]) for node in research_nodes(profile_key))


def node_by_id(profile_key: str, node_id: str) -> ResearchNode | None:
    for node in research_nodes(profile_key):
        if node["id"] == node_id:
            return node
    return None
