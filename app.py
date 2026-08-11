"""NZ AAT Sovereign Orchestration Engine — secure Crown claims governance.

New Zealand Accident Compensation Corporation operational surface with
All-of-Government grids: IRD Income Exchange, MSD Workforce Pipeline, and
Health NZ Clinical Grid. NZD ledger, MSD certified CV pivot matrices,
Cabinet Minister statutory overrides, and PR #24 HTML sanitation.
"""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from adaptive_drift_learner import (
    BASE_DRIFT_THRESHOLD,
    effective_drift_threshold,
    learner,
)
from config import (
    DEFAULT_SECTOR_KEY,
    EXECUTIVE_THEME,
    PRIVATE_CHROME,
    get_sector_book,
    layer2_operations,
    sector_book_options,
    structural_mirror_cards,
)
from surface_nav import (
    render_command_level_controls,
    render_sidebar_surface_links,
    render_surface_page_links,
)

# Live Gemini / Colab notebook surface (replace with project notebook URL when ready).
GEMINI_NOTEBOOK_URL = "https://colab.research.google.com/"

# Defensive bounds for intake / dossier surfaces (PR #24 compliance).
MAX_TOKEN_CHARS = 96
MAX_STATUS_CHARS = 64
MAX_NOTES_CHARS = 4000
MAX_MANDATE_CHARS = 280
MAX_INTAKE_ROWS = 500
MAX_FIELD_CHARS = 120
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Executive Command Profile media (repo public/ assets).
PUBLIC_DIR = Path(__file__).resolve().parent / "public"
AVATAR_PATH = PUBLIC_DIR / "avatar.png"
BRIEFING_AUDIO_PATH = PUBLIC_DIR / "briefing.mp3"
COMMAND_VIDEO_PATH = PUBLIC_DIR / "command_overview.mp4"


def sanitize_plain_text(value: Any, *, max_chars: int) -> str:
    """Strip control chars and truncate free-form intake before render/store."""
    text = _CONTROL_CHARS.sub("", str(value if value is not None else "")).strip()
    return text[:max_chars]


def sanitize_html_text(value: Any, *, max_chars: int | None = None) -> str:
    """HTML-escape dynamic values injected into custom metric-box markup."""
    text = sanitize_plain_text(
        value, max_chars=max_chars if max_chars is not None else MAX_FIELD_CHARS
    )
    return html.escape(text, quote=True)


def sanitize_claim_token(value: Any) -> str:
    """Bound participant / claim identifiers used across dossier + tables."""
    return sanitize_plain_text(value, max_chars=MAX_TOKEN_CHARS)


def sanitize_status_label(value: Any) -> str:
    return sanitize_plain_text(value, max_chars=MAX_STATUS_CHARS)


def sanitize_for_markdown(value: Any, *, max_chars: int = MAX_TOKEN_CHARS) -> str:
    """Neutralize markdown metacharacters in claim labels rendered via st.markdown."""
    text = sanitize_plain_text(value, max_chars=max_chars)
    for ch in ("*", "_", "`", "[", "]", "<", ">", "|"):
        text = text.replace(ch, "")
    return text


def bound_intake_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Cap row count for any corporate / matrix intake parse to avoid unbounded load."""
    if frame is None or frame.empty:
        return frame
    if len(frame) > MAX_INTAKE_ROWS:
        return frame.iloc[:MAX_INTAKE_ROWS].copy()
    return frame


def render_sector_header(sector: dict[str, Any]) -> None:
    """Render sector title and statutory subtitle from config.py."""
    header = sector["header"]
    st.title(header["title"])
    st.markdown(
        f"<p class='statutory-meta'>"
        f"{sanitize_html_text(header['statutory_meta'], max_chars=280)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{EXECUTIVE_THEME['muted']}; margin-top:-6px;'>"
        f"{sanitize_html_text(header['subtitle'], max_chars=320)}</p>",
        unsafe_allow_html=True,
    )


def build_metric_card_html(card: dict[str, Any]) -> str:
    """Build a standardized metric card: Label, Big Value, Ground-Truth Basis."""
    value_class = sanitize_html_text(
        card.get("value_class", "metric-value-silver"), max_chars=48
    )
    border_style = ""
    if card.get("border_accent"):
        accent = sanitize_html_text(card["border_accent"], max_chars=16)
        border_style = f' style="border-left:3px solid {accent};"'
    sequence_html = ""
    if card.get("sequence_tag"):
        safe_tag = sanitize_html_text(card["sequence_tag"], max_chars=32)
        sequence_html = f'<div class="metric-sequence-tag">{safe_tag}</div>'
    safe_label = sanitize_html_text(card["label"], max_chars=80)
    safe_value = sanitize_html_text(card["big_value"], max_chars=64)
    safe_basis = sanitize_html_text(card["ground_truth_basis"], max_chars=120)
    return (
        f'<div class="metric-box"{border_style}>'
        f"{sequence_html}"
        f'<div class="metric-label">{safe_label}</div>'
        f'<div class="{value_class}">{safe_value}</div>'
        f'<div class="metric-subtext">{safe_basis}</div>'
        f"</div>"
    )


def render_metric_card_row(cards: list[dict[str, Any]], *, columns: int = 4) -> None:
    """Render a row of metric cards from sector book configuration."""
    metric_cols = st.columns(columns)
    for col, card in zip(metric_cols, cards):
        with col:
            st.markdown(build_metric_card_html(card), unsafe_allow_html=True)


def render_operational_bridge(sector: dict[str, Any]) -> None:
    """Render operational bridge caption, metric row, and channel receipts."""
    bridge = sector["operational_bridge"]
    st.markdown(
        f"<p style='color:{EXECUTIVE_THEME['muted']}; font-size:0.9rem; "
        f"margin-bottom:0.35rem;'>"
        f"{sanitize_html_text(bridge['section_caption'], max_chars=200)}</p>",
        unsafe_allow_html=True,
    )
    render_metric_card_row(sector["bridge_metrics"])
    with st.expander(
        "All-of-Government channel hashes & harvest receipts", expanded=False
    ):
        receipt_cols = st.columns(max(len(bridge["channel_receipts"]), 1))
        for col, receipt in zip(receipt_cols, bridge["channel_receipts"]):
            col.markdown(
                f"**{sanitize_for_markdown(receipt['agency'], max_chars=48)}** · "
                f"{sanitize_for_markdown(receipt['status'], max_chars=48)} · "
                f"{sanitize_for_markdown(receipt['receipt'], max_chars=120)}"
            )


def render_operational_bridge_banner(sector: dict[str, Any]) -> None:
    """Render sector escalation banner when critical subjects exceed zero."""
    critical = int(sector.get("critical_subjects", 0))
    if critical <= 0:
        return
    bridge = sector["operational_bridge"]
    headline = bridge["banner_headline"].format(critical_subjects=critical)
    safe_badge = sanitize_html_text(bridge["banner_badge"], max_chars=64)
    safe_title = sanitize_html_text(bridge["banner_title"], max_chars=120)
    safe_headline = sanitize_html_text(headline, max_chars=120)
    safe_footer = sanitize_html_text(bridge["banner_footer"], max_chars=200)
    muted_color = EXECUTIVE_THEME["muted"]
    st.markdown(
        f"""
        <div class="ministerial-banner">
          <div class="ministerial-badge">{safe_badge}</div>
          <div style="color:#ffffff; font-size:1.15rem; font-weight:700;
                      margin-bottom:0.35rem;">
            {safe_title}
          </div>
          <div style="color:#e2e8f0; font-size:1rem; font-weight:600;
                      margin-bottom:0.55rem;">
            {safe_headline}
          </div>
          <div style="color:{muted_color}; font-size:0.85rem;
                      font-family:monospace;">
            {safe_footer}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_structural_mirror_kpis(sector: dict[str, Any]) -> None:
    """Render Structural Mirror Standard: 3 KPI cards + Card 3 Layer 2 drill-down."""
    cards = structural_mirror_cards(sector)
    layer2 = layer2_operations(sector)
    sector_code = sanitize_plain_text(sector.get("code", "SECTOR"), max_chars=32)

    st.markdown(
        f"<p style='color:{EXECUTIVE_THEME['muted']}; font-size:0.9rem; "
        f"margin-bottom:0.35rem;'>"
        "Structural Mirror Standard · Macro Valuation · Velocity Friction · "
        "Actionable Controllable Loss</p>",
        unsafe_allow_html=True,
    )

    kpi_cols = st.columns(3)
    for col, card in zip(kpi_cols, cards):
        with col:
            st.markdown(build_metric_card_html(card), unsafe_allow_html=True)

    # Card 3 control: Inspect Layer 2 Operational Drift
    with kpi_cols[min(2, max(len(cards) - 1, 0))]:
        inspect_label = sanitize_for_markdown(
            layer2.get("inspect_label", "Inspect Layer 2 Operational Drift"),
            max_chars=80,
        )
        inspect_layer2 = st.toggle(
            inspect_label,
            value=bool(st.session_state.get(f"layer2_open_{sector_code}", False)),
            key=f"layer2_toggle_{sector_code}",
        )
        st.session_state[f"layer2_open_{sector_code}"] = inspect_layer2

    if not st.session_state.get(f"layer2_open_{sector_code}", False):
        return

    render_layer2_operations_view(sector, layer2)


def render_layer2_operations_view(
    sector: dict[str, Any], layer2: dict[str, Any]
) -> None:
    """Expandable Layer 2 site/queue breakdown + Layer 3 clearance trigger."""
    sector_code = sanitize_plain_text(sector.get("code", "SECTOR"), max_chars=32)
    title = sanitize_for_markdown(layer2.get("title", "Layer 2 Operations View"), max_chars=80)
    caption = sanitize_for_markdown(layer2.get("caption", ""), max_chars=200)

    with st.expander(title, expanded=True):
        st.caption(caption)
        rows = list(layer2.get("site_queue_metrics", []))
        if rows:
            table_rows = []
            for row in rows:
                table_rows.append(
                    {
                        "Site": sanitize_for_markdown(row.get("site", ""), max_chars=64),
                        "Queue": sanitize_for_markdown(row.get("queue", ""), max_chars=64),
                        "Backlog": sanitize_for_markdown(
                            row.get("backlog", ""), max_chars=32
                        ),
                        "Delay": sanitize_for_markdown(
                            row.get("delay_days", ""), max_chars=24
                        ),
                        "Burn": sanitize_for_markdown(row.get("burn", ""), max_chars=32),
                        "Ground-Truth Basis": sanitize_for_markdown(
                            row.get("ground_truth_basis", ""), max_chars=120
                        ),
                    }
                )
            st.dataframe(
                pd.DataFrame(table_rows),
                use_container_width=True,
                hide_index=True,
            )
            metric_cols = st.columns(min(len(rows), 4))
            for col, row in zip(metric_cols, rows):
                with col:
                    site_card = {
                        "label": row.get("site", "Site"),
                        "big_value": row.get("burn", "-"),
                        "ground_truth_basis": (
                            f"{row.get('queue', 'Queue')} · "
                            f"{row.get('delay_days', '-')} · "
                            f"{row.get('ground_truth_basis', '')}"
                        ),
                        "value_class": "metric-value-crimson",
                    }
                    st.markdown(
                        build_metric_card_html(site_card), unsafe_allow_html=True
                    )

        action_label = sanitize_for_markdown(
            layer2.get("layer3_action_label", "Trigger Layer 3 Actionable Clearance"),
            max_chars=80,
        )
        if st.button(
            action_label,
            type="primary",
            use_container_width=True,
            key=f"layer3_clearance_{sector_code}",
        ):
            receipt = sanitize_for_markdown(
                layer2.get(
                    "layer3_clearance_receipt",
                    "Layer 3 Actionable Clearance staged.",
                ),
                max_chars=240,
            )
            st.session_state[f"layer3_receipt_{sector_code}"] = receipt
            st.success(receipt)
        elif st.session_state.get(f"layer3_receipt_{sector_code}"):
            st.info(
                sanitize_for_markdown(
                    st.session_state[f"layer3_receipt_{sector_code}"],
                    max_chars=240,
                )
            )


# 1. High-Contrast Sovereign Dark Theme Configuration
st.set_page_config(
    layout="wide",
    page_title="NZ AAT Sovereign Orchestration Engine",
    page_icon="⬡",
    initial_sidebar_state="expanded",
)

# Private Chrome Removal — hide native Streamlit chrome for iPad Board presentations
if PRIVATE_CHROME.get("enabled", True):
    st.markdown(
        """
        <style>
        /* ============================================================
           PRIVATE CHROME REMOVAL (CSS Injection)
           Hide default Streamlit UI so the surface reads 100% custom
           on iPad (header, Share, hamburger, GitHub link, footer).
           ============================================================ */
        #MainMenu,
        #MainMenu > button,
        header[data-testid="stHeader"],
        header.stAppHeader,
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stAppDeployButton"],
        [data-testid="stDeployButton"],
        [data-testid="baseButton-header"],
        [data-testid="baseButton-headerNoPadding"],
        [data-testid="stBaseButton-header"],
        [data-testid="stBaseButton-headerNoPadding"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="stToolbarActions"],
        [data-testid="manage-app-button"],
        .stDeployButton,
        .stAppToolbar,
        .stDecoration,
        footer,
        footer[data-testid="stFooter"],
        .stApp > footer,
        a[href*="github.com/streamlit"],
        a[href*="streamlit.io"],
        a[href*="share.streamlit.io"],
        div[data-testid="stToolbar"] button,
        section[data-testid="stSidebar"] [data-testid="stLogoSpacer"] {
          display: none !important;
          visibility: hidden !important;
          height: 0 !important;
          min-height: 0 !important;
          max-height: 0 !important;
          margin: 0 !important;
          padding: 0 !important;
          opacity: 0 !important;
          pointer-events: none !important;
          overflow: hidden !important;
        }

        /* Reclaim the top chrome strip for a full-bleed executive canvas */
        .stApp,
        [data-testid="stAppViewContainer"],
        .main .block-container {
          padding-top: max(12px, env(safe-area-inset-top, 0px)) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# 🔒 EXECUTIVE SECURITY GATE
# ==========================================
def _executive_access_key() -> str:
    """Prefer Streamlit secrets; fall back to demo default for local / Cloud bootstrap."""
    try:
        key = st.secrets.get("EXECUTIVE_ACCESS_KEY", "")
    except Exception:
        key = ""
    return str(key or "NZ-ACC-2026")


def check_password():
    """Returns `True` if the user has entered the correct executive passcode."""

    def password_entered():
        if st.session_state["password_input"] == _executive_access_key():
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]  # Don't keep passcode in memory
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🏛️ NZ ACC Sovereign Orchestration Engine")
        st.subheader("🔒 Executive Security Gate")
        st.text_input(
            "Enter Access Key to unlock command surface:",
            type="password",
            on_change=password_entered,
            key="password_input",
        )
        return False

    elif not st.session_state["password_correct"]:
        st.title("🏛️ NZ ACC Sovereign Orchestration Engine")
        st.subheader("🔒 Executive Security Gate")
        st.text_input(
            "Enter Access Key to unlock command surface:",
            type="password",
            on_change=password_entered,
            key="password_input",
        )
        st.error("⛔ Invalid Access Key. Access Denied.")
        return False

    return True


# Block execution of the rest of the app until password is correct
if not check_password():
    st.stop()
# ==========================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    .reportview-container, .main {
        background-color: #0b0f17;
        color: #f8fafc;
        font-family: "IBM Plex Sans", sans-serif;
    }
    .stApp {
        background-color: #0b0f17;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    /* Industry Metric Card Highlights — executive dark viewport */
    .metric-box {
        background-color: #131d2a;
        border: 1px solid #1e293b;
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
        color: #2f81f7;
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
       PRIVATE CHROME REMOVAL (reinforced after auth unlock)
       Header bar · Share · hamburger · GitHub link · footer
       ============================================================ */
    #MainMenu,
    #MainMenu > button,
    header[data-testid="stHeader"],
    header.stAppHeader,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stAppDeployButton"],
    [data-testid="stDeployButton"],
    [data-testid="baseButton-header"],
    [data-testid="baseButton-headerNoPadding"],
    [data-testid="stBaseButton-header"],
    [data-testid="stBaseButton-headerNoPadding"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"],
    [data-testid="stToolbarActions"],
    [data-testid="manage-app-button"],
    .stDeployButton,
    .stAppToolbar,
    .stDecoration,
    footer,
    footer[data-testid="stFooter"],
    .stApp > footer,
    a[href*="github.com/streamlit"],
    a[href*="streamlit.io"],
    a[href*="share.streamlit.io"] {
      display: none !important;
      visibility: hidden !important;
      height: 0 !important;
      min-height: 0 !important;
      max-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      opacity: 0 !important;
      pointer-events: none !important;
      overflow: hidden !important;
    }

    /* ============================================================
       iPadOS / mobile — safe-area padding (no Streamlit chrome)
       ============================================================ */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
      padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
      box-sizing: border-box !important;
    }

    [data-testid="stSidebarHeader"] {
      padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
      margin-top: max(8px, env(safe-area-inset-top, 0px)) !important;
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
      border-bottom: 1px solid #1e293b;
      background: #0b0f17;
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
      border: 1px solid #1e293b;
      background: #131d2a;
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
      color: #2f81f7;
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
      background: #0b0f17;
      border: 1px solid #1e293b;
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
      background: #131d2a;
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

    /* Tablet / mobile: hard floor — custom nav clear of iPadOS chrome */
    @media (max-width: 1024px) {
      .ipad-top-nav {
        margin-top: max(40px, calc(env(safe-area-inset-top, 0px) + 16px)) !important;
        margin-left: max(40px, calc(env(safe-area-inset-left, 0px) + 16px)) !important;
        padding-top: max(16px, env(safe-area-inset-top, 0px)) !important;
      }

      .ipad-top-nav .nav-mark {
        margin-top: 0 !important;
        margin-left: 0 !important;
        position: relative !important;
        top: auto !important;
        left: auto !important;
        min-width: 44px !important;
        min-height: 44px !important;
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

# Dedicated top navigation — real page links (host multipage nav is disabled
# for private iPad chrome, so without these links pages look "missing").
render_surface_page_links(active="home")

# viewport-fit=cover so env(safe-area-inset-*) resolves on iPadOS Safari
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    """,
    unsafe_allow_html=True,
)

# --- MASTER CLAIMS DATABASE CORE ---
MINISTER_ROLE = "Cabinet Minister (Executive Authority)"
SCHEME_DIRECTOR = "Scheme Director (GM)"
CLAIMS_OFFICER = "Claims Officer / Analyst"
REVIEWING_SPECIALIST = "Reviewing Specialist"
FINANCE_LEGAL_SPECIALIST = "Finance, Actuarial & Legal Specialist"
ACTUARY_COUNSEL = "Actuary / Counsel"
FINANCE_LEGAL_ROLES = frozenset({FINANCE_LEGAL_SPECIALIST, ACTUARY_COUNSEL})

# Proprietary mitigation bands — numeric weights stay server-side (IP lockdown).
IP_MITIGATION_BANDS: dict[str, int] = {
    "Nominal Guardrail": 0,
    "Measured Stewardship": 10,
    "Standard Crown Floor": 15,
    "Elevated Containment": 25,
    "Maximum Statutory Ceiling": 50,
}
IP_BAND_LABELS: tuple[str, ...] = tuple(IP_MITIGATION_BANDS.keys())
DEFAULT_IP_BAND = "Standard Crown Floor"

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


def render_abstracted_sidebar_ip() -> tuple[str, int]:
    """IP lockdown: select_slider with abstracted bands — no raw % on glass."""
    st.markdown("### SCHEME MANDATE INJECTION")
    st.caption(
        "Proprietary stewardship band control · explicit arithmetic withheld from glass"
    )
    band = st.select_slider(
        "Enforce Liability Mitigation Floor (Abstracted Stewardship Band)",
        options=list(IP_BAND_LABELS),
        value=DEFAULT_IP_BAND,
        key="ip_mitigation_band_slider",
    )
    internal_floor = int(IP_MITIGATION_BANDS[band])
    st.session_state["ip_mitigation_band"] = band
    st.session_state["ip_mitigation_floor_internal"] = internal_floor
    safe_band = html.escape(sanitize_plain_text(band, max_chars=64), quote=True)
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;'
        f'color:#8b949e;">Active stewardship band: '
        f'<span style="color:#c084fc;font-weight:700;">{safe_band}</span>'
        f" · proprietary weight sealed</div>",
        unsafe_allow_html=True,
    )
    return band, internal_floor


def apply_finance_legal_action(claim_id: str, title: str, details: str) -> None:
    """Persist Department #4 execution deck confirmation into session state."""
    st.session_state[f"finance_legal_action_{claim_id}"] = {
        "title": sanitize_plain_text(title, max_chars=160),
        "details": sanitize_plain_text(details, max_chars=320),
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
    }


def render_finance_legal_view() -> None:
    """Department #4: Finance, Actuarial & Legal Specialist View.

    Isolates commutation, reserve, counsel briefing, and actuarial vault
    workflows. Dynamic strings pass through html.escape (PR #24).
    """
    st.markdown("## Finance, Actuarial & Legal Command Sector")
    st.caption(
        "Role-Gated Interface: Actuaries & Counsel | "
        "Focus: Commutation · Reserve · Dispute · Vault Seal"
    )
    st.divider()

    finance_case_options: dict[str, dict[str, str]] = {
        "AAT-Claimant-Zeta-2026": {
            "subject": "Claimant-Zeta · Knee construct",
            "reserve_posture": "Cabinet Threshold Exceeded · Long-tail watch",
            "commutation_band": "Abstracted Crown Settlement Envelope",
            "counsel_status": "Dispute matrix primed · PII tokenized",
            "actuary_owner": "Actuarial Pod #AL-04",
        },
        "AAT-Claimant-Delta-2026": {
            "subject": "Claimant-Delta · Shoulder pathway",
            "reserve_posture": "Ministerial Escalation Required",
            "commutation_band": "Measured Stewardship Settlement Window",
            "counsel_status": "Counsel brief draft pending seal",
            "actuary_owner": "Actuarial Pod #AL-04",
        },
    }

    selected_id = st.selectbox(
        "Select Finance / Legal Case File:",
        list(finance_case_options.keys()),
        index=0,
        key="finance_legal_case_selector",
    )
    case = finance_case_options[selected_id]
    action_key = f"finance_legal_action_{selected_id}"
    if action_key not in st.session_state:
        st.session_state[action_key] = None

    safe_subject = html.escape(
        sanitize_plain_text(case["subject"], max_chars=80), quote=True
    )
    safe_reserve = html.escape(
        sanitize_plain_text(case["reserve_posture"], max_chars=120), quote=True
    )
    safe_commutation = html.escape(
        sanitize_plain_text(case["commutation_band"], max_chars=120), quote=True
    )
    safe_counsel = html.escape(
        sanitize_plain_text(case["counsel_status"], max_chars=120), quote=True
    )
    safe_owner = html.escape(
        sanitize_plain_text(case["actuary_owner"], max_chars=64), quote=True
    )
    safe_token = html.escape(
        sanitize_claim_token(selected_id), quote=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Subject & Ownership")
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-label">Claim Token</div>'
            f'<div style="color:#ffffff;font-weight:700;">{safe_token}</div>'
            f'<div class="metric-label" style="margin-top:0.55rem;">Subject</div>'
            f'<div style="color:#e2e8f0;">{safe_subject}</div>'
            f'<div class="metric-label" style="margin-top:0.55rem;">Actuarial Owner</div>'
            f'<div style="color:#c084fc;">{safe_owner}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown("### Reserve Posture")
        st.markdown(
            f'<div class="metric-box" style="border-left:3px solid #eab308;">'
            f'<div class="metric-label">Statutory Reserve Posture</div>'
            f'<div style="color:#fde68a;font-weight:700;">{safe_reserve}</div>'
            f'<div class="metric-label" style="margin-top:0.55rem;">Commutation Envelope</div>'
            f'<div style="color:#e2e8f0;">{safe_commutation}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown("### Counsel Status")
        st.markdown(
            f'<div class="metric-box" style="border-left:3px solid #a855f7;">'
            f'<div class="metric-label">Legal Channel</div>'
            f'<div style="color:#e9d5ff;">{safe_counsel}</div>'
            f'<div class="metric-label" style="margin-top:0.55rem;">IP Posture</div>'
            f'<div style="color:#8b949e;">Proprietary floor weights sealed · glass-safe</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    action_state = st.session_state.get(action_key)
    if action_state:
        safe_title = html.escape(
            sanitize_plain_text(action_state["title"], max_chars=160), quote=True
        )
        safe_details = html.escape(
            sanitize_plain_text(action_state["details"], max_chars=320), quote=True
        )
        safe_ts = html.escape(
            sanitize_plain_text(action_state.get("ts", ""), max_chars=40), quote=True
        )
        st.markdown(
            f"""
            <div style="margin:0.25rem 0 0.85rem; padding:1rem 1.15rem;
                        background:linear-gradient(135deg,#10241a 0%,#14532d 55%,#0f1f17 100%);
                        border:1px solid #16a34a; border-radius:6px;">
              <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
                          letter-spacing:0.08em; text-transform:uppercase;
                          color:#86efac; margin-bottom:0.35rem;">
                Finance / Legal Action Executed · {safe_ts}
              </div>
              <div style="font-size:1.05rem; font-weight:700; color:#ecfdf5;
                          margin-bottom:0.35rem;">{safe_title}</div>
              <div style="color:#d1fae5; font-size:0.92rem; line-height:1.45;">
                • {safe_details}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.success(
            "**FINANCE / LEGAL ACTION EXECUTED:** "
            + sanitize_for_markdown(action_state["title"], max_chars=160)
        )
        st.divider()

    st.markdown("### Finance & Legal Execution Deck")
    st.caption(
        "Tap a trigger to update session state and confirm the statutory action "
        "live on this device."
    )
    b1, b2 = st.columns(2)
    with b1:
        st.button(
            "1. Authorize Crown Commutation Settlement Review",
            use_container_width=True,
            type="primary",
            key=f"fl_commutation_{selected_id}",
            on_click=apply_finance_legal_action,
            args=(
                selected_id,
                "Crown Commutation Settlement Review Authorized",
                "Abstracted settlement envelope staged for actuarial seal. "
                "Explicit arithmetic withheld from glass (IP lockdown).",
            ),
        )
        st.button(
            "2. Issue Statutory Liability Reserve Adjustment",
            use_container_width=True,
            key=f"fl_reserve_{selected_id}",
            on_click=apply_finance_legal_action,
            args=(
                selected_id,
                "Statutory Liability Reserve Adjustment Issued",
                "Reserve posture recalibrated under abstracted stewardship band. "
                "Ledger delta sealed to Crown vault.",
            ),
        )
    with b2:
        st.button(
            "3. Flag File for Legal Dispute / Counsel Brief",
            use_container_width=True,
            key=f"fl_counsel_{selected_id}",
            on_click=apply_finance_legal_action,
            args=(
                selected_id,
                "Legal Dispute / Counsel Brief Flagged",
                "Tokenized counsel brief packet queued. Individual PII remains "
                "masked pending statutory unmask authority.",
            ),
        )
        st.button(
            "4. Seal Actuarial Projection to Crown Vault",
            use_container_width=True,
            key=f"fl_vault_{selected_id}",
            on_click=apply_finance_legal_action,
            args=(
                selected_id,
                "Actuarial Projection Sealed to Crown Vault",
                "36-month liability projection hash committed. Provenance receipt "
                "written to session vault for Cabinet pouch.",
            ),
        )


def render_executive_command_profile() -> None:
    """Avatar / profile strip plus audio briefing and command overview video."""
    col1, col2 = st.columns([1, 4])
    with col1:
        if AVATAR_PATH.is_file():
            st.image(str(AVATAR_PATH), width=100)
        else:
            st.caption("Avatar asset missing (`public/avatar.png`).")
    with col2:
        st.markdown("### Executive Command Profile")
        st.caption("Active Duty · NZ AAT Sovereign Orchestration Hub")

    st.subheader("Audio Briefing & Command Video")
    if BRIEFING_AUDIO_PATH.is_file():
        st.audio(str(BRIEFING_AUDIO_PATH), format="audio/mp3")
    else:
        st.caption("Audio briefing missing (`public/briefing.mp3`).")
    if COMMAND_VIDEO_PATH.is_file():
        st.video(str(COMMAND_VIDEO_PATH))
    else:
        st.caption("Command video missing (`public/command_overview.mp4`).")


def render_gemini_notebook_sidebar(*, role: str, claim_token: str) -> None:
    """Gemini Notebook Manifest — Note #01 generated from active role + claim."""
    safe_role = html.escape(sanitize_plain_text(role, max_chars=80), quote=True)
    safe_token = html.escape(sanitize_claim_token(claim_token), quote=True)
    ts = html.escape(
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), quote=True
    )
    role_focus = {
        MINISTER_ROLE: "Cabinet statutory oversight & BIM escalation posture",
        SCHEME_DIRECTOR: "Scheme CapEx stewardship & pathway governance",
        CLAIMS_OFFICER: "Milestone SLA execution & claimant engagement",
        REVIEWING_SPECIALIST: "Clinical telemetry variance & IME compliance",
        FINANCE_LEGAL_SPECIALIST: "Commutation, reserve, and counsel brief matrix",
        ACTUARY_COUNSEL: "Actuarial projection seal & dispute channel readiness",
    }
    focus = html.escape(
        sanitize_plain_text(
            role_focus.get(role, "General scheme operational brief"),
            max_chars=160,
        ),
        quote=True,
    )
    st.markdown("---")
    st.markdown("### Gemini Notebook Manifest")
    st.markdown(
        f"""
        <div style="background:#12161e; border:1px solid #30363d; border-left:3px solid #a855f7;
                    border-radius:6px; padding:0.85rem 0.95rem; margin-bottom:0.5rem;">
          <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
                      letter-spacing:0.08em; text-transform:uppercase; color:#c084fc;
                      font-weight:700; margin-bottom:0.4rem;">
            Note #01 · Role-Dynamic Operational Brief
          </div>
          <div style="font-size:0.82rem; color:#8b949e; margin-bottom:0.35rem;">
            Timestamp: <span style="color:#e2e8f0;">{ts}</span>
          </div>
          <div style="font-size:0.88rem; color:#f8fafc; line-height:1.45;">
            <strong>Active Role:</strong> {safe_role}<br/>
            <strong>Claim Token:</strong> {safe_token}<br/>
            <strong>Focus Vector:</strong> {focus}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button(
        "Open Live Gemini Notebook Manifest",
        GEMINI_NOTEBOOK_URL,
        use_container_width=True,
    )
    st.caption("Note #01 auto-generated · strings html.escape'd (PR #24)")


def render_gemini_intelligence_notebook() -> None:
    """Main-dashboard Gemini Intelligence Notebook & Manifest (link + embed)."""
    st.markdown("---")
    st.subheader("Gemini Intelligence Notebook & Manifest")
    st.link_button(
        "Open Live Gemini Notebook Manifest",
        GEMINI_NOTEBOOK_URL,
        use_container_width=True,
    )
    components.iframe(GEMINI_NOTEBOOK_URL, height=500, scrolling=True)


def compute_actuarial_inaction_threat_matrix(
    *,
    portfolio_spend: float,
    critical_subjects: int,
) -> dict[str, Any]:
    """36-month Controlled Upgrade vs Runaway Inaction liability projection (NZD)."""
    base = max(float(portfolio_spend), 150_000.0)
    # Critical drift subjects amplify runaway exposure without exploding the narrative band.
    drift_scale = 1.0 + (max(int(critical_subjects), 0) * 0.02)
    cost_rows = (
        ("Maintenance Fees", 0.42, 0.78),
        ("Failure Downtime", 0.18, 0.52),
        ("Security Breach Vulnerabilities", 0.12, 0.44),
        ("Productivity Drag", 0.22, 0.58),
    )
    rows: list[dict[str, Any]] = []
    controlled_total = 0.0
    runaway_total = 0.0
    for label, controlled_w, runaway_w in cost_rows:
        controlled = round(base * controlled_w, 2)
        runaway = round(base * runaway_w * drift_scale, 2)
        variance = round(runaway - controlled, 2)
        controlled_total += controlled
        runaway_total += runaway
        rows.append(
            {
                "dimension": label,
                "controlled": controlled,
                "runaway": runaway,
                "variance": variance,
            }
        )
    sovereign_variance_total = round(runaway_total - controlled_total, 2)
    fiduciary_pct = (
        round((sovereign_variance_total / controlled_total) * 100.0, 1)
        if controlled_total > 0
        else 0.0
    )
    return {
        "horizon_months": 36,
        "rows": rows,
        "controlled_total": round(controlled_total, 2),
        "runaway_total": round(runaway_total, 2),
        "sovereign_variance_total": sovereign_variance_total,
        "fiduciary_pct": fiduciary_pct,
    }


def render_actuarial_inaction_threat_matrix(forecast: dict[str, Any]) -> None:
    """High-contrast side-by-side forecast table + fiduciary warning (PR #24 safe)."""
    horizon = sanitize_html_text(int(forecast["horizon_months"]), max_chars=8)
    row_html: list[str] = []
    for row in forecast["rows"]:
        dim = sanitize_html_text(row["dimension"], max_chars=MAX_FIELD_CHARS)
        controlled = sanitize_html_text(f"{row['controlled']:,.0f}", max_chars=32)
        runaway = sanitize_html_text(f"{row['runaway']:,.0f}", max_chars=32)
        variance = sanitize_html_text(f"{row['variance']:,.0f}", max_chars=32)
        row_html.append(
            "<tr style='border-bottom:1px solid #30363d;'>"
            f"<td style='padding:0.65rem 0.55rem; color:#f8fafc; font-weight:600;'>{dim}</td>"
            f"<td style='padding:0.65rem 0.55rem; color:#e2e8f0; text-align:right;'>"
            f"${controlled}</td>"
            f"<td style='padding:0.65rem 0.55rem; color:#e2e8f0; text-align:right;'>"
            f"${runaway}</td>"
            f"<td style='padding:0.65rem 0.55rem; text-align:right;'>"
            f"<strong style='color:#ef4444; font-size:1.05rem;'>${variance}</strong></td>"
            "</tr>"
        )

    safe_controlled_total = sanitize_html_text(
        f"{forecast['controlled_total']:,.0f}", max_chars=32
    )
    safe_runaway_total = sanitize_html_text(
        f"{forecast['runaway_total']:,.0f}", max_chars=32
    )
    safe_variance_total = sanitize_html_text(
        f"{forecast['sovereign_variance_total']:,.0f}", max_chars=32
    )
    safe_fiduciary_pct = sanitize_html_text(
        f"{forecast['fiduciary_pct']:.1f}", max_chars=16
    )

    table_markup = f"""
<div class="metric-box" style="border-left:4px solid #ef4444; padding:1.25rem;">
  <div class="metric-label" style="color:#ef4444;">ACTUARIAL INACTION THREAT MATRIX · {horizon}-MONTH LIABILITY PROJECTION</div>
  <div style="color:#8b949e; font-size:0.88rem; margin:0.35rem 0 0.85rem;">
    Controlled Upgrade Modernization Engine vs Runaway Inaction — NZD sovereign exposure
  </div>
  <div style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; font-size:0.92rem; min-width:560px;">
      <thead>
        <tr style="border-bottom:2px solid #484f58; text-align:left;">
          <th style="padding:0.55rem; color:#8b949e; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; text-transform:uppercase;">Cost Dimension</th>
          <th style="padding:0.55rem; color:#10b981; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; text-transform:uppercase; text-align:right;">Controlled Upgrade</th>
          <th style="padding:0.55rem; color:#f59e0b; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; text-transform:uppercase; text-align:right;">Runaway Inaction</th>
          <th style="padding:0.55rem; color:#ef4444; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; text-transform:uppercase; text-align:right;">Sovereign Variance</th>
        </tr>
      </thead>
      <tbody>
        {''.join(row_html)}
        <tr style="background:#161b22;">
          <td style="padding:0.75rem 0.55rem; color:#ffffff; font-weight:700;">36-Month Aggregate</td>
          <td style="padding:0.75rem 0.55rem; color:#10b981; font-weight:700; text-align:right;">${safe_controlled_total}</td>
          <td style="padding:0.75rem 0.55rem; color:#f59e0b; font-weight:700; text-align:right;">${safe_runaway_total}</td>
          <td style="padding:0.75rem 0.55rem; text-align:right;">
            <strong style="color:#ef4444; font-size:1.15rem;">${safe_variance_total}</strong>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
"""
    st.markdown(table_markup, unsafe_allow_html=True)

    warning_markup = f"""
<blockquote style="
  margin:1rem 0 0;
  padding:1.15rem 1.25rem;
  background:linear-gradient(135deg,#1c1012 0%,#3f1215 55%,#1a0e10 100%);
  border-left:6px solid #dc2626;
  border:1px solid #7f1d1d;
  border-left-width:6px;
  border-radius:6px;
  color:#fecaca;
  font-size:1.02rem;
  line-height:1.55;
">
  <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; letter-spacing:0.08em;
              text-transform:uppercase; color:#f87171; font-weight:700; margin-bottom:0.45rem;">
    Fiduciary Warning · Executive Callout
  </div>
  <strong style="color:#ffffff;">Fiduciary Warning:</strong>
  Maintaining the status quo locks in an unmitigated liability exposure evaluated at
  <strong style="color:#ef4444; font-size:1.15rem;">{safe_fiduciary_pct}%</strong>
  higher than the modern cloud deployment pathway.
  Sovereign variance locked at
  <strong style="color:#ef4444;">${safe_variance_total} NZD</strong>
  across the {horizon}-month runway.
</blockquote>
"""
    st.markdown(warning_markup, unsafe_allow_html=True)


def compute_nationwide_scalability_matrix(
    *,
    pilot_cohort_size: int,
    portfolio_spend: float,
    critical_subjects: int,
    performance_index: float = 85.9,
) -> dict[str, Any]:
    """Pilot baseline vs nationwide geographic expansion value projection."""
    pilot_n = max(int(pilot_cohort_size), 1)
    # NZ ACC-scale population vector (full geographic framework).
    nationwide_n = 142_000
    scale_factor = nationwide_n / pilot_n
    spend = max(float(portfolio_spend), 1.0)
    precision_pilot = min(92.0, 74.0 + (max(int(critical_subjects), 0) * 0.55))
    precision_nation = min(97.5, precision_pilot + 4.8)
    ingest_pilot = round(12.0 + (pilot_n * 0.35), 1)  # records / hour
    ingest_nation = round(ingest_pilot * min(scale_factor * 0.18, 85.0), 1)
    alignment_pilot = round(float(performance_index), 1)
    alignment_nation = round(min(96.5, alignment_pilot + 7.4), 1)
    value_pilot = round(spend * 1.15, 2)
    # Unit economics × full population with scale-efficiency haircut (not linear spend blow-up).
    unit_capture = (spend / pilot_n) * 0.68
    value_nation = round(unit_capture * nationwide_n, 2)
    alignment_gain_pp = round(alignment_nation - alignment_pilot, 1)
    rows = [
        {
            "dimension": "Monitored Cohort Size",
            "pilot": f"{pilot_n:,}",
            "nationwide": f"{nationwide_n:,}",
            "unit": "subjects",
        },
        {
            "dimension": "At-Risk Identification Precision",
            "pilot": f"{precision_pilot:.1f}%",
            "nationwide": f"{precision_nation:.1f}%",
            "unit": "precision",
        },
        {
            "dimension": "Ingestion Velocity",
            "pilot": f"{ingest_pilot:,.1f}/hr",
            "nationwide": f"{ingest_nation:,.1f}/hr",
            "unit": "velocity",
        },
        {
            "dimension": "Functional Alignment Improvement",
            "pilot": f"{alignment_pilot:.1f}%",
            "nationwide": f"{alignment_nation:.1f}%",
            "unit": "alignment",
        },
        {
            "dimension": "Total Captured Financial Value",
            "pilot": f"${value_pilot:,.0f} NZD",
            "nationwide": f"${value_nation:,.0f} NZD",
            "unit": "value",
        },
    ]
    return {
        "rows": rows,
        "scale_factor": round(scale_factor, 1),
        "value_pilot": value_pilot,
        "value_nation": value_nation,
        "alignment_gain_pp": alignment_gain_pp,
    }


def render_nationwide_scalability_matrix(matrix: dict[str, Any]) -> None:
    """High-contrast pilot vs nationwide ledger + purple transformational callout."""
    row_html: list[str] = []
    for row in matrix["rows"]:
        dim = sanitize_html_text(row["dimension"], max_chars=MAX_FIELD_CHARS)
        pilot = sanitize_html_text(row["pilot"], max_chars=48)
        nationwide = sanitize_html_text(row["nationwide"], max_chars=48)
        row_html.append(
            "<tr style='border-bottom:1px solid #30363d;'>"
            f"<td style='padding:0.65rem 0.55rem; color:#f8fafc; font-weight:600;'>{dim}</td>"
            f"<td style='padding:0.65rem 0.55rem; color:#e2e8f0; text-align:right;'>{pilot}</td>"
            f"<td style='padding:0.65rem 0.55rem; color:#c084fc; font-weight:700; text-align:right;'>"
            f"{nationwide}</td>"
            "</tr>"
        )

    safe_scale = sanitize_html_text(f"{matrix['scale_factor']:.1f}", max_chars=16)
    safe_gain = sanitize_html_text(f"{matrix['alignment_gain_pp']:.1f}", max_chars=16)
    safe_nation_value = sanitize_html_text(
        f"{matrix['value_nation']:,.0f}", max_chars=32
    )

    table_markup = f"""
<div class="metric-box" style="border-left:4px solid #a855f7; padding:1.25rem;">
  <div class="metric-label" style="color:#c084fc;">
    NATIONWIDE MACROECONOMIC SCALABILITY &amp; VALUE PROJECTION MATRIX
  </div>
  <div style="color:#8b949e; font-size:0.88rem; margin:0.35rem 0 0.85rem;">
    Current Pilot Phase Baseline vs Projected Nationwide Expansion · geographic scale factor
    <strong style="color:#e9d5ff;">{safe_scale}×</strong>
  </div>
  <div style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; font-size:0.92rem; min-width:560px;">
      <thead>
        <tr style="border-bottom:2px solid #484f58; text-align:left;">
          <th style="padding:0.55rem; color:#8b949e; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; text-transform:uppercase;">Performance Vector</th>
          <th style="padding:0.55rem; color:#94a3b8; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; text-transform:uppercase; text-align:right;">Current Pilot Phase Baseline</th>
          <th style="padding:0.55rem; color:#c084fc; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; text-transform:uppercase; text-align:right;">Projected Nationwide Expansion</th>
        </tr>
      </thead>
      <tbody>
        {''.join(row_html)}
      </tbody>
    </table>
  </div>
</div>
"""
    st.markdown(table_markup, unsafe_allow_html=True)

    callout_markup = f"""
<div style="
  margin:1rem 0 0;
  padding:1.2rem 1.3rem;
  background:linear-gradient(135deg,#18141c 0%,#2a1540 55%,#16101f 100%);
  border:2px solid #a855f7;
  border-radius:8px;
  box-shadow:0 0 0 1px #6b21a8 inset;
  color:#e9d5ff;
  font-size:1.02rem;
  line-height:1.55;
">
  <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; letter-spacing:0.08em;
              text-transform:uppercase; color:#c084fc; font-weight:700; margin-bottom:0.5rem;">
    Transformational Impact Callout · Sovereign Scaling Validated
  </div>
  <strong style="color:#ffffff;">Core Strategy Validated:</strong>
  The observed performance acceleration within the primary pilot tranche confirms a
  transformational upgrade in systemic efficiency when scaled across the complete
  geographic framework.
  <div style="margin-top:0.65rem; color:#d8b4fe; font-size:0.92rem;">
    Captured nationwide financial value projected at
    <strong style="color:#f5d0fe;">${safe_nation_value} NZD</strong>
    · geographic scale
    <strong style="color:#f5d0fe;">{safe_scale}×</strong>
    · functional alignment gain
    <strong style="color:#f5d0fe;">+{safe_gain} pp</strong>.
  </div>
</div>
"""
    st.markdown(callout_markup, unsafe_allow_html=True)


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

    safe_anatomy_cohort = sanitize_html_text(anatomy, max_chars=MAX_FIELD_CHARS)
    safe_role_cohort = sanitize_html_text(role, max_chars=64)
    st.markdown(
        f"""
        <div class="metric-box" style="border-left: 4px solid #ef4444;">
          <div class="metric-label" style="color:#ef4444;">COHORT ANALYSIS</div>
          <div style="color:#ffffff; font-size:1.25rem; font-weight:700; margin-bottom:0.55rem;">
            Cohort Analysis: {safe_anatomy_cohort} — {n_critical} Critical Drift Subjects
          </div>
          <div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:0.75rem;">
            <div>
              <div class="metric-label">Average Days Elapsed</div>
              <div class="metric-value-silver" style="font-size:1.45rem;">{sanitize_html_text(f"{avg_days:.1f}", max_chars=16)}</div>
            </div>
            <div>
              <div class="metric-label">Cumulative Financial Risk (NZD)</div>
              <div class="metric-value-crimson" style="font-size:1.45rem;">${sanitize_html_text(f"{cumulative_risk:,.0f}", max_chars=32)}</div>
            </div>
            <div>
              <div class="metric-label">Primary Drift Velocity</div>
              <div class="metric-value-silver" style="font-size:1.45rem;">{sanitize_html_text(f"{primary_velocity:.2f}", max_chars=16)}×</div>
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
            (
                f"<li><strong>{sanitize_html_text(cause, max_chars=120)}</strong> — "
                f"signal weight {sanitize_html_text(weight, max_chars=16)}"
                + (
                    f" · “{sanitize_html_text(snippet, max_chars=180)}…”"
                    if snippet
                    else ""
                )
                + "</li>"
            )
            for cause, weight, snippet in causes
        )
        st.markdown(
            f"""
            <div class="metric-box" style="border-left: 4px solid #a855f7;">
              <div class="metric-label" style="color:#c084fc;">NLP ROOT-CAUSE SUMMARIZER</div>
              <div style="color:#8b949e; font-size:0.88rem; margin-bottom:0.45rem;">
                Scanned {len(focus)} cohort NLP Ingest field(s) · Role: {safe_role_cohort}
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


def _append_identity_audit(actor: str, action: str, token: str, native_id: str) -> None:
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


def _sector_label(key: str) -> str:
    """Sidebar display label for a sector book key."""
    return str(get_sector_book(key).get("display_name", key))


# --- SIDEBAR: GOVERNANCE LAYER FILTERS ---
with st.sidebar:
    render_sidebar_surface_links(active="home")
    st.markdown("---")
    st.markdown("### SECTOR BOOK")
    if "active_sector_book" not in st.session_state:
        st.session_state.active_sector_book = DEFAULT_SECTOR_KEY
    sector_key = st.selectbox(
        "Active Sector Book",
        options=sector_book_options(),
        format_func=_sector_label,
        key="active_sector_book",
    )
    active_sector = get_sector_book(sector_key)
    SCHEME_CRITICAL_SUBJECTS = int(active_sector["critical_subjects"])
    st.markdown("---")
    st.markdown("### AAT SCHEME GOVERNANCE")
    role = st.selectbox(
        "Active User Role Matrix",
        [
            MINISTER_ROLE,
            SCHEME_DIRECTOR,
            CLAIMS_OFFICER,
            REVIEWING_SPECIALIST,
            FINANCE_LEGAL_SPECIALIST,
            ACTUARY_COUNSEL,
        ],
        key="active_user_role_matrix",
    )
    statutory_briefing_mode = role == MINISTER_ROLE
    finance_legal_mode = role in FINANCE_LEGAL_ROLES
    # GM + caseworkers/specialists may unmask; Cabinet Minister + Dept #4 retain aliases
    can_unmask_identity = role in {
        SCHEME_DIRECTOR,
        CLAIMS_OFFICER,
        REVIEWING_SPECIALIST,
    }
    st.markdown("---")
    if finance_legal_mode:
        st.markdown("### FINANCE / ACTUARIAL / LEGAL MODE")
        st.info(
            "Isolated Department #4 surface — Cabinet chrome suppressed. "
            "Proprietary mitigation arithmetic sealed behind IP lockdown."
        )
        ip_band, cap_floor = render_abstracted_sidebar_ip()
        st.caption(
            f"Active role: {sanitize_for_markdown(role, max_chars=80)} · "
            "Commutation · Reserve · Counsel · Vault"
        )
    else:
        ip_band, cap_floor = render_abstracted_sidebar_ip()
        performance_mandate = st.text_input(
            "Disseminate Performance Mandate",
            placeholder="e.g., Accelerate Pathway Interventions",
            max_chars=MAX_MANDATE_CHARS,
        )
        if statutory_briefing_mode:
            st.info(
                "Statutory Briefing Mode active — Crown Entity Act compliance view."
            )
            st.caption(
                "Aggregated cohort & root-cause analysis permitted. "
                "Individual PII / Native ACC Claim ID unmasking restricted."
            )
        st.caption(sanitize_for_markdown(active_sector["sidebar_caption"], max_chars=120))
    claim_token_for_note = sanitize_claim_token(
        st.session_state.get("audit_view_selection", GLOBAL_VIEW)
    )
    if claim_token_for_note == GLOBAL_VIEW:
        claim_token_for_note = "AAT-Claimant-Delta-2026"
    render_gemini_notebook_sidebar(role=role, claim_token=claim_token_for_note)
    if st.session_state.identity_audit_log and not finance_legal_mode:
        with st.expander("Identity Unmask Audit Log", expanded=False):
            for entry in reversed(st.session_state.identity_audit_log[-8:]):
                st.text(
                    f"{entry['ts']} · {entry['actor']} · {entry['action']} · "
                    f"{entry['token']} → {entry['native_id']}"
                )

# Department #4 — Finance / Actuarial / Legal isolated surface
if finance_legal_mode:
    render_sector_header(active_sector)
    st.markdown(
        "<p class='statutory-meta'>"
        "Department #4 Surface · Finance, Actuarial &amp; Legal Channel</p>",
        unsafe_allow_html=True,
    )
    render_finance_legal_view()
    st.stop()

# --- MAIN PERFORMANCE DASHBOARD TITLE ---
render_sector_header(active_sector)
if statutory_briefing_mode:
    st.markdown(
        '<div class="briefing-mode-chip">STATUTORY BRIEFING MODE · CABINET EXECUTIVE OVERLAY</div>',
        unsafe_allow_html=True,
    )

# --- AVATAR / PROFILE DISPLAY + AUDIO BRIEFING & VIDEO DEMO ---
render_executive_command_profile()
st.markdown("---")

# --- CABINET MINISTER DIRECTIVE PANEL (top-down statutory override controls) ---
if "ministerial_override" not in st.session_state:
    st.session_state.ministerial_override = False
if role == MINISTER_ROLE:
    st.markdown(
        """
        <div style="background-color:#1c1112; border:1px solid #dc2626; padding:1.2rem;
                    border-radius:6px; margin-bottom:1.5rem;">
          <div style="font-family:'IBM Plex Mono', monospace; font-size:0.75rem; color:#ef4444;
                      font-weight:700; letter-spacing:0.05em; text-transform:uppercase;">
            STATUTORY CABINET AUTHORITY PORTAL
          </div>
          <h3 style="margin-top:0.2rem; margin-bottom:0.5rem; color:#ffffff;">
            Ministerial Executive Directive Matrix
          </h3>
          <p style="color:#8b949e; font-size:0.88rem; margin-bottom:0;">
            As the Crown Executive, your input bypasses standard inter-departmental friction.
            Activating systemic overrides will force institutional data reconciliation and
            re-allocate capital reserves immediately.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_min1, col_min2 = st.columns(2)
    with col_min1:
        st.session_state.ministerial_override = st.checkbox(
            "Force Cross-Agency Data Integration Share Mandate (Bypass Bureaucratic Silos)",
            value=st.session_state.ministerial_override,
            key="cabinet_force_cross_agency",
        )
    with col_min2:
        st.selectbox(
            "Execute Macro Statutory Intervention",
            [
                "Maintain Standard Operations runway",
                "Emergency CapEx Liquidity Release (Settle P0 Drift Blocks In Bulk)",
                "Direct MSD to Open 500 Immediate Training Cert Slots",
                "Fast-Track Crown Clinical Network Triage Mandate",
            ],
            key="cabinet_macro_intervention",
        )
    st.markdown("---")

# --- WHAT / WHERE / WHEN OPERATIONAL BRIDGE (sector-driven) ---
render_operational_bridge(active_sector)

# --- Ministerial Escalation Banner (between operational bridge and Audit Command) ---
render_operational_bridge_banner(active_sector)
if SCHEME_CRITICAL_SUBJECTS > 0:
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

# --- RUNAWAY INACTION vs CONTROLLED UPGRADE MODERNIZATION ENGINE ---
st.markdown("### RUNAWAY INACTION vs CONTROLLED UPGRADE MODERNIZATION ENGINE")
st.caption(
    "High-clearance actuarial forecast · 36-month sovereign liability projection (NZD)"
)
init_threat_matrix = st.checkbox(
    "📊 Initialize Actuarial Inaction Threat Matrix (36-Month Liability Projection)",
    value=False,
    key="init_actuarial_inaction_threat_matrix",
)
if init_threat_matrix:
    portfolio_spend_nzd = float(df_master_ledger["Spend_To_Date"].sum())
    forecast = compute_actuarial_inaction_threat_matrix(
        portfolio_spend=portfolio_spend_nzd,
        critical_subjects=int(SCHEME_CRITICAL_SUBJECTS),
    )
    render_actuarial_inaction_threat_matrix(forecast)

st.markdown("---")

# --- NATIONWIDE MACROECONOMIC SCALABILITY & VALUE PROJECTION MATRIX ---
st.markdown("### NATIONWIDE MACROECONOMIC SCALABILITY & VALUE PROJECTION MATRIX")
st.caption(
    "Sovereign scaling ledger · Pilot tranche → full geographic population vector"
)
init_scaling_matrix = st.checkbox(
    "🌐 Model Nationwide Geographic Scaling Matrix (Pilot to Full Population Vector)",
    value=False,
    key="init_nationwide_geographic_scaling_matrix",
)
if init_scaling_matrix:
    portfolio_spend_nzd = float(df_master_ledger["Spend_To_Date"].sum())
    pilot_cohort_size = int(len(df_master_ledger))
    scaling = compute_nationwide_scalability_matrix(
        pilot_cohort_size=pilot_cohort_size,
        portfolio_spend=portfolio_spend_nzd,
        critical_subjects=int(SCHEME_CRITICAL_SUBJECTS),
        performance_index=85.9,
    )
    render_nationwide_scalability_matrix(scaling)

st.markdown("---")

# --- COMMAND LEVELS (Layer 1/2/3 + Interface A/B) ---
# These are in-app levels on Executive Command — not separate Streamlit pages.
# Expose them explicitly so they are discoverable after private-chrome nav removal.
_sector_code_for_levels = str(active_sector.get("code", "SECTOR"))
render_command_level_controls(
    sector_code=_sector_code_for_levels,
    global_view_label=GLOBAL_VIEW,
)

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
    st.markdown("#### Interface Layer A · Global Scheme Portfolio")
    st.caption("Layer 1 Structural Mirror KPIs · toggle Layer 2 site/queue drift below Card 3")

    render_structural_mirror_kpis(active_sector)

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
              <div class="metric-label" style="color:#38bdf8;">CABINET MINISTER · HIGH-LEVEL OVERSIGHT</div>
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
<div style="font-size:0.85rem; color:#8b949e;">Active Mandate: {sanitize_html_text(ip_band, max_chars=64)} CapEx Mitigation Control Active</div>
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
        token = sanitize_claim_token(row["Claim ID"])
        anatomy = sanitize_plain_text(row["Anatomy Target"], max_chars=MAX_FIELD_CHARS)
        status = sanitize_status_label(row["Status"])
        rating = sanitize_plain_text(row["Statutory Risk Rating"], max_chars=MAX_FIELD_CHARS)
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
    st.markdown("#### Interface Layer B · Individual Claim Drill-down")
    st.caption("Dossier · alignment vector · Adaptive Drift threshold · Native ACC unlock")

    selected_row = df_master_ledger[
        df_master_ledger["Claim ID"] == view_selection
    ].iloc[0]

    subject_token = sanitize_claim_token(selected_row["Claim ID"])
    anatomy = sanitize_plain_text(selected_row["Anatomy Target"], max_chars=MAX_FIELD_CHARS)
    age = int(selected_row["Age"])
    duty_tier = sanitize_plain_text(selected_row["Demands"], max_chars=MAX_FIELD_CHARS)
    actual_rom = float(selected_row["ROM_Actual"])
    actual_spend = float(selected_row["Spend_To_Date"])
    dict_txt = sanitize_plain_text(
        selected_row.get("NLP_Ingest") or "", max_chars=MAX_NOTES_CHARS
    )

    # Core Backend Calculations Matrix
    job_multiplier = (
        1.30 if "Heavy" in duty_tier else (1.10 if "Medium" in duty_tier else 0.90)
    )
    age_factor = (age - 25) * 0.015
    calibrated_base_cost = 22500.0 * (1.0 + age_factor) * job_multiplier
    calibrated_base_days = int(90 * (1.0 + age_factor) * job_multiplier)

    functional_drift = 100.0 - actual_rom
    ivc = (actual_spend - calibrated_base_cost) / calibrated_base_cost

    # Consume Kinetic Lab continual-learning sensitivity (θ) for live drift band.
    drift_sensitivity = round(float(learner.sensitivity), 4)
    drift_threshold = effective_drift_threshold()
    high_drift = functional_drift > drift_threshold

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
    if high_drift or permanent_disability_prob > 0.50:
        status_label = "CRITICAL PATHWAY DRIFT DETECTED"
        status_color = "#ef4444"
        impact_class = "critical-impact-value"
    else:
        status_label = "NOMINAL PATHWAY ALIGNMENT"
        status_color = "#10b981"
        impact_class = "nominal-impact-value"

    # Prescriptive AI Protocol Engine & Adaptive CV Trajectory Loops
    # High-contrast purple recommendations banner: MSD Vocational Re-Allocation,
    # Crown Commutation settlement metrics, private clinical network bypass.
    safe_commutation_low = sanitize_html_text(f"{mitigated_reserve_target:,.0f}", max_chars=32)
    safe_commutation_high = sanitize_html_text(f"{projected_final_cost:,.0f}", max_chars=32)
    crown_commutation_band = f"${safe_commutation_low} – ${safe_commutation_high} NZD"
    private_bypass_armed = bool(st.session_state.get("ministerial_override", False)) or role == MINISTER_ROLE
    bypass_status = (
        "ARMED — private clinical network triage window open (Crown override)"
        if private_bypass_armed
        else "STANDBY — requires Cabinet Minister statutory override to fire"
    )
    safe_bypass_status = sanitize_html_text(bypass_status, max_chars=160)

    if "Zeta" in subject_token or "Knee" in str(anatomy) or high_drift:
        protocol_html = f"""<div style="background:linear-gradient(135deg,#1b1024 0%,#2a1540 55%,#1b1416 100%); padding:1rem; border-radius:6px; border:2px solid #a855f7; box-shadow:0 0 0 1px #6b21a8 inset; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#e9d5ff; font-weight:700; letter-spacing:0.04em;">UPGRADED RECOMMENDATIONS · CROWN PRESCRIPTIVE ENGINE</div>
<ul style="color:#f8fafc; font-size:0.9rem; margin:0.55rem 0 0; padding-left:1.2rem; line-height:1.5;">
<li><strong style="color:#c084fc;">MSD Vocational Re-Allocation Path:</strong> Immediate pivot from Heavy Manual / Industrial into <em>Site Quality &amp; Safety Compliance Auditor</em> — MSD Registry Slot Reserved → Digital Site Log Systems Cert #AAT-2026.</li>
<li><strong style="color:#c084fc;">Crown Commutation Settlement Metrics:</strong> Calculated lump-sum review band <strong>{crown_commutation_band}</strong> (mitigated reserve floor → total absolute system exposure) to transfer long-tail structural risk off ledger.</li>
<li><strong style="color:#c084fc;">Private Clinical Network Bypass Trigger:</strong> {safe_bypass_status}. Fast-Track Crown Clinical Network Triage Mandate + Independent Medical Examination within 7 days.</li>
</ul>
</div>"""
        adaptive_cv_html = """<div style="background-color:#18141c; padding:0.8rem; border-radius:4px; border:1px solid #a855f7; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#c084fc; font-weight:700; display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
<span>ADAPTIVE CAREER TRAJECTORY &amp; CV PIVOT MATRIX</span>
<span style="background-color:#10b981; color:#0c1017; font-size:0.7rem; padding:1px 5px; border-radius:3px; font-weight:700;">MSD CERTIFIED ADOPTION MANDATORY</span>
</div>
<div style="font-size:0.84rem; color:#8b949e; margin-bottom:0.4rem; font-style:italic;">Mental Preparation Lifeline &amp; Supportive Path Forward via Inter-Agency Ingest. Adherence is state-certified.</div>
<table style="width:100%; border-collapse:collapse; font-size:0.85rem; color:#f8fafc;">
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">Obsolete Vector:</td><td>Heavy Industrial Operations (Physically Incapacitated)</td></tr>
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">Cognitive Harvest:</td><td>Blueprint Interpretation, Logistics Coordination, OHS Enforcement</td></tr>
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">New Target CV:</td><td><strong>Site Quality &amp; Safety Compliance Auditor</strong> (MSD Legally Registered Blueprint)</td></tr>
<tr><td style="color:#8b949e; padding:4px 0; vertical-align:middle;">MSD Vocational Re-Allocation:</td><td>
<div style="display:inline-block; background-color:#166534; color:#4ade80; border:1px solid #14532d; font-size:0.72rem; padding:1px 6px; border-radius:3px; font-weight:600; margin-bottom:3px;">SYSTEM AUTOMATION ACTIVE</div><br/>
<span style="color:#38bdf8; font-family:monospace;">MSD Registry Slot Reserved → Digital Site Log Systems Cert #AAT-2026</span>
</td></tr>
</table>
</div>"""
    else:
        protocol_html = f"""<div style="background:linear-gradient(135deg,#141f17 0%,#1a2a20 100%); padding:1rem; border-radius:6px; border:2px solid #166534; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#4ade80; font-weight:700;">UPGRADED RECOMMENDATIONS · PATH ALIGNMENT SECURE</div>
<ul style="color:#f8fafc; font-size:0.9rem; margin:0.55rem 0 0; padding-left:1.2rem; line-height:1.5;">
<li><strong>MSD Vocational Re-Allocation Path:</strong> Baseline capacity holds — no structural CV pivot required this cycle.</li>
<li><strong>Crown Commutation Settlement Metrics:</strong> Contingent reserve band {crown_commutation_band} held on watch only.</li>
<li><strong>Private Clinical Network Bypass Trigger:</strong> {safe_bypass_status}.</li>
</ul>
</div>"""
        adaptive_cv_html = """<div style="background-color:#141f17; padding:0.8rem; border-radius:4px; border:1px solid #166534; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#4ade80; font-weight:700;">ADAPTIVE CAREER TRAJECTORY STATUS</div>
<p style="color:#f8fafc; font-size:0.88rem; margin:0;">Baseline capacity holds. Pre-injury CV requires zero structural alterations. Verified via MSD National Framework.</p>
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
    safe_subject = sanitize_html_text(subject_token, max_chars=MAX_TOKEN_CHARS)
    safe_native = sanitize_html_text(native_acc_id, max_chars=MAX_TOKEN_CHARS)
    with id_col:
        if st.session_state[resolve_key] and can_unmask_identity:
            st.markdown(
                f"""
                <div class="claim-id-bar">
                  <span class="id-label">ID</span>
                  <span class="id-token">{safe_subject}</span>
                  <span class="resolve-chip">RESOLVED</span>
                  <span class="id-label">Native ACC Claim ID</span>
                  <span class="id-native">{safe_native}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif statutory_briefing_mode:
            st.markdown(
                f"""
                <div class="claim-id-bar">
                  <span class="id-label">ID</span>
                  <span class="id-token">{safe_subject}</span>
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
                  <span class="id-token">{safe_subject}</span>
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
                '<div class="audit-toast">Cabinet Minister · PII gate enforced</div>',
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
            f'<span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{safe_subject}</span> '
            f'<span class="resolve-chip">Resolve to Native ACC Claim ID</span><br/>'
            f'<span style="font-size:0.9rem; color:#8b949e;">Native ACC Claim ID:</span> '
            f'<span style="font-size:0.9rem; color:#10b981; font-weight:700;">{safe_native}</span><br/>'
        )
    elif statutory_briefing_mode:
        id_status_line = (
            f'<span style="font-size:0.9rem; color:#8b949e;">ID:</span> '
            f'<span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{safe_subject}</span> '
            f'<span class="locked-chip">Identity Unmasking Restricted</span><br/>'
        )
    else:
        id_status_line = (
            f'<span style="font-size:0.9rem; color:#8b949e;">ID:</span> '
            f'<span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{safe_subject}</span> '
            f'<span class="masked-chip">Resolve to Native ACC Claim ID</span><br/>'
        )

    safe_anatomy = sanitize_html_text(anatomy, max_chars=MAX_FIELD_CHARS)
    safe_duty = sanitize_html_text(duty_tier, max_chars=MAX_FIELD_CHARS)
    safe_age = sanitize_html_text(int(age), max_chars=8)
    safe_status_label = sanitize_html_text(status_label, max_chars=MAX_STATUS_CHARS)
    safe_dict_html = sanitize_html_text(dict_txt, max_chars=MAX_NOTES_CHARS)
    safe_ppd = sanitize_html_text(f"{permanent_disability_prob * 100:.1f}", max_chars=16)
    safe_tase = sanitize_html_text(f"{projected_final_cost:,.2f}", max_chars=32)
    safe_reserve = sanitize_html_text(f"{mitigated_reserve_target:,.2f}", max_chars=32)
    safe_band_label = sanitize_html_text(
        st.session_state.get("ip_mitigation_band", ip_band), max_chars=64
    )
    safe_lookback = sanitize_html_text(
        f"{(5000 + (projected_final_cost * 0.12)):,.2f}", max_chars=32
    )

    if role == SCHEME_DIRECTOR:
        fee_line = f"""<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>
<div class="metric-value-green" style="font-size:1.4rem;">${safe_lookback} NZD</div>"""
    else:
        fee_line = """<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>
<div style="color:#8b949e; font-style:italic; font-size:0.95rem;">SECURE LEDGER PROXIED TO EXECUTIVE SECTOR</div>"""

    # Left-aligned HTML — no indent so Streamlit does not code-fence it
    html_payload = f"""<div class="metric-box" style="border-left: 4px solid {status_color}; padding: 1.5rem; height: auto;">
<div class="metric-label">Scheme Alignment Status</div>
<div style="color:{status_color}; font-weight:700; font-size:1.2rem; margin-bottom:0.8rem;">{safe_status_label}</div>
<div style="background-color:#0c1017; padding:0.8rem; border-radius:4px; border:1px solid #30363d; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#ffffff;">Claimant File Dossier Matrix</div>
{id_status_line}
<span style="font-size:0.9rem; color:#8b949e;">Target Anatomy:</span> <span style="font-size:0.9rem; color:#ffffff;">{safe_anatomy}</span><br/>
<span style="font-size:0.9rem; color:#8b949e;">Demands / Age:</span> <span style="font-size:0.9rem; color:#ffffff;">{safe_duty} (Age {safe_age})</span><br/>
<p style="font-size:0.85rem; color:#8b949e; font-style:italic; margin-top:0.4rem; margin-bottom:0;"><strong>NLP Ingest:</strong> {safe_dict_html}</p>
</div>
{protocol_html}
{adaptive_cv_html}
<div class="metric-label">Probability of Permanent Disability (PPD)</div>
<div class="{impact_class}">{safe_ppd}%</div>
<hr style="border:0; border-top:1px solid #30363d; margin: 0.8rem 0;"/>
<div class="metric-label">Total Absolute System Exposure (TASE)</div>
<div class="metric-value-silver" style="font-size:1.5rem; margin-bottom:0.3rem;">${safe_tase} NZD</div>
<div class="metric-label">Mitigated Capital Reserve Target ({safe_band_label} Applied)</div>
<div class="metric-value-green" style="font-size:1.5rem; margin-bottom:0.3rem;">${safe_reserve} NZD</div>
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
                "High Drift Flag" if high_drift else "Clear",
            ],
            "Point of Drift Variance": [
                "On Track",
                f"${actual_spend - calibrated_base_cost:+,.0f} NZD",
                f"-{functional_drift:.0f}% Dev",
                "Path B Active" if high_drift else "Clear",
            ],
        }
    )
    st.table(df_vector)
    safe_sensitivity = sanitize_html_text(f"{drift_sensitivity:.4f}", max_chars=16)
    safe_threshold = sanitize_html_text(f"{drift_threshold:.2f}", max_chars=16)
    safe_base_threshold = sanitize_html_text(f"{BASE_DRIFT_THRESHOLD:.1f}", max_chars=16)
    st.markdown(
        f"""
        <div class="metric-box" style="margin-top:0.4rem;">
          <div class="metric-label">Adaptive Drift Learner · Continual Sensitivity θ(t)</div>
          <div style="display:flex; gap:1.5rem; flex-wrap:wrap; font-size:0.9rem; color:#e2e8f0;">
            <div><span style="color:#8b949e;">Sensitivity</span><br/>
              <strong style="font-family:IBM Plex Mono,monospace;">{safe_sensitivity}</strong></div>
            <div><span style="color:#8b949e;">Live Threshold</span><br/>
              <strong style="font-family:IBM Plex Mono,monospace;">{safe_threshold}%</strong>
              <span style="color:#8b949e;"> (base {safe_base_threshold}%)</span></div>
            <div><span style="color:#8b949e;">Observed Drift</span><br/>
              <strong style="font-family:IBM Plex Mono,monospace;">{sanitize_html_text(f"{functional_drift:.1f}", max_chars=16)}%</strong></div>
          </div>
          <div class="metric-subtext">θ sourced from Kinetic Lab drift feedback loop · base band {safe_base_threshold}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
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

    if high_drift:
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

# --- GEMINI NOTEBOOK MANIFEST (main surface: link + embedded notebook) ---
render_gemini_intelligence_notebook()
