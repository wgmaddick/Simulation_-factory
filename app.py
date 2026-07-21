"""NZ ACC Risk Orchestration Engine — AAT Scheme Performance (localized).

New Zealand Accident Compensation Corporation operational surface with
All-of-Government grids: IRD Income Exchange, MSD Workforce Pipeline, and
Health NZ Clinical Grid. NZD ledger, MSD certified CV pivot matrices.
"""

from __future__ import annotations

import html
import re
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

# Defensive bounds — PR #24 HTML / intake sanitation standard
MAX_TOKEN_CHARS = 96
MAX_STATUS_CHARS = 64
MAX_NOTES_CHARS = 4000
MAX_MANDATE_CHARS = 280
MAX_FIELD_CHARS = 120
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_plain_text(value: Any, *, max_chars: int) -> str:
    """Strip control chars and truncate free-form text before render/store."""
    text = _CONTROL_CHARS.sub("", str(value if value is not None else "")).strip()
    return text[:max_chars]


def sanitize_html_text(value: Any, *, max_chars: int | None = None) -> str:
    """HTML-escape dynamic values injected into custom metric-box markup."""
    text = sanitize_plain_text(
        value, max_chars=max_chars if max_chars is not None else MAX_FIELD_CHARS
    )
    return html.escape(text, quote=True)


def sanitize_claim_token(value: Any) -> str:
    return sanitize_plain_text(value, max_chars=MAX_TOKEN_CHARS)


def sanitize_status_label(value: Any) -> str:
    return sanitize_plain_text(value, max_chars=MAX_STATUS_CHARS)


def sanitize_for_markdown(value: Any, *, max_chars: int = MAX_TOKEN_CHARS) -> str:
    text = sanitize_plain_text(value, max_chars=max_chars)
    for ch in ("*", "_", "`", "[", "]", "<", ">", "|"):
        text = text.replace(ch, "")
    return text


# 1. High-Contrast Sovereign Dark Theme Configuration
st.set_page_config(
    layout="wide",
    page_title="NZ ACC Risk Orchestration Engine",
    page_icon="⬡",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    .reportview-container, .main {
        background-color: #0c1017;
        color: #f8fafc;
        font-family: "IBM Plex Sans", sans-serif;
    }
    .stApp {
        background-color: #0c1017;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    /* Industry Metric Card Highlights — matched to US Risk viewport */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        height: auto;
        overflow: visible;
    }
    .metric-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #8b949e;
        letter-spacing: 0.05em;
        margin-bottom: 0.45rem;
    }
    .metric-sequence-tag {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #38bdf8;
        margin-bottom: 0.35rem;
    }
    .metric-value-silver {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1.2;
    }
    .metric-value-crimson {
        font-size: 2rem;
        font-weight: 700;
        color: #ef4444;
        line-height: 1.2;
    }
    .metric-value-green {
        font-size: 2rem;
        font-weight: 700;
        color: #10b981;
        line-height: 1.2;
    }
    .metric-value-purple {
        font-size: 2rem;
        font-weight: 700;
        color: #a855f7;
        line-height: 1.2;
    }
    .metric-subtext {
        font-size: 0.85rem;
        color: #8b949e;
        margin-top: 0.35rem;
    }
    /* Regional Drift Heat Map — iPad landscape-safe cards */
    .directive-matrix {
        background-color: #1c1112;
        border: 1px solid #dc2626;
        padding: 1.2rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    .heat-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 1.15rem 1.1rem;
        margin-bottom: 0.75rem;
        min-height: 11.5rem;
        box-sizing: border-box;
    }
    .heat-card.heat-card-active {
        border-color: #10b981;
        box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.35);
    }
    .heat-region {
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.15rem 0;
        line-height: 1.25;
    }
    .heat-scope {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.75rem;
        color: #8b949e;
        letter-spacing: 0.04em;
        margin-bottom: 0.65rem;
    }
    .heat-metric-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #8b949e;
        margin-top: 0.45rem;
    }
    .heat-metric-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
        line-height: 1.35;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
    .drift-tag {
        display: inline-block;
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        padding: 0.28rem 0.5rem;
        border-radius: 4px;
        margin-top: 0.55rem;
        line-height: 1.35;
        overflow-wrap: anywhere;
    }
    .drift-tag-accelerating {
        color: #fecaca;
        background: rgba(239, 68, 68, 0.18);
        border: 1px solid #ef4444;
    }
    .drift-tag-stable {
        color: #fef08a;
        background: rgba(234, 179, 8, 0.16);
        border: 1px solid #eab308;
    }
    .drift-tag-reversing {
        color: #bbf7d0;
        background: rgba(16, 185, 129, 0.16);
        border: 1px solid #10b981;
    }
    .heat-policy-banner {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid #10b981;
        border-radius: 6px;
        padding: 0.85rem 1rem;
        margin: 0.35rem 0 1rem 0;
        color: #ecfdf5;
        font-weight: 600;
        font-size: 0.95rem;
    }
    @media (max-width: 1100px) {
      .heat-card {
        min-height: 0;
        padding: 1rem 0.85rem;
      }
      .heat-region {
        font-size: 1.05rem;
      }
      .drift-tag {
        font-size: 0.68rem;
      }
    }
    /* Executive Large-Print Callout Focus Elements */
    .critical-impact-value {
        font-size: 3.8rem;
        font-weight: 700;
        line-height: 1.1;
        margin-top: 0.4rem;
        margin-bottom: 0.4rem;
        font-family: "IBM Plex Mono", monospace;
        color: #ef4444 !important;
    }
    .nominal-impact-value {
        font-size: 3.8rem;
        font-weight: 700;
        line-height: 1.1;
        margin-top: 0.4rem;
        margin-bottom: 0.4rem;
        font-family: "IBM Plex Mono", monospace;
        color: #10b981 !important;
    }
    th, td {
        color: #ffffff !important;
        font-size: 0.95rem !important;
    }

    /* ============================================================
       iPadOS / mobile — top-left navigation overlay fix
       ============================================================ */
    html {
      /* Enable env(safe-area-inset-*) with viewport-fit=cover */
    }
    html, body, .stApp, [data-testid="stAppViewContainer"] {
      padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
      box-sizing: border-box !important;
    }

    /* Dedicated top navigation bar (flow layout — not absolute) */
    header[data-testid="stHeader"],
    .stAppHeader,
    [data-testid="stHeader"] {
      position: relative !important;
      top: auto !important;
      left: auto !important;
      right: auto !important;
      width: 100% !important;
      height: auto !important;
      min-height: 52px !important;
      padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
      padding-bottom: 8px !important;
      padding-left: max(12px, env(safe-area-inset-left, 0px)) !important;
      padding-right: max(12px, env(safe-area-inset-right, 0px)) !important;
      margin: 0 !important;
      background: #0c1017 !important;
      border-bottom: 1px solid #30363d !important;
      z-index: 100 !important;
      display: flex !important;
      align-items: center !important;
      overflow: visible !important;
    }

    /* Pull Streamlit sidebar toggle / return into header flow */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"],
    button[kind="header"],
    [data-testid="stBaseButton-headerNoPadding"],
    [data-testid="stBaseButton-header"],
    header[data-testid="stHeader"] button,
    .stAppHeader button {
      position: relative !important;
      top: auto !important;
      left: auto !important;
      right: auto !important;
      bottom: auto !important;
      transform: none !important;
      margin-top: max(24px, calc(env(safe-area-inset-top, 0px) + 8px)) !important;
      margin-left: 4px !important;
      min-width: 44px !important;
      min-height: 44px !important;
      z-index: 101 !important;
    }

    [data-testid="stSidebarHeader"] {
      padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
      margin-top: max(24px, env(safe-area-inset-top, 0px)) !important;
    }

    section[data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"] {
      padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
    }

    /* In-flow primary nav strip — ≥40px clear of top AND left edges */
    .ipad-top-nav {
      position: relative !important;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      width: 100%;
      box-sizing: border-box;
      padding-top: max(16px, env(safe-area-inset-top, 0px));
      margin-top: max(40px, calc(env(safe-area-inset-top, 0px) + 16px));
      margin-left: max(40px, calc(env(safe-area-inset-left, 0px) + 16px));
      padding-bottom: 0.65rem;
      padding-left: 0.35rem;
      padding-right: 0.35rem;
      border-bottom: 1px solid #30363d;
      background: #0c1017;
      z-index: 50;
    }
    .ipad-top-nav .nav-mark {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      color: #10b981;
      text-transform: uppercase;
      min-height: 44px;
      min-width: 44px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 0.65rem;
      border: 1px solid #30363d;
      background: #161b22;
      margin-top: 0;
      margin-left: 0;
    }
    .ipad-top-nav .nav-hint {
      color: #8b949e;
      font-size: 0.82rem;
      font-weight: 600;
      line-height: 1.35;
    }

    .statutory-meta {
      color: #38bdf8;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.88rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      margin: -0.35rem 0 0.85rem 0;
      line-height: 1.45;
    }
    .ministerial-banner {
      background: #1b1416;
      border: 1px solid #ef4444;
      border-left: 5px solid #ef4444;
      padding: 1.15rem 1.25rem;
      margin: 0.85rem 0 1.1rem 0;
    }
    .ministerial-badge {
      display: inline-block;
      background: #ef4444;
      color: #ffffff;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      padding: 0.3rem 0.65rem;
      margin-bottom: 0.55rem;
    }
    .briefing-mode-chip {
      display: inline-block;
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid #38bdf8;
      color: #38bdf8;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      padding: 0.25rem 0.6rem;
      margin-bottom: 0.65rem;
    }
    .claim-id-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.65rem;
      background: #0c1017;
      border: 1px solid #30363d;
      padding: 0.75rem 0.95rem;
      margin: 0.35rem 0 0.85rem 0;
      font-family: "IBM Plex Mono", monospace;
    }
    .claim-id-bar .id-label {
      color: #8b949e;
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    .claim-id-bar .id-token {
      color: #ffffff;
      font-size: 1.05rem;
      font-weight: 700;
    }
    .claim-id-bar .id-native {
      color: #10b981;
      font-size: 1.05rem;
      font-weight: 700;
    }
    .claim-id-bar .resolve-chip {
      display: inline-block;
      border: 1px solid #10b981;
      color: #10b981;
      background: rgba(16, 185, 129, 0.12);
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.35rem 0.7rem;
      letter-spacing: 0.02em;
    }
    .claim-id-bar .masked-chip {
      display: inline-block;
      border: 1px solid #8b949e;
      color: #e2e8f0;
      background: #161b22;
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.35rem 0.7rem;
    }
    .claim-id-bar .locked-chip {
      display: inline-block;
      border: 1px solid #475569;
      color: #94a3b8;
      background: #1e293b;
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.35rem 0.7rem;
    }
    /* Ministerial locked resolve control — muted slate */
    div[data-testid="stButton"] > button[kind="secondary"].locked-resolve,
    .locked-resolve-wrap button {
      background-color: #1e293b !important;
      background-image: none !important;
      color: #94a3b8 !important;
      border: 1px solid #475569 !important;
      font-weight: 700 !important;
    }
    .locked-resolve-wrap button:hover {
      background-color: #334155 !important;
      color: #cbd5e1 !important;
      border-color: #64748b !important;
    }
    /* Claims Officer / Specialist — active green resolve */
    .active-resolve-wrap button[kind="primary"] {
      background-color: #10b981 !important;
      border-color: #10b981 !important;
      color: #0c1017 !important;
      font-weight: 700 !important;
    }
    .audit-toast {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.8rem;
      color: #8b949e;
      margin-top: 0.35rem;
    }

    /* Tablet / mobile: hard floor — top-left hit targets ≥40px from edges */
    @media (max-width: 1024px) {
      header[data-testid="stHeader"],
      .stAppHeader,
      [data-testid="stHeader"],
      .ipad-top-nav {
        margin-top: max(40px, calc(env(safe-area-inset-top, 0px) + 16px)) !important;
        margin-left: max(40px, calc(env(safe-area-inset-left, 0px) + 16px)) !important;
        padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
      }

      [data-testid="stSidebarCollapsedControl"],
      [data-testid="collapsedControl"],
      [data-testid="stSidebarCollapseButton"],
      [data-testid="stExpandSidebarButton"],
      header[data-testid="stHeader"] button,
      .stAppHeader button,
      [data-testid="stToolbar"] button,
      [data-testid="stSidebarHeader"] button,
      .ipad-top-nav .nav-mark {
        /* Clear iPadOS Multitasking pill (...) , status bar, Stage Manager */
        margin-top: max(40px, calc(env(safe-area-inset-top, 0px) + 16px)) !important;
        margin-left: max(40px, calc(env(safe-area-inset-left, 0px) + 16px)) !important;
        position: relative !important;
        top: auto !important;
        left: auto !important;
      }

      div[data-testid="stMainBlockContainer"],
      .block-container {
        padding-top: max(1.5rem, calc(env(safe-area-inset-top, 0px) + 1rem)) !important;
        padding-left: max(1rem, calc(env(safe-area-inset-left, 0px) + 0.5rem)) !important;
      }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Dedicated top navigation bar — in-document flow (not absolute overlay)
st.markdown(
    """
    <div class="ipad-top-nav" role="navigation" aria-label="Primary scheme navigation">
      <span class="nav-mark" aria-hidden="true">☰ NAV</span>
      <span class="nav-hint">NZ ACC · Scheme navigation — clear of iPadOS status bar &amp; Multitasking controls</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# viewport-fit=cover so env(safe-area-inset-*) resolves on iPadOS Safari
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    """,
    unsafe_allow_html=True,
)

# --- MASTER CLAIMS DATABASE CORE ---
MINISTER_ROLE = "Minister for ACC / Crown Governance"
SCHEME_DIRECTOR = "Scheme Director (GM)"
CLAIMS_OFFICER = "Claims Officer / Analyst"
REVIEWING_SPECIALIST = "Reviewing Specialist"
CLINICAL_TRIAGE_ROLE = "Clinical & Health Triage Specialist"
VOCATIONAL_MSD_ROLE = "Vocational & MSD Placement Specialist"

STATUTORY_NOMINAL = "Nominal"
STATUTORY_MINISTERIAL = "Ministerial Escalation Required"
STATUTORY_CABINET = "Cabinet Threshold Exceeded"

# Anonymized AAT tokens → Native ACC claim identifiers (tiered unlock)
NATIVE_ACC_CLAIM_REGISTRY: dict[str, str] = {
    "AAT-Claimant-Delta-2026": "ACC-NZ-2026-481739",
    "AAT-Claimant-Epsilon-2026": "ACC-NZ-2026-552018",
    "AAT-Claimant-Zeta-2026": "ACC-NZ-2026-619447",
    "AAT-Claimant-Eta-2026": "ACC-NZ-2026-703882",
    "AAT-Claimant-Theta-2026": "ACC-NZ-2026-774105",
    "AAT-Claimant-Iota-2026": "ACC-NZ-2026-801336",
    "AAT-Claimant-Kappa-2026": "ACC-NZ-2026-862559",
}


def resolve_native_acc_claim_id(aat_token: str) -> str:
    """Map anonymized AAT scheme token to Native ACC Claim ID."""
    return NATIVE_ACC_CLAIM_REGISTRY.get(
        str(aat_token),
        f"ACC-NZ-PENDING-{abs(hash(str(aat_token))) % 10_000_000:07d}",
    )


# Regional heat-map baseline (closed-loop with ministerial_override)
_REGIONAL_DRIFT_BASE: list[dict[str, Any]] = [
    {
        "name": "Northern",
        "scope": "Auckland / Northland",
        "bottleneck": "Elective Orthopaedics Waitlist",
        "liability_nzd": 48_200_000,
        "hot": True,
    },
    {
        "name": "Midland",
        "scope": "Waikato / Bay of Plenty",
        "bottleneck": "MSD Light-Duty Placement Lag",
        "liability_nzd": 31_400_000,
        "hot": False,
    },
    {
        "name": "Central",
        "scope": "Capital / Coast",
        "bottleneck": "IME Authorization Backlog",
        "liability_nzd": 27_850_000,
        "hot": False,
    },
    {
        "name": "Southern",
        "scope": "Canterbury / Otago",
        "bottleneck": "Long-Tail Indemnity Compounding",
        "liability_nzd": 39_600_000,
        "hot": True,
    },
]


def build_regional_drift_cards(ministerial_override: bool) -> list[dict[str, str]]:
    """Derive sanitized regional heat-map card payloads from override state."""
    cards: list[dict[str, str]] = []
    for region in _REGIONAL_DRIFT_BASE:
        if ministerial_override:
            status_key = "reversing"
            status_label = "🟢 REVERSING (-14.2% Drift Rate)"
            liability = int(region["liability_nzd"] * 0.86)
            bottleneck = f"Mitigated · {region['bottleneck']}"
        elif region["hot"]:
            status_key = "accelerating"
            status_label = "🔴 ACCELERATING (+12.4% Drift Rate)"
            liability = int(region["liability_nzd"])
            bottleneck = str(region["bottleneck"])
        else:
            status_key = "stable"
            status_label = "🟡 STABLE (+0.8% Drift Rate)"
            liability = int(region["liability_nzd"])
            bottleneck = str(region["bottleneck"])

        cards.append(
            {
                "name": sanitize_html_text(region["name"], max_chars=48),
                "scope": sanitize_html_text(region["scope"], max_chars=64),
                "bottleneck": sanitize_html_text(bottleneck, max_chars=96),
                "liability": sanitize_html_text(
                    f"${liability:,.0f} NZD", max_chars=48
                ),
                "status_key": status_key,
                "status_label": sanitize_html_text(status_label, max_chars=96),
            }
        )
    return cards


def render_regional_heat_card(card: dict[str, str], *, policy_active: bool) -> str:
    """Return HTML for one regional heat card (values pre-sanitized)."""
    active_class = " heat-card-active" if policy_active else ""
    tag_class = {
        "accelerating": "drift-tag-accelerating",
        "stable": "drift-tag-stable",
        "reversing": "drift-tag-reversing",
    }.get(card["status_key"], "drift-tag-stable")
    return (
        f'<div class="heat-card{active_class}">'
        f'<div class="heat-region">{card["name"]}</div>'
        f'<div class="heat-scope">{card["scope"]}</div>'
        f'<div class="heat-metric-label">Primary Bottleneck</div>'
        f'<div class="heat-metric-value">{card["bottleneck"]}</div>'
        f'<div class="heat-metric-label">Total Regional Liability Exposure</div>'
        f'<div class="heat-metric-value">{card["liability"]}</div>'
        f'<div class="heat-metric-label">Drift Velocity</div>'
        f'<div class="drift-tag {tag_class}">{card["status_label"]}</div>'
        f"</div>"
    )


@st.cache_data
def load_internal_portfolio_ledger():
    return pd.DataFrame(
        [
            {
                "Claim ID": "AAT-Claimant-Delta-2026",
                "Anatomy Target": "Shoulder (Glenohumeral)",
                "Age": 48,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 62.0,
                "Spend_To_Date": 28400.0,
                "Days_Elapsed": 42,
                "Drift_Velocity": 1.35,
                "Status": "CRITICAL DRIFT",
                "Statutory Risk Rating": STATUTORY_MINISTERIAL,
                "NLP_Ingest": (
                    "Claimant presents with severe shoulder disruption. Cellular age "
                    "curves indicate prolonged recovery runway. Psychosocial fear of "
                    "re-injury spike noted; workplace physical demand conflict with "
                    "overhead lifting role unresolved."
                ),
            },
            {
                "Claim ID": "AAT-Claimant-Epsilon-2026",
                "Anatomy Target": "Lumbar Spine Matrix",
                "Age": 32,
                "Demands": "Sedentary Clerical",
                "ROM_Actual": 94.0,
                "Spend_To_Date": 12100.0,
                "Days_Elapsed": 28,
                "Drift_Velocity": 0.22,
                "Status": "NOMINAL ALIGNMENT",
                "Statutory Risk Rating": STATUTORY_NOMINAL,
                "NLP_Ingest": (
                    "Favorable tissue consistency. Functional path trajectory arc "
                    "tracking nominal. Low stress metrics."
                ),
            },
            {
                "Claim ID": "AAT-Claimant-Zeta-2026",
                "Anatomy Target": "Lower Extremity (Knee)",
                "Age": 61,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 48.0,
                "Spend_To_Date": 41200.0,
                "Days_Elapsed": 67,
                "Drift_Velocity": 2.10,
                "Status": "CRITICAL DRIFT",
                "Statutory Risk Rating": STATUTORY_CABINET,
                "NLP_Ingest": (
                    "Advanced structural vulnerability noted in knee construct. High "
                    "manual occupational exposures compounding timeline variance. "
                    "Surgical waitlist delays extending incapacity window; workplace "
                    "physical demand conflict with kneeling/climbing duties."
                ),
            },
            {
                "Claim ID": "AAT-Claimant-Eta-2026",
                "Anatomy Target": "Shoulder (Glenohumeral)",
                "Age": 29,
                "Demands": "Medium Logistics / Transport",
                "ROM_Actual": 88.0,
                "Spend_To_Date": 19400.0,
                "Days_Elapsed": 35,
                "Drift_Velocity": 0.40,
                "Status": "NOMINAL ALIGNMENT",
                "Statutory Risk Rating": STATUTORY_NOMINAL,
                "NLP_Ingest": (
                    "Favorable tissue consistency. Functional path trajectory arc "
                    "tracking nominal. Low stress metrics."
                ),
            },
            {
                "Claim ID": "AAT-Claimant-Theta-2026",
                "Anatomy Target": "Lower Extremity (Knee)",
                "Age": 54,
                "Demands": "Medium Logistics / Transport",
                "ROM_Actual": 55.0,
                "Spend_To_Date": 33800.0,
                "Days_Elapsed": 51,
                "Drift_Velocity": 1.72,
                "Status": "CRITICAL DRIFT",
                "Statutory Risk Rating": STATUTORY_MINISTERIAL,
                "NLP_Ingest": (
                    "Partial-thickness meniscal involvement with delayed MRI access. "
                    "Surgical waitlist delays primary. Psychosocial spikes around "
                    "income uncertainty; light-duty matching incomplete."
                ),
            },
            {
                "Claim ID": "AAT-Claimant-Iota-2026",
                "Anatomy Target": "Shoulder (Glenohumeral)",
                "Age": 44,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 58.0,
                "Spend_To_Date": 30150.0,
                "Days_Elapsed": 49,
                "Drift_Velocity": 1.48,
                "Status": "CRITICAL DRIFT",
                "Statutory Risk Rating": STATUTORY_MINISTERIAL,
                "NLP_Ingest": (
                    "Rotator cuff strain with workplace physical demand conflict. "
                    "Psychosocial spikes and fear-avoidance; surgical waitlist "
                    "delays secondary contributor."
                ),
            },
            {
                "Claim ID": "AAT-Claimant-Kappa-2026",
                "Anatomy Target": "Lumbar Spine Matrix",
                "Age": 39,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 64.0,
                "Spend_To_Date": 26750.0,
                "Days_Elapsed": 44,
                "Drift_Velocity": 1.25,
                "Status": "CRITICAL DRIFT",
                "Statutory Risk Rating": STATUTORY_MINISTERIAL,
                "NLP_Ingest": (
                    "Lumbar load intolerance with workplace physical demand conflict. "
                    "Psychosocial spikes noted; conservative pathway preferred over "
                    "surgical waitlist."
                ),
            },
        ]
    )


NLP_ROOT_CAUSE_TAXONOMY: dict[str, tuple[str, ...]] = {
    "Surgical Waitlist Delays": (
        "surgical waitlist",
        "mri access",
        "delayed mri",
        "waitlist delay",
    ),
    "Workplace Physical Demand Conflict": (
        "workplace physical demand",
        "occupational exposure",
        "overhead lifting",
        "kneeling",
        "climbing",
        "manual occupational",
    ),
    "Psychosocial Spikes": (
        "psychosocial",
        "fear of re-injury",
        "fear-avoidance",
        "income uncertainty",
        "stress",
    ),
}


def synthesize_drift_causes(nlp_texts: list[str]) -> list[tuple[str, int, str]]:
    """Aggregate NLP ingest fields into ranked root-cause drivers."""
    scores: dict[str, int] = {k: 0 for k in NLP_ROOT_CAUSE_TAXONOMY}
    snippets: dict[str, str] = {k: "" for k in NLP_ROOT_CAUSE_TAXONOMY}
    for raw in nlp_texts:
        text = str(raw or "").lower()
        for cause, keywords in NLP_ROOT_CAUSE_TAXONOMY.items():
            hits = sum(1 for kw in keywords if kw in text)
            if hits:
                scores[cause] += hits
                if not snippets[cause]:
                    snippets[cause] = str(raw or "")[:140]
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [
        (cause, count, snippets[cause])
        for cause, count in ranked
        if count > 0
    ]


GLOBAL_VIEW = "Global Scheme Portfolio (All Active Claims)"


def set_audit_view(claim_id: str) -> None:
    """Streamlit on_click callback: open a specific claim in Audit View."""
    st.session_state["audit_view_selection"] = claim_id
    st.session_state["cohort_mode"] = False
    st.session_state["audit_status_filter"] = "ALL"
    st.session_state["audit_anatomy_filter"] = "ALL"
    st.session_state["audit_focus_token"] = True
    st.rerun()


def jump_to_audit_sector(
    status: str | None = None,
    anatomy: str | None = None,
    claim_id: str | None = None,
    cohort: bool = False,
) -> None:
    """Cross-sector jump callback: sync Audit View filters + focus.

    Intended for ``st.button(..., on_click=jump_to_audit_sector, kwargs=...)``
    so widget-keyed session state is updated before the next script run
    instantiates the Audit View selectboxes.
    """
    st.session_state["audit_focus_token"] = True
    if claim_id:
        set_audit_view(claim_id)
        return
    st.session_state["audit_view_selection"] = GLOBAL_VIEW
    st.session_state["cohort_mode"] = bool(cohort) or bool(anatomy) or bool(status)
    if status:
        st.session_state["audit_status_filter"] = status
    if anatomy:
        st.session_state["audit_anatomy_filter"] = anatomy
        st.session_state["cohort_mode"] = True
    st.rerun()


def clear_audit_filters() -> None:
    """Reset Audit View Command Sector filters (on_click-safe)."""
    st.session_state["audit_status_filter"] = "ALL"
    st.session_state["audit_anatomy_filter"] = "ALL"
    st.session_state["cohort_mode"] = False
    st.session_state["audit_view_selection"] = GLOBAL_VIEW
    st.session_state["audit_focus_token"] = True
    st.rerun()


def apply_ledger_filters(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    status = st.session_state.get("audit_status_filter", "ALL")
    anatomy = st.session_state.get("audit_anatomy_filter", "ALL")
    if status and status != "ALL":
        out = out[out["Status"] == status]
    if anatomy and anatomy != "ALL":
        out = out[out["Anatomy Target"] == anatomy]
    return out.reset_index(drop=True)


def apply_clinical_triage_action(
    claim_id: str,
    title: str,
    impact: str,
    new_drift: str,
) -> None:
    """on_click-safe clinical intervention binder."""
    st.session_state[f"action_taken_{claim_id}"] = {
        "title": sanitize_plain_text(title, max_chars=160),
        "impact": sanitize_plain_text(impact, max_chars=280),
        "new_drift": sanitize_plain_text(new_drift, max_chars=280),
    }
    st.rerun()


def render_clinical_triage_view() -> None:
    """Department #1: Clinical & Health Triage Team View.

    Strictly isolated surface for medical officers, clinical coordinators,
    and triage specialists. Hides financial payouts, wage ledgers, and legal
    disputes to ensure data compliance and zero clutter.
    """
    st.markdown("## Clinical & Health Triage Command Sector")
    st.caption(
        "Role-Gated Interface: Health & Medical Specialists | "
        "Focus: Diagnostic Triage & Recovery Alignment"
    )
    st.divider()

    # Claim profiles are clinical-only — no indemnity / wage / legal fields rendered.
    claim_options: dict[str, dict[str, Any]] = {
        "AAT-Claimant-Delta-2026": {
            "anatomy": "Shoulder (Glenohumeral / Supraspinatus Tear)",
            "duty_tier": "Heavy Industrial Laborer",
            "public_waitlist_days": 84,
            "odg_baseline_days": 45,
            "actual_days_elapsed": 112,
            "flexion_rom": "38% Functional ROM (Severe Limitation)",
            "facility": "Te Whatu Ora - Northern Surgical Hub",
            "drift_status": "HIGH DRIFT RISK (+52 Days Variance)",
        },
        "AAT-Claimant-Epsilon-2026": {
            "anatomy": "Lumbar Spine Matrix (L4/L5 Disc Bulge)",
            "duty_tier": "Clerical / Administrative",
            "public_waitlist_days": 21,
            "odg_baseline_days": 30,
            "actual_days_elapsed": 38,
            "flexion_rom": "72% Functional ROM (Moderate Stiffness)",
            "facility": "Te Whatu Ora - Midland Regional Care Network",
            "drift_status": "NOMINAL ALIGNMENT (+8 Days Variance)",
        },
        "AAT-Claimant-Zeta-2026": {
            "anatomy": "Lower Extremity (Knee Joint Narrowing / ACL Strain)",
            "duty_tier": "Heavy Logistics & Transport",
            "public_waitlist_days": 65,
            "odg_baseline_days": 60,
            "actual_days_elapsed": 98,
            "flexion_rom": "45% Functional ROM (Flexion Deficit)",
            "facility": "Te Whatu Ora - Southern Triage Unit",
            "drift_status": "HIGH DRIFT RISK (+38 Days Variance)",
        },
    }

    selected_claim_id = st.selectbox(
        "Select Active Medical File for Triage Audit:",
        list(claim_options.keys()),
        index=0,
        key="clinical_triage_claim_selector",
    )
    claim = claim_options[selected_claim_id]
    action_key = f"action_taken_{selected_claim_id}"
    if action_key not in st.session_state:
        st.session_state[action_key] = None

    safe_anatomy = sanitize_for_markdown(claim["anatomy"], max_chars=120)
    safe_duty = sanitize_for_markdown(claim["duty_tier"], max_chars=80)
    safe_rom = sanitize_for_markdown(claim["flexion_rom"], max_chars=120)
    safe_facility = sanitize_for_markdown(claim["facility"], max_chars=120)
    safe_drift = sanitize_for_markdown(claim["drift_status"], max_chars=120)
    wait_days = int(claim["public_waitlist_days"])
    odg_days = int(claim["odg_baseline_days"])
    actual_days = int(claim["actual_days_elapsed"])

    # --- 3-COLUMN CLINICAL INGESTION GRID (What / Where / When) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### WHAT: Medical Profile")
        st.info(
            f"**Anatomical Target:** {safe_anatomy}\n\n"
            f"**Occupational Duty Tier:** {safe_duty}\n\n"
            f"**Flexion / ROM Status:** {safe_rom}"
        )
    with col2:
        st.markdown("### WHERE: Care Facility")
        st.warning(
            f"**Assigned Node:** {safe_facility}\n\n"
            f"**Public Diagnostic Queue:** {wait_days} Days Active\n\n"
            f"**Primary Bottleneck:** Public Surgical / MRI Assessment Backlog"
        )
    with col3:
        st.markdown("### WHEN: Recovery Baseline")
        st.error(
            f"**Actual Days Elapsed:** {actual_days} Days\n\n"
            f"**ODG Optimal Baseline:** {odg_days} Days\n\n"
            f"**Status:** {safe_drift}"
        )

    st.divider()

    action_state = st.session_state.get(action_key)
    if action_state:
        safe_title = sanitize_for_markdown(action_state["title"], max_chars=160)
        safe_impact = sanitize_for_markdown(action_state["impact"], max_chars=280)
        safe_new_drift = sanitize_for_markdown(
            action_state["new_drift"], max_chars=280
        )
        st.success(
            f"**CLINICAL INTERVENTION ACTIVE:** {safe_title}\n\n"
            f"• **System Impact:** {safe_impact}\n\n"
            f"• **Updated Pathway Drift:** {safe_new_drift}"
        )
        st.divider()

    st.markdown("### Clinical Intervention Execution Deck")
    st.caption(
        "Select a pre-approved clinical override to halt pathway drift "
        "and accelerate functional recovery:"
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button(
            "1. Authorize Private Diagnostic Fast-Track ($2,200 NZD)",
            use_container_width=True,
            key=f"clinical_fast_track_{selected_claim_id}",
            on_click=apply_clinical_triage_action,
            args=(
                selected_claim_id,
                "Private MRI/CT Fast-Track Dispatched",
                "Bypasses public waitlist. Diagnostic completed within 72 hours.",
                "Drift reduced by 38 Days | Trajectory re-aligned to Baseline.",
            ),
        )
        st.button(
            "2. Route to Private Surgical Partner ($14,500 NZD)",
            use_container_width=True,
            key=f"clinical_surgical_{selected_claim_id}",
            on_click=apply_clinical_triage_action,
            args=(
                selected_claim_id,
                "Private Surgical Partner Allocation Approved",
                "Transfers case out of public hospital backlog to private "
                "orthopaedic center.",
                "Saves 65 Days of unmitigated weekly indemnity decay.",
            ),
        )
    with btn_col2:
        st.button(
            "3. Dispatch IME Independent Capacity Audit",
            use_container_width=True,
            key=f"clinical_ime_{selected_claim_id}",
            on_click=apply_clinical_triage_action,
            args=(
                selected_claim_id,
                "IME Peer-Review Panel Assigned",
                "Independent medical audit ordered for ROM and functional "
                "capacity re-rating.",
                "Audit scheduled within 5 business days.",
            ),
        )
        st.button(
            "4. Inject Intensive Multidisciplinary Rehab ($3,200 NZD)",
            use_container_width=True,
            key=f"clinical_rehab_{selected_claim_id}",
            on_click=apply_clinical_triage_action,
            args=(
                selected_claim_id,
                "Intensive Rehab Package Activated (EARI)",
                "Dispatches physio + occupational therapy team directly "
                "to claimant.",
                "Flattens Day 60 drift curve prior to permanent workforce "
                "detachment.",
            ),
        )


def apply_vocational_msd_action(
    claim_id: str,
    title: str,
    details: str,
) -> None:
    """on_click-safe vocational / MSD placement binder."""
    st.session_state[f"msd_action_{claim_id}"] = {
        "title": sanitize_plain_text(title, max_chars=160),
        "details": sanitize_plain_text(details, max_chars=320),
    }
    st.rerun()


def render_vocational_msd_view() -> None:
    """Department #2: Vocational & MSD Placement Team View.

    Focused strictly on functional capacity limits, job re-allocation,
    and retraining vouchers.
    """
    st.markdown("## Vocational & MSD Placement Command Sector")
    st.caption(
        "Role-Gated Interface: MSD Case Officers & Vocational Specialists | "
        "Focus: Workforce Re-Entry & Retraining"
    )
    st.divider()

    claim_msd_options: dict[str, dict[str, str]] = {
        "AAT-Claimant-Delta-2026": {
            "current_role": "Heavy Industrial Laborer",
            "modified_capacity": "Modified Light Duty (Max 5kg Overhead Lifting)",
            "msd_match_code": "MSD-AX-7710 (Safety & Logistics Coordinator)",
            "retraining_eligible": "High Priority (100% Match)",
            "weekly_indemnity_rate": "$1,420 NZD / week",
            "status": "Awaiting Vocational Re-Allocation",
        },
        "AAT-Claimant-Zeta-2026": {
            "current_role": "Heavy Logistics Driver",
            "modified_capacity": "Sedentary / Light Driving Only (Knee Flexion Cap)",
            "msd_match_code": "MSD-LOG-3302 (Fleet Dispatch Controller)",
            "retraining_eligible": "Approved",
            "weekly_indemnity_rate": "$1,280 NZD / week",
            "status": "Placement Match Identified",
        },
    }

    selected_msd_id = st.selectbox(
        "Select Active Claimant for Vocational Placement:",
        list(claim_msd_options.keys()),
        index=0,
        key="vocational_msd_claim_selector",
    )
    msd_claim = claim_msd_options[selected_msd_id]
    action_key = f"msd_action_{selected_msd_id}"
    if action_key not in st.session_state:
        st.session_state[action_key] = None

    safe_role = sanitize_for_markdown(msd_claim["current_role"], max_chars=80)
    safe_capacity = sanitize_for_markdown(
        msd_claim["modified_capacity"], max_chars=120
    )
    safe_match = sanitize_for_markdown(msd_claim["msd_match_code"], max_chars=120)
    safe_retrain = sanitize_for_markdown(
        msd_claim["retraining_eligible"], max_chars=80
    )
    safe_rate = sanitize_for_markdown(
        msd_claim["weekly_indemnity_rate"], max_chars=64
    )
    safe_status = sanitize_for_markdown(msd_claim["status"], max_chars=80)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Functional Limits")
        st.info(
            f"**Baseline Role:** {safe_role}\n\n"
            f"**Medical Restriction:** {safe_capacity}"
        )
    with col2:
        st.markdown("### MSD Job Match Grid")
        st.success(
            f"**Target Role:** {safe_match}\n\n"
            f"**Skill Status:** {safe_retrain}"
        )
    with col3:
        st.markdown("### Indemnity Burn Rate")
        st.warning(
            f"**Weekly Compensation:** {safe_rate}\n\n"
            f"**Current Status:** {safe_status}"
        )

    st.divider()

    action_state = st.session_state.get(action_key)
    if action_state:
        safe_title = sanitize_for_markdown(action_state["title"], max_chars=160)
        safe_details = sanitize_for_markdown(action_state["details"], max_chars=320)
        st.success(
            f"**VOCATIONAL ACTION EXECUTED:** {safe_title}\n\n• {safe_details}"
        )
        st.divider()

    st.markdown("### Vocational Placement Execution Deck")
    st.caption(
        "Issue placement vouchers, retraining grants, and workplace adaptations "
        "to halt indemnity burn and restore workforce capacity."
    )
    b1, b2 = st.columns(2)
    with b1:
        st.button(
            "1. Issue MSD Light-Duty Placement Voucher ($1,500 NZD)",
            use_container_width=True,
            key=f"msd_voucher_{selected_msd_id}",
            on_click=apply_vocational_msd_action,
            args=(
                selected_msd_id,
                "MSD Light-Duty Partner Voucher Issued",
                "Allocated candidate to active dispatch coordinator role. "
                "Reduces weekly indemnity burn by 100% within 14 days.",
            ),
        )
        st.button(
            "2. Authorize Retraining Certificate Grant ($3,500 NZD)",
            use_container_width=True,
            key=f"msd_retrain_{selected_msd_id}",
            on_click=apply_vocational_msd_action,
            args=(
                selected_msd_id,
                "Health & Safety Certification Enrolled",
                "Enrolled in 4-week fast-track compliance course. "
                "Re-allocates worker out of heavy labor tier.",
            ),
        )
    with b2:
        st.button(
            "3. Workplace Ergonomic Adaptation ($1,200 NZD)",
            use_container_width=True,
            key=f"msd_ergo_{selected_msd_id}",
            on_click=apply_vocational_msd_action,
            args=(
                selected_msd_id,
                "Ergonomic Modification Approved",
                "Funds workstation adjustments with existing employer to enable "
                "immediate part-time return to work.",
            ),
        )
        st.button(
            "4. Transition to Active MSD Search Pipeline",
            use_container_width=True,
            key=f"msd_pipeline_{selected_msd_id}",
            on_click=apply_vocational_msd_action,
            args=(
                selected_msd_id,
                "Active Placement Pipeline Transitioned",
                "File transferred to regional MSD employment liaison officer "
                "for direct placement matching.",
            ),
        )


def render_cohort_analysis_panel(
    cohort_df: pd.DataFrame,
    *,
    anatomy: str,
    can_unmask: bool,
    role: str,
) -> None:
    """Anatomical cohort aggregation + NLP root-cause synthesis."""
    critical_df = cohort_df[cohort_df["Status"] == "CRITICAL DRIFT"]
    n_critical = int(len(critical_df))
    focus = critical_df if n_critical else cohort_df
    avg_days = float(focus["Days_Elapsed"].mean()) if len(focus) else 0.0
    cumulative_risk = float(focus["Spend_To_Date"].sum()) if len(focus) else 0.0
    primary_velocity = float(focus["Drift_Velocity"].mean()) if len(focus) else 0.0

    st.markdown(
        f"""
        <div class="metric-box" style="border-left: 4px solid #ef4444;">
          <div class="metric-label" style="color:#ef4444;">COHORT ANALYSIS</div>
          <div style="color:#ffffff; font-size:1.25rem; font-weight:700; margin-bottom:0.55rem;">
            Cohort Analysis: {anatomy} — {n_critical} Critical Drift Subjects
          </div>
          <div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:0.75rem;">
            <div>
              <div class="metric-label">Average Days Elapsed</div>
              <div class="metric-value-silver" style="font-size:1.45rem;">{avg_days:.1f}</div>
            </div>
            <div>
              <div class="metric-label">Cumulative Financial Risk (NZD)</div>
              <div class="metric-value-crimson" style="font-size:1.45rem;">${cumulative_risk:,.0f}</div>
            </div>
            <div>
              <div class="metric-label">Primary Drift Velocity</div>
              <div class="metric-value-silver" style="font-size:1.45rem;">{primary_velocity:.2f}×</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    causes = synthesize_drift_causes(list(focus["NLP_Ingest"].astype(str)))
    st.markdown("### SYNTHESIZED DRIFT CAUSE BREAKDOWN")
    if causes:
        bullets = "".join(
            f"<li><strong>{cause}</strong> — signal weight {weight}"
            f"{f' · “{snippet}…”' if snippet else ''}</li>"
            for cause, weight, snippet in causes
        )
        st.markdown(
            f"""
            <div class="metric-box" style="border-left: 4px solid #a855f7;">
              <div class="metric-label" style="color:#c084fc;">NLP ROOT-CAUSE SUMMARIZER</div>
              <div style="color:#8b949e; font-size:0.88rem; margin-bottom:0.45rem;">
                Scanned {len(focus)} cohort NLP Ingest field(s) · Role: {role}
              </div>
              <ul style="color:#f8fafc; font-size:0.95rem; line-height:1.45; margin:0; padding-left:1.2rem;">
                {bullets}
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No dominant NLP root-cause signals detected in this cohort.")

    exp_c1, exp_c2 = st.columns(2)
    export_df = focus[
        [
            "Claim ID",
            "Anatomy Target",
            "Status",
            "Days_Elapsed",
            "Spend_To_Date",
            "Drift_Velocity",
            "Statutory Risk Rating",
            "NLP_Ingest",
        ]
    ].copy()
    if not can_unmask:
        # Ministerial / statutory: keep tokenized aliases only
        export_df["Claim ID"] = export_df["Claim ID"].astype(str)
    else:
        export_df["Native ACC Claim ID"] = export_df["Claim ID"].map(
            resolve_native_acc_claim_id
        )

    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    with exp_c1:
        st.download_button(
            "Export Cohort Summary Report (CSV)",
            data=csv_bytes,
            file_name=f"cohort_{anatomy.replace(' ', '_').replace('(', '').replace(')', '')}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"export_cohort_csv_{anatomy}",
        )
    report_txt = (
        f"NZ ACC COHORT SUMMARY REPORT\n"
        f"Anatomy: {anatomy}\n"
        f"Critical Drift Subjects: {n_critical}\n"
        f"Average Days Elapsed: {avg_days:.1f}\n"
        f"Cumulative Financial Risk (NZD): ${cumulative_risk:,.0f}\n"
        f"Primary Drift Velocity: {primary_velocity:.2f}\n"
        f"Role: {role}\n"
        f"PII Unmask Allowed: {can_unmask}\n\n"
        f"SYNTHESIZED DRIFT CAUSE BREAKDOWN\n"
        + "\n".join(f"- {c} (weight {w})" for c, w, _ in causes)
        + "\n\nCLAIMANTS\n"
        + "\n".join(export_df["Claim ID"].astype(str).tolist())
    )
    with exp_c2:
        st.download_button(
            "Export Cohort Summary Report (PDF/TXT)",
            data=report_txt.encode("utf-8"),
            file_name=f"cohort_{anatomy.replace(' ', '_')}_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key=f"export_cohort_txt_{anatomy}",
        )

    if st.button(
        "Apply Batch Intervention Protocol to Cohort",
        type="primary",
        use_container_width=True,
        key=f"batch_intervene_{anatomy}",
    ):
        st.success(
            f"Batch intervention protocol armed for {n_critical or len(focus)} "
            f"{anatomy} subject(s) — pathway acceleration + MSD light-duty match queued."
        )

    st.markdown("#### Cohort Claimant List")
    for _, row in focus.iterrows():
        token = str(row["Claim ID"])
        display_id = token
        if can_unmask and st.session_state.get(f"resolve_native_{token}", False):
            display_id = f"{token} → {resolve_native_acc_claim_id(token)}"
        c1, c2, c3, c4 = st.columns([2.2, 1.4, 1.2, 1.0])
        c1.markdown(f"**{display_id}**")
        c2.caption(str(row["Status"]))
        c3.caption(f"${float(row['Spend_To_Date']):,.0f} NZD · Day {int(row['Days_Elapsed'])}")
        c4.button(
            "Open",
            key=f"open_cohort_{token}",
            use_container_width=True,
            on_click=set_audit_view,
            args=(token,),
        )


df_master_ledger = load_internal_portfolio_ledger()
critical_drift_count = int(
    (df_master_ledger["Status"] == "CRITICAL DRIFT").sum()
)
# Portfolio-level watchlist count for Ministerial banner (scheme-wide)
SCHEME_CRITICAL_SUBJECTS = 18

if "identity_audit_log" not in st.session_state:
    st.session_state.identity_audit_log = []
if "audit_view_selection" not in st.session_state:
    st.session_state.audit_view_selection = GLOBAL_VIEW
if "audit_status_filter" not in st.session_state:
    st.session_state.audit_status_filter = "ALL"
if "audit_anatomy_filter" not in st.session_state:
    st.session_state.audit_anatomy_filter = "ALL"
if "cohort_mode" not in st.session_state:
    st.session_state.cohort_mode = False
if "audit_focus_token" not in st.session_state:
    st.session_state.audit_focus_token = False
if "ministerial_override" not in st.session_state:
    st.session_state.ministerial_override = False


def _append_identity_audit(actor: str, action: str, token: str, native_id: str) -> None:
    from datetime import datetime, timezone

    st.session_state.identity_audit_log.append(
        {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
            "actor": actor,
            "action": action,
            "token": token,
            "native_id": native_id,
        }
    )
    # Keep a short rolling window for the session console
    if len(st.session_state.identity_audit_log) > 40:
        st.session_state.identity_audit_log = st.session_state.identity_audit_log[-40:]


# --- SIDEBAR: GOVERNANCE LAYER FILTERS ---
with st.sidebar:
    st.markdown("### NZ ACC SCHEME GOVERNANCE")
    role = st.selectbox(
        "Active User Role Matrix",
        [
            SCHEME_DIRECTOR,
            CLAIMS_OFFICER,
            REVIEWING_SPECIALIST,
            CLINICAL_TRIAGE_ROLE,
            VOCATIONAL_MSD_ROLE,
            MINISTER_ROLE,
        ],
        key="active_user_role_matrix",
    )
    statutory_briefing_mode = role == MINISTER_ROLE
    clinical_triage_mode = role == CLINICAL_TRIAGE_ROLE
    vocational_msd_mode = role == VOCATIONAL_MSD_ROLE
    department_isolated_mode = clinical_triage_mode or vocational_msd_mode
    # GM + caseworkers/specialists may unmask; Minister + department roles keep aliases
    can_unmask_identity = role in {
        SCHEME_DIRECTOR,
        CLAIMS_OFFICER,
        REVIEWING_SPECIALIST,
    }
    st.markdown("---")
    if clinical_triage_mode:
        st.markdown("### CLINICAL TRIAGE MODE")
        st.info(
            "Isolated Health & Medical surface — financial payouts, wage ledgers, "
            "and legal dispute matrices are suppressed."
        )
        st.caption("Te Whatu Ora · Health NZ Clinical Grid · Diagnostic Triage")
    elif vocational_msd_mode:
        st.markdown("### VOCATIONAL & MSD MODE")
        st.info(
            "Isolated MSD Placement surface — clinical dossiers, Cabinet liability "
            "matrices, and legal dispute chrome are suppressed."
        )
        st.caption("MSD Workforce Pipeline · Light-Duty Match · Retraining Vouchers")
    else:
        st.markdown("### SCHEME MANDATE INJECTION")
        cap_floor = st.slider("Enforce Liability Mitigation Floor (%)", 0, 50, 15)
        st.text_input(
            "Disseminate Performance Mandate",
            placeholder="e.g., Accelerate Pathway Interventions",
        )
        if statutory_briefing_mode:
            st.info(
                "Statutory Briefing Mode active — Crown Entity Act compliance view."
            )
            st.caption(
                "Aggregated cohort & root-cause analysis permitted. "
                "Individual PII / Native ACC Claim ID unmasking restricted."
            )
        st.caption("Localized NZ ACC · IRD · MSD · Health NZ · Ministerial AoG grids")
    if st.session_state.identity_audit_log and not department_isolated_mode:
        with st.expander("Identity Unmask Audit Log", expanded=False):
            for entry in reversed(st.session_state.identity_audit_log[-8:]):
                st.text(
                    f"{entry['ts']} · {entry['actor']} · {entry['action']} · "
                    f"{entry['token']} → {entry['native_id']}"
                )

# Department surfaces are strictly isolated — no scheme finance / Cabinet chrome.
if clinical_triage_mode:
    st.title("NZ ACC RISK ORCHESTRATION ENGINE")
    st.markdown(
        "<p class='statutory-meta'>"
        "Clinical Department Surface · Health NZ / Te Whatu Ora Triage Channel</p>",
        unsafe_allow_html=True,
    )
    render_clinical_triage_view()
    st.stop()

if vocational_msd_mode:
    st.title("NZ ACC RISK ORCHESTRATION ENGINE")
    st.markdown(
        "<p class='statutory-meta'>"
        "Vocational Department Surface · MSD Workforce Pipeline Channel</p>",
        unsafe_allow_html=True,
    )
    render_vocational_msd_view()
    st.stop()

# --- MAIN PERFORMANCE DASHBOARD TITLE ---
st.title("NZ ACC RISK ORCHESTRATION ENGINE")
st.markdown(
    "<p class='statutory-meta'>"
    "Statutory Governance: Answerable to Minister for ACC | "
    "Crown Entity Act Compliance Mode</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#8b949e; margin-top:-6px;'>"
    "AAT Scheme Performance · Predictive Operational Risk & Long-Tail Claims "
    "Governance (NZD) · All-of-Government Integration</p>",
    unsafe_allow_html=True,
)
if statutory_briefing_mode:
    st.markdown(
        '<div class="briefing-mode-chip">STATUTORY BRIEFING MODE · MINISTERIAL OVERLAY</div>',
        unsafe_allow_html=True,
    )
st.markdown("---")

# --- MINISTERIAL EXECUTIVE DIRECTIVE MATRIX ---
st.markdown(
    """
    <div class="directive-matrix">
      <div style="font-family:'IBM Plex Mono', monospace; font-size:0.75rem;
                  color:#ef4444; font-weight:700; letter-spacing:0.05em;
                  text-transform:uppercase;">
        Statutory Cabinet Authority Portal
      </div>
      <h3 style="margin-top:0.25rem; margin-bottom:0.45rem; color:#ffffff;">
        Ministerial Executive Directive Matrix
      </h3>
      <p style="color:#8b949e; font-size:0.88rem; margin:0;">
        Crown Executive input bypasses inter-departmental friction. Activating
        systemic overrides forces IRD / MSD / Health NZ reconciliation and
        re-allocates scheme capital reserves immediately.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)
dir_col1, dir_col2 = st.columns(2)
with dir_col1:
    st.checkbox(
        "Force Cross-Agency Integration Share Mandate",
        key="ministerial_override",
        help="Bypass bureaucratic silos — binds regional drift heat map nationwide.",
    )
with dir_col2:
    st.selectbox(
        "Macro Statutory Intervention",
        [
            "Maintain Standard Operations runway",
            "Emergency CapEx Liquidity Release (Settle P0 Drift Blocks In Bulk)",
            "Direct MSD to Open 500 Immediate Training Certs",
            "Fast-Track Health NZ Clinical Network Triage Mandate",
        ],
        key="macro_statutory_intervention",
    )

# --- DYNAMIC REGIONAL DRIFT HEAT MAP SUMMARY ---
st.markdown("### Dynamic Regional Drift Heat Map Summary")
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem; margin-top:-0.55rem;'>"
    "Major healthcare regions · Primary bottleneck · Liability (NZD) · Drift velocity</p>",
    unsafe_allow_html=True,
)

ministerial_policy_active = bool(st.session_state.ministerial_override)
if ministerial_policy_active:
    banner_msg = sanitize_html_text(
        "Ministerial Policy Active: Regional Drift Suppressed Nationwide.",
        max_chars=160,
    )
    st.markdown(
        f'<div class="heat-policy-banner">{banner_msg}</div>',
        unsafe_allow_html=True,
    )

heat_cards = build_regional_drift_cards(ministerial_policy_active)
heat_cols = st.columns(4)
for col, card in zip(heat_cols, heat_cards):
    with col:
        st.markdown(
            render_regional_heat_card(card, policy_active=ministerial_policy_active),
            unsafe_allow_html=True,
        )

st.markdown("---")

# --- WHAT / WHERE / WHEN SEQUENCE (US Risk viewport container layout · Crown metrics) ---
# Exact visual port of the US Layer-1 metric-box row; labels remapped to AoG agencies.
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem; margin-bottom:0.35rem;'>"
    "What · Where · When — Crown Agency Sync Surface · "
    "Health NZ · MSD · IRD · Ministerial</p>",
    unsafe_allow_html=True,
)

www_col1, www_col2, www_col3, www_col4 = st.columns(4)

with www_col1:
    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-sequence-tag">What</div>'
        '<div class="metric-label">Health NZ Clinical Grid</div>'
        '<div class="metric-value-green">Operational</div>'
        '<div class="metric-subtext">Orthopaedic records linked · HNZ-MED-4402</div>'
        "</div>",
        unsafe_allow_html=True,
    )
with www_col2:
    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-sequence-tag">Where</div>'
        '<div class="metric-label">MSD Workforce Pipeline</div>'
        '<div class="metric-value-silver">14 Matches</div>'
        '<div class="metric-subtext">Modified light-duty · MSD-AX-7710</div>'
        "</div>",
        unsafe_allow_html=True,
    )
with www_col3:
    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-sequence-tag">When</div>'
        '<div class="metric-label">IRD Income Exchange</div>'
        '<div class="metric-value-green">Live Sync</div>'
        '<div class="metric-subtext">12-month wage ledger · IRD-2026-99X4 · 11:42</div>'
        "</div>",
        unsafe_allow_html=True,
    )
with www_col4:
    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-sequence-tag">Crown</div>'
        '<div class="metric-label">Ministerial Cabinet Pipeline</div>'
        '<div class="metric-value-silver" style="color:#38bdf8;">Blue / Active</div>'
        '<div class="metric-subtext">BIM escalation · CAB-BIM-2026-ACC</div>'
        "</div>",
        unsafe_allow_html=True,
    )

# Channel detail expanders (secondary) — harvest hashes remain available without cluttering viewport
with st.expander("All-of-Government channel hashes & harvest receipts", expanded=False):
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(
        "**Health NZ** · PROXIED / OPERATIONAL · Last harvest 10:15 AM · HNZ-MED-4402"
    )
    d2.markdown(
        "**MSD** · LIVE INTEGRATION · Last harvest 11:40 AM · MSD-AX-7710"
    )
    d3.markdown(
        "**IRD** · SECURE LIVE SYNC · Last harvest 11:42 AM · IRD-2026-99X4"
    )
    d4.markdown(
        "**Ministerial** · BLUE / ACTIVE · Last harvest 11:45 AM · CAB-BIM-2026-ACC"
    )

# --- Ministerial Escalation Banner (between AoG grid and Audit Command) ---
if SCHEME_CRITICAL_SUBJECTS > 0:
    st.markdown(
        f"""
        <div class="ministerial-banner">
          <div class="ministerial-badge">[MINISTERIAL WATCHLIST ACTIVE]</div>
          <div style="color:#ffffff; font-size:1.15rem; font-weight:700; margin-bottom:0.35rem;">
            Critical Pathway Drift — Statutory Escalation Surface
          </div>
          <div style="color:#e2e8f0; font-size:1rem; font-weight:600; margin-bottom:0.55rem;">
            {SCHEME_CRITICAL_SUBJECTS} Subjects breaching long-tail liability thresholds
          </div>
          <div style="color:#8b949e; font-size:0.85rem; font-family:monospace;">
            Crown Entity Act · Answerable to Minister for ACC · BIM / Statutory Escalation channel
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "Generate Cabinet Briefing Note (BIM / Statutory Escalation)",
        type="primary",
        use_container_width=True,
        key="generate_cabinet_briefing",
    ):
        st.success(
            "Cabinet Briefing Note compiled — BIM / Statutory Escalation packet "
            "staged for Minister for ACC. Provenance receipt sealed to Crown vault."
        )
        if statutory_briefing_mode:
            st.code(
                "BIM-ACC-2026 · Watchlist subjects: 18 · "
                "Cabinet Threshold Exceeded files: "
                f"{int((df_master_ledger['Statutory Risk Rating'] == STATUTORY_CABINET).sum())} · "
                "Status: READY FOR TABLE",
                language=None,
            )
    if st.button(
        "Open Critical Drift Cohort in Audit View",
        use_container_width=True,
        key="banner_jump_critical_drift",
        on_click=jump_to_audit_sector,
        kwargs={"status": "CRITICAL DRIFT", "cohort": True},
    ):
        pass

st.markdown("---")

# --- CENTRAL ROUTING SELECTOR (cross-sector jump target) ---
st.markdown('<div id="audit-view-command-sector"></div>', unsafe_allow_html=True)
if st.session_state.get("audit_focus_token"):
    st.success("AUDIT VIEW COMMAND SECTOR focused — filters synced from cross-sector jump.")
    st.session_state.audit_focus_token = False

claim_options = [GLOBAL_VIEW] + sorted(
    df_master_ledger["Claim ID"].astype(str).tolist()
)
if st.session_state.audit_view_selection not in claim_options:
    st.session_state.audit_view_selection = GLOBAL_VIEW

view_selection = st.selectbox(
    "AUDIT VIEW COMMAND SECTOR",
    claim_options,
    key="audit_view_selection",
)

filter_c1, filter_c2, filter_c3 = st.columns([1.2, 1.4, 1.0])
with filter_c1:
    st.selectbox(
        "Status Pre-filter",
        ["ALL", "CRITICAL DRIFT", "NOMINAL ALIGNMENT"],
        key="audit_status_filter",
    )
with filter_c2:
    anatomy_options = ["ALL"] + sorted(
        df_master_ledger["Anatomy Target"].astype(str).unique().tolist()
    )
    st.selectbox(
        "Anatomy Target Pre-filter",
        anatomy_options,
        key="audit_anatomy_filter",
    )
with filter_c3:
    if st.button(
        "Clear Audit Filters",
        use_container_width=True,
        key="clear_audit_filters",
        on_click=clear_audit_filters,
    ):
        pass

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# INTERFACE LAYER A: GLOBAL SCHEME PORTFOLIO VIEW
# ==============================================================================
if view_selection == GLOBAL_VIEW:

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Total Scheme Claims</div>'
            '<div class="metric-value-silver">142 Active</div>'
            '<div class="metric-subtext">Regional Portfolio Intake</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Critical Pathway Drift</div>'
            '<div class="metric-value-crimson">18 Subjects</div>'
            '<div class="metric-subtext">Click to jump → Audit View</div></div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "Jump: Critical Drift → Audit View",
            key="metric_jump_critical_drift",
            use_container_width=True,
            type="primary",
            on_click=jump_to_audit_sector,
            kwargs={"status": "CRITICAL DRIFT", "cohort": True},
        ):
            pass
    with col3:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Performance Index</div>'
            '<div class="metric-value-green">85.9%</div>'
            '<div class="metric-subtext">Baseline Trajectory Alignment</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Ministerial Expectations Match</div>'
            '<div class="metric-value-silver" style="color:#38bdf8;">88%</div>'
            '<div class="metric-subtext">Trajectory Alignment</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Anatomical Cohort Jump Pads")
    anatomy_vals = sorted(df_master_ledger["Anatomy Target"].astype(str).unique().tolist())
    anatomy_cols = st.columns(max(len(anatomy_vals), 1))
    for col, anatomy in zip(anatomy_cols, anatomy_vals):
        n_crit = int(
            (
                (df_master_ledger["Anatomy Target"] == anatomy)
                & (df_master_ledger["Status"] == "CRITICAL DRIFT")
            ).sum()
        )
        with col:
            if st.button(
                f"{anatomy} ({n_crit} critical)",
                key=f"anatomy_jump_{anatomy}",
                use_container_width=True,
                on_click=jump_to_audit_sector,
                kwargs={
                    "anatomy": anatomy,
                    "status": "CRITICAL DRIFT",
                    "cohort": True,
                },
            ):
                pass

    filtered_ledger = apply_ledger_filters(df_master_ledger)
    active_anatomy = st.session_state.get("audit_anatomy_filter", "ALL")
    show_cohort = bool(st.session_state.get("cohort_mode")) and active_anatomy not in (
        None,
        "ALL",
        "",
    )

    if show_cohort:
        anatomy_cohort = df_master_ledger[
            df_master_ledger["Anatomy Target"] == active_anatomy
        ].copy()
        render_cohort_analysis_panel(
            anatomy_cohort,
            anatomy=str(active_anatomy),
            can_unmask=can_unmask_identity,
            role=role,
        )
        st.markdown("---")

    if statutory_briefing_mode:
        st.markdown("### STATUTORY BRIEFING MODE — CROWN GOVERNANCE SURFACE")
        st.markdown(
            """
            <div class="metric-box" style="border-left: 4px solid #38bdf8;">
              <div class="metric-label" style="color:#38bdf8;">MINISTER FOR ACC · HIGH-LEVEL OVERSIGHT</div>
              <div style="color:#ffffff; font-weight:600; margin-bottom:0.55rem;">
                Tactical case-worker widgets suppressed. Displaying statutory metrics,
                long-tail financial liability trajectories, and Cabinet briefing tools.
              </div>
              <div style="font-size:0.9rem; color:#8b949e; line-height:1.45;">
                Crown Entity Act Compliance Mode · Scheme Performance Index 85.9% ·
                Ministerial Expectations Match 88% · Watchlist 18 subjects
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Long-Tail Liability Watchlist", f"{SCHEME_CRITICAL_SUBJECTS} subjects")
        m2.metric("Cabinet Threshold Files", f"{int((df_master_ledger['Statutory Risk Rating'] == STATUTORY_CABINET).sum())}")
        m3.metric("Ministerial Escalations", f"{int((df_master_ledger['Statutory Risk Rating'] == STATUTORY_MINISTERIAL).sum())}")

        st.markdown("#### Long-Tail Financial Liability Trajectory (NZD)")
        days_series = np.arange(0, 121, 10)
        standard_macro = np.clip(25000 * 3 * (days_series / 90), 0, 25000 * 3)
        actual_macro = 25000 * 3 * (days_series / 90) * (1.0 + (0.006 * days_series))
        ministerial_ceiling = standard_macro * 1.12
        df_macro_chart = pd.DataFrame(
            {
                "Days Elapsed": days_series,
                "Target Operational Runway": standard_macro,
                "Actual Scheme Outflow": actual_macro,
                "Ministerial Liability Ceiling": ministerial_ceiling,
            }
        )
        st.line_chart(
            df_macro_chart,
            x="Days Elapsed",
            y=[
                "Target Operational Runway",
                "Actual Scheme Outflow",
                "Ministerial Liability Ceiling",
            ],
        )

        st.markdown("#### Cabinet Briefing Tools")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Export BIM One-Pager", use_container_width=True):
                st.info("BIM one-pager staged for Ministerial pouch.")
        with b2:
            if st.button("Table for Cabinet Committee", use_container_width=True):
                st.success("Matter queued for Cabinet committee timetable.")

    elif role == CLAIMS_OFFICER:
        st.markdown("### CLAIMS OFFICER / ANALYST — ACTION TASK")
        html_task_co = f"""<div class="metric-box" style="border-left: 4px solid #ef4444; padding: 1.2rem;">
<div class="metric-label" style="color:#ef4444;">TASK ID: CO-AAT-2026-031</div>
<div class="metric-subtext" style="color:#ffffff; font-weight:600; margin-bottom:0.4rem;">Clear the CRITICAL DRIFT files before they harden into long-tail PPD exposure.</div>
<div style="font-size:0.85rem; color:#8b949e;">Active Mandate: {cap_floor}% CapEx Mitigation Control Active</div>
</div>"""
        st.markdown(html_task_co, unsafe_allow_html=True)

    elif role == REVIEWING_SPECIALIST:
        st.markdown("### REVIEWING SPECIALIST — CLINICAL ESCALATION AUDIT DECK")
        html_task_rs = """<div class="metric-box" style="border-left: 4px solid #a855f7; padding: 1.2rem;">
<div class="metric-label" style="color:#a855f7;">TASK ID: RS-AAT-2026-042</div>
<div class="metric-subtext" style="color:#ffffff; font-weight:600; margin-bottom:0.4rem;">Validate physical telemetry variance anomalies and verify Independent Medical Examination (IME) compliance directives.</div>
</div>"""
        st.markdown(html_task_rs, unsafe_allow_html=True)

    # Shared interactive Master Claims Accountability Ledger
    st.markdown("### MASTER CLAIMS ACCOUNTABILITY LEDGER")
    show_only_escalations = st.checkbox(
        "Show Only Ministerial Escalations",
        value=statutory_briefing_mode,
        key="filter_ministerial_escalations_ledger",
    )
    ledger_view = filtered_ledger.copy()
    if show_only_escalations:
        ledger_view = ledger_view[
            ledger_view["Statutory Risk Rating"].isin(
                [STATUTORY_MINISTERIAL, STATUTORY_CABINET]
            )
        ]

    st.caption(
        "Click Status or Anatomy Target to sync Audit View filters and open cohort analysis."
    )
    header_cols = st.columns([2.0, 1.6, 1.3, 1.5, 0.9])
    header_cols[0].markdown("**Claim ID**")
    header_cols[1].markdown("**Anatomy Target**")
    header_cols[2].markdown("**Status**")
    header_cols[3].markdown("**Statutory Risk Rating**")
    header_cols[4].markdown("**Open**")

    for _, row in ledger_view.iterrows():
        token = str(row["Claim ID"])
        anatomy = str(row["Anatomy Target"])
        status = str(row["Status"])
        rating = str(row["Statutory Risk Rating"])
        r1, r2, r3, r4, r5 = st.columns([2.0, 1.6, 1.3, 1.5, 0.9])
        r1.code(token, language=None)
        r2.button(
            anatomy,
            key=f"ledger_anatomy_{token}",
            use_container_width=True,
            on_click=jump_to_audit_sector,
            kwargs={
                "anatomy": anatomy,
                "status": "CRITICAL DRIFT",
                "cohort": True,
            },
        )
        r3.button(
            status,
            key=f"ledger_status_{token}",
            use_container_width=True,
            on_click=jump_to_audit_sector,
            kwargs={"status": status, "cohort": True},
        )
        r4.caption(rating)
        r5.button(
            "Open",
            key=f"ledger_open_{token}",
            use_container_width=True,
            on_click=set_audit_view,
            args=(token,),
        )

    if role == SCHEME_DIRECTOR and not statutory_briefing_mode:
        st.markdown("---")
        st.markdown("### AGGREGATE SCHEME CAPEX VELOCITY TRAJECTORY")
        days_series = np.arange(0, 121, 10)
        standard_macro = np.clip(25000 * 3 * (days_series / 90), 0, 25000 * 3)
        actual_macro = 25000 * 3 * (days_series / 90) * (1.0 + (0.006 * days_series))
        df_macro_chart = pd.DataFrame(
            {
                "Days Elapsed": days_series,
                "Target Operational Runway": standard_macro,
                "Actual Scheme Outflow": actual_macro,
            }
        )
        st.line_chart(
            df_macro_chart,
            x="Days Elapsed",
            y=["Target Operational Runway", "Actual Scheme Outflow"],
        )

# ==============================================================================
# INTERFACE LAYER B: INDIVIDUAL DRILL-DOWN VIEW
# ==============================================================================
else:
    selected_row = df_master_ledger[
        df_master_ledger["Claim ID"] == view_selection
    ].iloc[0]

    subject_token = selected_row["Claim ID"]
    anatomy = selected_row["Anatomy Target"]
    age = int(selected_row["Age"])
    duty_tier = selected_row["Demands"]
    actual_rom = float(selected_row["ROM_Actual"])
    actual_spend = float(selected_row["Spend_To_Date"])
    dict_txt = str(selected_row.get("NLP_Ingest") or "")

    # Core Backend Calculations Matrix
    job_multiplier = (
        1.30 if "Heavy" in duty_tier else (1.10 if "Medium" in duty_tier else 0.90)
    )
    age_factor = (age - 25) * 0.015
    calibrated_base_cost = 22500.0 * (1.0 + age_factor) * job_multiplier
    calibrated_base_days = int(90 * (1.0 + age_factor) * job_multiplier)

    functional_drift = 100.0 - actual_rom
    ivc = (actual_spend - calibrated_base_cost) / calibrated_base_cost

    projected_final_cost = (
        calibrated_base_cost
        + (functional_drift * 185.0)
        + (ivc * calibrated_base_cost)
    )
    mitigated_reserve_target = projected_final_cost * (1.0 - (cap_floor / 100.0))
    permanent_disability_prob = 1.0 / (
        1.0 + np.exp(-(-2.8 + (age * 0.045) + (functional_drift * 0.055)))
    )

    # Set Color Logic for Display Elements
    if functional_drift > 15.0 or permanent_disability_prob > 0.50:
        status_label = "CRITICAL PATHWAY DRIFT DETECTED"
        status_color = "#ef4444"
        impact_class = "critical-impact-value"
    else:
        status_label = "NOMINAL PATHWAY ALIGNMENT"
        status_color = "#10b981"
        impact_class = "nominal-impact-value"

    # Prescriptive AI Protocol Engine & Adaptive CV Trajectory Loops
    if "Zeta" in subject_token or "Knee" in str(anatomy):
        protocol_html = f"""<div style="background-color:#1b1416; padding:0.8rem; border-radius:4px; border:1px solid #6b21a8; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#ef4444; font-weight:700;">AUTOMATED MITIGATION PROTOCOL</div>
<ul style="color:#f8fafc; font-size:0.88rem; margin:0; padding-left:1.2rem; line-height:1.4;">
<li><strong>Commutation Target:</strong> Initiate immediate Lump-Sum settlement review range (${mitigated_reserve_target:,.0f} - ${projected_final_cost:,.0f} NZD).</li>
<li><strong>IME Authorization:</strong> Issue urgent Independent Medical Examination directive.</li>
<li><strong>Demands Override:</strong> Force immediate drop in Occupational Tier from Heavy Manual to Clerical/Supervisory.</li>
</ul>
</div>"""
        adaptive_cv_html = """<div style="background-color:#18141c; padding:0.8rem; border-radius:4px; border:1px solid #a855f7; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#c084fc; font-weight:700;">ADAPTIVE CAREER TRAJECTORY & CV PIVOT MATRIX</div>
<div style="font-size:0.84rem; color:#8b949e; margin-bottom:0.4rem;">MSD Certified Adoption Mandatory · Inter-Agency Ingest</div>
</div>"""
    elif functional_drift > 15:
        protocol_html = """<div style="background-color:#141b1f; padding:0.8rem; border-radius:4px; border:1px solid #0369a1; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#38bdf8; font-weight:700;">AUTOMATED MITIGATION PROTOCOL</div>
<ul style="color:#f8fafc; font-size:0.88rem; margin:0; padding-left:1.2rem; line-height:1.4;">
<li><strong>Clinical Triage:</strong> Deploy psychological resilience counseling within 7 days.</li>
<li><strong>Light-Duty Matching:</strong> Initialize transitional employer-return tracking protocol.</li>
</ul>
</div>"""
        adaptive_cv_html = """<div style="background-color:#141b1f; padding:0.8rem; border-radius:4px; border:1px solid #0284c7; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#38bdf8; font-weight:700;">ADAPTIVE CAREER TRAJECTORY & CV PIVOT MATRIX</div>
<div style="font-size:0.84rem; color:#8b949e;">MSD Certified Adoption Mandatory</div>
</div>"""
    else:
        protocol_html = """<div style="background-color:#141f17; padding:0.8rem; border-radius:4px; border:1px solid #15803d; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#4ade80; font-weight:700;">AUTOMATED MITIGATION PROTOCOL</div>
<p style="color:#f8fafc; font-size:0.88rem; margin:0;">Path Alignment Secure — maintain standard vocational rehabilitation baseline.</p>
</div>"""
        adaptive_cv_html = """<div style="background-color:#141f17; padding:0.8rem; border-radius:4px; border:1px solid #166534; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#4ade80; font-weight:700;">ADAPTIVE CAREER TRAJECTORY STATUS</div>
<p style="color:#f8fafc; font-size:0.88rem; margin:0;">Baseline capacity holds. Verified via MSD National Framework.</p>
</div>"""

    # Quick anatomy cohort jump from dossier
    if st.button(
        f"Open Anatomical Cohort: {anatomy}",
        key=f"dossier_cohort_{subject_token}",
        use_container_width=True,
        on_click=jump_to_audit_sector,
        kwargs={
            "anatomy": str(anatomy),
            "status": "CRITICAL DRIFT",
            "cohort": True,
        },
    ):
        pass



    st.markdown("## PREVENTATIVE DRIFT RADAR DEEP-DIVE")

    # --- STACKED BLOCK 1: MASTER LEDGER DOSSIER BOX ---
    st.markdown("#### Comprehensive Scheme Ledger Dossier")

    native_acc_id = resolve_native_acc_claim_id(subject_token)
    resolve_key = f"resolve_native_{subject_token}"
    if resolve_key not in st.session_state:
        st.session_state[resolve_key] = False

    # Ministerial statutory mode never retains an unmasked identity surface
    if statutory_briefing_mode and st.session_state[resolve_key]:
        st.session_state[resolve_key] = False

    id_col, btn_col = st.columns([2.4, 1.2])
    with id_col:
        if st.session_state[resolve_key] and can_unmask_identity:
            st.markdown(
                f"""
                <div class="claim-id-bar">
                  <span class="id-label">ID</span>
                  <span class="id-token">{subject_token}</span>
                  <span class="resolve-chip">RESOLVED</span>
                  <span class="id-label">Native ACC Claim ID</span>
                  <span class="id-native">{native_acc_id}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif statutory_briefing_mode:
            st.markdown(
                f"""
                <div class="claim-id-bar">
                  <span class="id-label">ID</span>
                  <span class="id-token">{subject_token}</span>
                  <span class="locked-chip">IDENTITY UNMASKING RESTRICTED</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="claim-id-bar">
                  <span class="id-label">ID</span>
                  <span class="id-token">{subject_token}</span>
                  <span class="masked-chip">MASKED TOKEN</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with btn_col:
        if statutory_briefing_mode:
            st.markdown('<div class="locked-resolve-wrap">', unsafe_allow_html=True)
            if st.button(
                "🔒 Identity Unmasking Restricted",
                key=f"resolve_locked_{subject_token}",
                use_container_width=True,
            ):
                st.warning(
                    "Statutory governance mode restricts access to individual PII."
                )
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(
                '<div class="audit-toast">Minister for ACC · PII gate enforced</div>',
                unsafe_allow_html=True,
            )
        elif can_unmask_identity:
            st.markdown('<div class="active-resolve-wrap">', unsafe_allow_html=True)
            if st.session_state[resolve_key]:
                if st.button(
                    "Re-mask AAT Token",
                    key=f"remask_{subject_token}",
                    use_container_width=True,
                ):
                    st.session_state[resolve_key] = False
                    _append_identity_audit(
                        role, "REMASK", subject_token, native_acc_id
                    )
                    st.rerun()
            else:
                if st.button(
                    "Resolve to Native ACC Claim ID",
                    key=f"resolve_{subject_token}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state[resolve_key] = True
                    _append_identity_audit(
                        role, "UNMASK", subject_token, native_acc_id
                    )
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        # No additional fallback — only Minister is locked; GM/CO/RS unmask via can_unmask_identity

    if st.session_state[resolve_key] and can_unmask_identity:
        id_status_line = (
            f'<span style="font-size:0.9rem; color:#8b949e;">ID:</span> '
            f'<span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{subject_token}</span> '
            f'<span class="resolve-chip">Resolve to Native ACC Claim ID</span><br/>'
            f'<span style="font-size:0.9rem; color:#8b949e;">Native ACC Claim ID:</span> '
            f'<span style="font-size:0.9rem; color:#10b981; font-weight:700;">{native_acc_id}</span><br/>'
        )
    elif statutory_briefing_mode:
        id_status_line = (
            f'<span style="font-size:0.9rem; color:#8b949e;">ID:</span> '
            f'<span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{subject_token}</span> '
            f'<span class="locked-chip">Identity Unmasking Restricted</span><br/>'
        )
    else:
        id_status_line = (
            f'<span style="font-size:0.9rem; color:#8b949e;">ID:</span> '
            f'<span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{subject_token}</span> '
            f'<span class="masked-chip">Resolve to Native ACC Claim ID</span><br/>'
        )

    if role == SCHEME_DIRECTOR:
        fee_line = f"""<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>
<div class="metric-value-green" style="font-size:1.4rem;">${(5000 + (projected_final_cost * 0.12)):,.2f} NZD</div>"""
    else:
        fee_line = """<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>
<div style="color:#8b949e; font-style:italic; font-size:0.95rem;">🔒 SECURE LEDGER PROXIED TO EXECUTIVE SECTOR</div>"""

    # Left-aligned HTML — no indent so Streamlit does not code-fence it
    html_payload = f"""<div class="metric-box" style="border-left: 4px solid {status_color}; padding: 1.5rem; height: auto;">
<div class="metric-label">Scheme Alignment Status</div>
<div style="color:{status_color}; font-weight:700; font-size:1.2rem; margin-bottom:0.8rem;">{status_label}</div>
<div style="background-color:#0c1017; padding:0.8rem; border-radius:4px; border:1px solid #30363d; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#ffffff;">Claimant File Dossier Matrix</div>
{id_status_line}
<span style="font-size:0.9rem; color:#8b949e;">Target Anatomy:</span> <span style="font-size:0.9rem; color:#ffffff;">{anatomy}</span><br/>
<span style="font-size:0.9rem; color:#8b949e;">Demands / Age:</span> <span style="font-size:0.9rem; color:#ffffff;">{duty_tier} (Age {age})</span><br/>
<p style="font-size:0.85rem; color:#8b949e; font-style:italic; margin-top:0.4rem; margin-bottom:0;"><strong>NLP Ingest:</strong> {dict_txt}</p>
</div>
{protocol_html}
{adaptive_cv_html}
<div class="metric-label">Probability of Permanent Disability (PPD)</div>
<div class="{impact_class}">{permanent_disability_prob * 100:.1f}%</div>
<hr style="border:0; border-top:1px solid #30363d; margin: 0.8rem 0;"/>
<div class="metric-label">Total Absolute System Exposure (TASE)</div>
<div class="metric-value-silver" style="font-size:1.5rem; margin-bottom:0.3rem;">${projected_final_cost:,.2f} NZD</div>
<div class="metric-label">Mitigated Capital Reserve Target ({cap_floor}% Floor Applied)</div>
<div class="metric-value-green" style="font-size:1.5rem; margin-bottom:0.3rem;">${mitigated_reserve_target:,.2f} NZD</div>
{fee_line}
</div>"""

    st.markdown(html_payload, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- STACKED BLOCK 2: DATA ALIGNMENT MATRIX ---
    st.markdown("#### Operational Pathway Alignment Vector")
    df_vector = pd.DataFrame(
        {
            "Performance Dimension": [
                "Target Recovery Runway",
                "Expected Cost Runway",
                "Current Capacity",
                "Variance Index",
            ],
            "Validated Standard": [
                f"{calibrated_base_days} Days",
                f"${calibrated_base_cost:,.0f} NZD",
                "100% Target",
                "Nominal",
            ],
            "Live Ingest State": [
                "Day 42",
                f"${actual_spend:,.0f} NZD",
                f"{actual_rom:.0f}% Flexion",
                "High Drift Flag" if functional_drift > 15 else "Clear",
            ],
            "Point of Drift Variance": [
                "On Track",
                f"${actual_spend - calibrated_base_cost:+,.0f} NZD",
                f"-{functional_drift:.0f}% Dev",
                "Path B Active" if functional_drift > 15 else "Clear",
            ],
        }
    )
    st.table(df_vector)
    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Individual Cost Trajectory Trend Graph
    st.markdown("### 📈 INDIVIDUAL PERFORMANCE TIME-COST AXIS")
    days_series = np.arange(0, calibrated_base_days + 31, 10)
    standard_trajectory = np.array(
        [
            min(calibrated_base_cost, (calibrated_base_cost / calibrated_base_days) * d)
            for d in days_series
        ]
    )

    if functional_drift > 15:
        actual_trajectory = np.array(
            [
                (calibrated_base_cost / calibrated_base_days)
                * d
                * (
                    1.0 + (0.007 * d)
                    if d > (calibrated_base_days * 0.4)
                    else 1.0
                )
                for d in days_series
            ]
        )
    else:
        actual_trajectory = standard_trajectory * (1.0 + (ivc * 0.5))

    df_chart = pd.DataFrame(
        {
            "Days Elapsed": days_series,
            "Standard Expected Runway": standard_trajectory,
            "Actual Cumulative Spend Velocity": actual_trajectory,
        }
    )
    st.line_chart(
        df_chart,
        x="Days Elapsed",
        y=["Standard Expected Runway", "Actual Cumulative Spend Velocity"],
    )
