"""University Operations Vault — tenant, sector, and research-node brief."""

from __future__ import annotations

from typing import Any, TypedDict


class ResearchNode(TypedDict):
    id: str
    label: str
    credit_cost: int
    short_name: str
    summary: str
    unlock_yield: str


class ThemeTokens(TypedDict):
    bg: str
    card: str
    border: str
    accent: str
    accent_soft: str
    text: str
    muted: str


# Source brief (theme keys map Tailwind utilities → concrete hex for Streamlit CSS).
TENANT_CONFIG: dict[str, Any] = {
    "target_domain": "UNIVERSITY INTERCOLLEGIATE ATHLETICS",
    "tenant_identity": "University Operations Vault",
    "active_sector_code": "SEC_01_KINETIC",
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
}

THEME: ThemeTokens = {
    "bg": "#020617",  # slate-950
    "card": "#0f172a",  # slate-900
    "border": "#1e293b",  # slate-800
    "accent": "#10b981",  # emerald-500
    "accent_soft": "rgba(16, 185, 129, 0.15)",
    "text": "#f8fafc",
    "muted": "#94a3b8",
}


def research_nodes() -> list[ResearchNode]:
    return list(TENANT_CONFIG["research_nodes"])


def node_by_id(node_id: str) -> ResearchNode | None:
    for node in research_nodes():
        if node["id"] == node_id:
            return node
    return None


def total_unlock_cost() -> int:
    return sum(int(n["credit_cost"]) for n in research_nodes())
