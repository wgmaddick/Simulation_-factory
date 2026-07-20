"""AAT Scheme Performance Engine — predictive operational risk governance.

Portrait-tablet optimized: slim 3-column global metrics, core-vector master
ledger, and stacked drill-down viewports (dossier → alignment table → chart).
"""

from __future__ import annotations

import html
import re
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

LAYOUT_LOCKED = True
SCHEME_DIRECTOR = "Scheme Director (GM)"
CLAIMS_OFFICER = "Claims Officer / Analyst"
REVIEWING_SPECIALIST = "Reviewing Specialist"
GLOBAL_VIEW = "Global Scheme Portfolio (All Active Claims)"
NEW_CLAIM_VIEW = "➕ Log New Claimant Profile"
CO_TASK_ID = "CO-AAT-2026-031"
DUTY_OPTIONS = [
    "Heavy Manual / Industrial",
    "Medium Logistics / Transport",
    "Sedentary Clerical",
]
ANATOMY_OPTIONS = [
    "Shoulder (Glenohumeral)",
    "Lumbar Spine Matrix",
    "Lower Extremity (Knee)",
]

# Defensive bounds for the data-intake matrix / form surfaces (Streamlit widgets
# + any future CSV/XLSX corporate profile parse path).
MAX_TOKEN_CHARS = 96
MAX_STATUS_CHARS = 64
MAX_NOTES_CHARS = 4000
MAX_MANDATE_CHARS = 280
MAX_INTAKE_ROWS = 500
MAX_FIELD_CHARS = 120
PORTFOLIO_LEDGER_COLUMNS = [
    "Claim ID",
    "Anatomy Target",
    "Age",
    "Demands",
    "ROM_Actual",
    "Spend_To_Date",
    "Status",
]
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


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


def bound_intake_frame(frame: pd.DataFrame | None) -> pd.DataFrame:
    """Cap row count for any corporate / matrix intake parse to avoid unbounded load."""
    if frame is None:
        return pd.DataFrame(columns=PORTFOLIO_LEDGER_COLUMNS)
    if frame.empty:
        return frame
    if len(frame) > MAX_INTAKE_ROWS:
        return frame.iloc[:MAX_INTAKE_ROWS].copy()
    return frame

# 1. High-Contrast Sovereign Dark Theme Configuration
st.set_page_config(
    layout="wide",
    page_title="AAT Scheme Performance Engine",
    page_icon="⬡",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;700&display=swap');

    .reportview-container, .main {
        background-color: #0c1017;
        color: #f8fafc;
        font-family: "IBM Plex Sans", sans-serif;
    }
    .stApp {
        background-color: #0c1017;
        color: #f8fafc;
        font-family: "IBM Plex Sans", sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #0c1017;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #f8fafc !important;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    /* Institutional Metric Box Grid Wrappers */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        height: auto;
        overflow: visible;
    }
    .metric-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.80rem;
        text-transform: uppercase;
        color: #8b949e;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .metric-value-silver {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1.2;
    }
    .metric-value-crimson {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ef4444;
        line-height: 1.2;
    }
    .metric-value-green {
        font-size: 1.8rem;
        font-weight: 700;
        color: #10b981;
        line-height: 1.2;
    }
    .metric-subtext {
        font-size: 0.85rem;
        color: #8b949e;
        margin-top: 0.3rem;
    }
    /* Executive Large-Print Callout Focus */
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
    th, td,
    [data-testid="stTable"] th,
    [data-testid="stTable"] td {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
    }
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border-color: #30363d !important;
    }
    [data-testid="stVegaLiteChart"],
    [data-testid="stLineChart"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 0.75rem 0.5rem 0.25rem 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- MASTER CLAIMS DATABASE CORE ---
@st.cache_data
def load_internal_portfolio_ledger() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Claim ID": "AAT-Claimant-Delta-2026",
                "Anatomy Target": "Shoulder (Glenohumeral)",
                "Age": 48,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 62.0,
                "Spend_To_Date": 28400.0,
                "Status": "CRITICAL DRIFT",
            },
            {
                "Claim ID": "AAT-Claimant-Epsilon-2026",
                "Anatomy Target": "Lumbar Spine Matrix",
                "Age": 32,
                "Demands": "Sedentary Clerical",
                "ROM_Actual": 94.0,
                "Spend_To_Date": 12100.0,
                "Status": "NOMINAL ALIGNMENT",
            },
            {
                "Claim ID": "AAT-Claimant-Zeta-2026",
                "Anatomy Target": "Lower Extremity (Knee)",
                "Age": 61,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 48.0,
                "Spend_To_Date": 41200.0,
                "Status": "CRITICAL DRIFT",
            },
            {
                "Claim ID": "AAT-Claimant-Eta-2026",
                "Anatomy Target": "Shoulder (Glenohumeral)",
                "Age": 29,
                "Demands": "Medium Logistics / Transport",
                "ROM_Actual": 88.0,
                "Spend_To_Date": 19400.0,
                "Status": "NOMINAL ALIGNMENT",
            },
        ]
    )


def dictation_for_claim(claim_id: str) -> str:
    if "Delta" in claim_id:
        return (
            "Claimant presents with severe shoulder disruption. Cellular age curves "
            "indicate prolonged recovery runway."
        )
    if "Zeta" in claim_id:
        return (
            "Advanced structural vulnerability noted in knee construct. High manual "
            "occupational exposures compounding timeline variance."
        )
    return (
        "Favorable tissue consistency. Functional path trajectory arc tracking "
        "nominal. Low stress metrics."
    )


def _job_params(duty_tier: str) -> tuple[float, float, float]:
    if "Heavy" in duty_tier:
        return 1.30, 28.0, 1.35
    if "Medium" in duty_tier:
        return 1.10, 15.0, 1.12
    return 0.90, 5.0, 0.95


def emulate_live_telemetry(age: int, duty_tier: str) -> tuple[float, float]:
    job_multiplier, rom_loss, spend_variance = _job_params(duty_tier)
    age_factor = (age - 25) * 0.015
    base_cost = 22500.0 * (1.0 + age_factor) * job_multiplier
    actual_rom = max(40.0, 100.0 - rom_loss - (age_factor * 25.0))
    actual_spend = base_cost * spend_variance * (1.0 + (age_factor * 0.2))
    return float(actual_rom), float(actual_spend)


def compute_claim_metrics(
    *,
    age: int,
    duty_tier: str,
    actual_rom: float,
    actual_spend: float,
    cap_floor: int,
) -> dict[str, float]:
    job_multiplier, _, _ = _job_params(duty_tier)
    age_factor = (age - 25) * 0.015
    calibrated_base_cost = 22500.0 * (1.0 + age_factor) * job_multiplier
    calibrated_base_days = max(1, int(90 * (1.0 + age_factor) * job_multiplier))
    functional_drift = 100.0 - actual_rom
    ivc = (actual_spend - calibrated_base_cost) / calibrated_base_cost
    projected_final_cost = (
        calibrated_base_cost
        + (functional_drift * 185.0)
        + (ivc * calibrated_base_cost)
    )
    mitigated_reserve_target = projected_final_cost * (1.0 - (cap_floor / 100.0))
    permanent_disability_prob = 1.0 / (
        1.0
        + np.exp(-(-2.8 + (age * 0.045) + (functional_drift * 0.055)))
    )
    return {
        "calibrated_base_cost": float(calibrated_base_cost),
        "calibrated_base_days": float(calibrated_base_days),
        "functional_drift": float(functional_drift),
        "ivc": float(ivc),
        "projected_final_cost": float(projected_final_cost),
        "mitigated_reserve_target": float(mitigated_reserve_target),
        "permanent_disability_prob": float(permanent_disability_prob),
    }


def enrich_ledger_with_metrics(
    ledger: pd.DataFrame, cap_floor: int
) -> pd.DataFrame:
    rows: list[dict] = []
    for _, row in ledger.iterrows():
        m = compute_claim_metrics(
            age=int(row["Age"]),
            duty_tier=str(row["Demands"]),
            actual_rom=float(row["ROM_Actual"]),
            actual_spend=float(row["Spend_To_Date"]),
            cap_floor=int(cap_floor),
        )
        rows.append(
            {
                **row.to_dict(),
                "Functional Drift": m["functional_drift"],
                "PPD": m["permanent_disability_prob"],
                "TASE": m["projected_final_cost"],
                "Reserve Target": m["mitigated_reserve_target"],
                "Base Days": int(m["calibrated_base_days"]),
            }
        )
    return pd.DataFrame(rows)


def render_claims_officer_action_task(
    ledger_enriched: pd.DataFrame, cap_floor: int
) -> None:
    """Role-gated action board for Claims Officer / Analyst (CO-AAT-2026-031)."""
    critical = ledger_enriched[
        ledger_enriched["Status"].str.contains("CRITICAL", case=False, na=False)
    ].sort_values("PPD", ascending=False)
    watch = ledger_enriched[
        ~ledger_enriched["Status"].str.contains("CRITICAL", case=False, na=False)
    ].sort_values("PPD", ascending=False)

    st.markdown("### CLAIMS OFFICER / ANALYST — ACTION TASK")
    safe_task_id = sanitize_html_text(CO_TASK_ID, max_chars=48)
    safe_cap = sanitize_html_text(f"{int(cap_floor)}", max_chars=8)
    st.markdown(
        f"<div class='metric-box' style='border-left:4px solid #ef4444;'>"
        f"<div class='metric-label'>Task ID</div>"
        f"<div class='metric-value-silver' style='font-size:1.35rem;'>{safe_task_id}</div>"
        f"<div class='metric-subtext'>Role: Claims Officer / Analyst · "
        f"Mandate floor: {safe_cap}% CapEx mitigation</div>"
        f"<p style='color:#e2e8f0; margin:0.75rem 0 0 0;'>"
        f"Clear the CRITICAL DRIFT files before they harden into long-tail PPD exposure."
        f"</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Priority Queue")
    queue_rows: list[dict] = []
    for idx, (_, row) in enumerate(critical.iterrows()):
        priority = "P0" if idx == 0 else f"P{idx}"
        why = (
            "Highest PPD + spend"
            if idx == 0
            else "Critical pathway escalation"
        )
        claim_id = sanitize_claim_token(row["Claim ID"])
        anatomy = sanitize_plain_text(row["Anatomy Target"], max_chars=MAX_FIELD_CHARS)
        demands = sanitize_plain_text(row["Demands"], max_chars=MAX_FIELD_CHARS)
        queue_rows.append(
            {
                "Priority": priority,
                "Claim ID": claim_id,
                "Status": sanitize_status_label(row.get("Status", "")),
                "Why now": why,
                "Key metrics": (
                    f"Age {int(row['Age'])} · {anatomy} · "
                    f"{demands} · ROM {row['ROM_Actual']:.0f}% · "
                    f"Drift −{row['Functional Drift']:.0f}% · "
                    f"Spend ${row['Spend_To_Date']:,.0f} · "
                    f"PPD {row['PPD'] * 100:.1f}% · "
                    f"TASE ${row['TASE']:,.0f} NZD · "
                    f"Reserve ${row['Reserve Target']:,.0f} NZD"
                ),
            }
        )
    if not watch.empty:
        watch_claim_ids = [
            sanitize_claim_token(c) for c in watch["Claim ID"].tolist()
        ]
        watch_ids = " / ".join(
            sanitize_for_markdown(
                c.replace("AAT-Claimant-", "").replace("-2026", ""),
                max_chars=48,
            )
            for c in watch_claim_ids
        )
        watch_ppd = " / ".join(f"{p * 100:.1f}%" for p in watch["PPD"].tolist())
        queue_rows.append(
            {
                "Priority": "Watch",
                "Claim ID": " / ".join(watch_claim_ids),
                "Status": "NOMINAL ALIGNMENT",
                "Why now": f"Nominal — no action this cycle ({watch_ids})",
                "Key metrics": f"PPD {watch_ppd}",
            }
        )
    st.table(pd.DataFrame(queue_rows))

    if not critical.empty:
        p0 = critical.iloc[0]
        p1 = critical.iloc[1] if len(critical) > 1 else None
        p0_short = sanitize_for_markdown(
            str(p0["Claim ID"]).replace("AAT-Claimant-", "").replace("-2026", ""),
            max_chars=48,
        )
        actions = [
            (
                f"Open **AUDIT VIEW → {p0_short}**, confirm Path B trigger and "
                "document NLP note (clinical compounding factors)."
            ),
            (
                f"Escalate **{p0_short}** for accelerated rehabilitation pathway; "
                f"log variance vs {int(p0['Base Days'])}-day recovery runway."
            ),
        ]
        if p1 is not None:
            p1_short = sanitize_for_markdown(
                str(p1["Claim ID"]).replace("AAT-Claimant-", "").replace("-2026", ""),
                max_chars=48,
            )
            actions.append(
                f"Open **{p1_short}**; schedule pathway review and psychosocial "
                "barrier check from NLP ingest."
            )
        actions.extend(
            [
                "Update escalated files with intervention status in the Master "
                "Claims Accountability Ledger.",
                "Do **not** attempt Lookback Valuation edits — proxied to Scheme Director.",
            ]
        )
        st.markdown("#### Required Actions (This Shift)")
        for i, action in enumerate(actions, start=1):
            st.markdown(f"{i}. {action}")

        critical_names = " and ".join(
            sanitize_for_markdown(
                str(c).replace("AAT-Claimant-", "").replace("-2026", ""),
                max_chars=48,
            )
            for c in critical["Claim ID"].tolist()
        )
        st.markdown("#### Done When")
        st.markdown(
            f"- {critical_names} have dated remediation notes in-file\n"
            "- Escalated claims flagged for Director lookback review if TASE "
            "still rising after intervention\n"
            "- Nominal files remain watch-only (no escalation)"
        )
    st.markdown("---")


df_master_ledger = bound_intake_frame(load_internal_portfolio_ledger())
claim_ids = [sanitize_claim_token(c) for c in df_master_ledger["Claim ID"].tolist()]

# --- SIDEBAR: GOVERNANCE LAYER FILTERS ---
with st.sidebar:
    st.markdown("### AAT SCHEME GOVERNANCE")
    # -------------------------------------------------------------------------
    # DEMO ROLE MATRIX (local toggle only — not an access-control boundary)
    #
    # Production identity architecture (OpenID Connect / enterprise OAuth):
    #   1. Place an OIDC-compliant IdP in front of Streamlit (e.g. Auth0,
    #      Azure AD / Entra ID, Okta, Keycloak) via reverse proxy or
    #      streamlit-oauth / custom st.login component.
    #   2. Resolve the authenticated principal once per session, e.g.:
    #        # claims = st.user  # or secrets-backed OIDC callback payload
    #        # role = map_idp_groups_to_scheme_role(claims["groups"])
    #   3. Replace the selectbox below with the IdP-derived role; keep the
    #      same SCHEME_DIRECTOR / CLAIMS_OFFICER / REVIEWING_SPECIALIST
    #      constants so privacy switches (lookback fee masking, action board)
    #      continue to gate on `role` without UI churn.
    #   4. Enforce authorization server-side on any future data APIs — never
    #      trust a client-chosen role string as the sole ACL.
    # -------------------------------------------------------------------------
    role = st.selectbox(
        "Active User Role Matrix",
        [
            SCHEME_DIRECTOR,
            CLAIMS_OFFICER,
            REVIEWING_SPECIALIST,
        ],
        help="Demo toggle only. Production will bind this to OIDC group claims.",
    )
    st.markdown("---")
    st.markdown("### SCHEME MANDATE INJECTION")
    cap_floor = st.slider("Enforce Liability Mitigation Floor (%)", 0, 50, 15)
    strategic_note = st.text_input(
        "Disseminate Performance Mandate",
        placeholder="e.g., Accelerate Pathway Interventions",
        max_chars=MAX_MANDATE_CHARS,
    )
    strategic_note = sanitize_plain_text(strategic_note, max_chars=MAX_MANDATE_CHARS)
    st.caption(f"Active role: **{sanitize_for_markdown(role, max_chars=64)}** · Liability floor **{int(cap_floor)}%**")
    if strategic_note:
        st.caption(f"Mandate: {sanitize_for_markdown(strategic_note, max_chars=MAX_MANDATE_CHARS)}")

# --- MAIN PERFORMANCE DASHBOARD TITLE ---
st.title("AAT SCHEME PERFORMANCE ENGINE")
st.markdown(
    "<p style='color:#8b949e; margin-top:-10px;'>"
    "Predictive Operational Risk & Long-Tail Claims Governance Framework</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- CENTRAL ROUTING SELECTOR ---
view_selection = st.selectbox(
    "AUDIT VIEW COMMAND SECTOR",
    [GLOBAL_VIEW, NEW_CLAIM_VIEW, *claim_ids],
)
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# INTERFACE LAYER A: GLOBAL SCHEME PORTFOLIO VIEW (PORTRAIT TABLET OPTIMIZED)
# ==============================================================================
if view_selection == GLOBAL_VIEW:
    # Text optimized to avoid text wrapping on tablet layouts
    col1, col2, col3 = st.columns(3)
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
            '<div class="metric-subtext">Targeted Escalations Pending</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Performance Index</div>'
            '<div class="metric-value-green">85.9%</div>'
            '<div class="metric-subtext">Baseline Trajectory Alignment</div></div>',
            unsafe_allow_html=True,
        )

    # Claims Officer / Analyst role surface — action task CO-AAT-2026-031
    if role == CLAIMS_OFFICER:
        st.markdown("---")
        ledger_enriched = enrich_ledger_with_metrics(df_master_ledger, int(cap_floor))
        render_claims_officer_action_task(ledger_enriched, int(cap_floor))

    st.markdown("### MASTER CLAIMS ACCOUNTABILITY LEDGER")
    # Sliced down strictly to core vectors to prevent page overflow.
    # Preserve responsive st.table CSS (overflow-wrap / word-break) — only
    # sanitize cell values before render.
    df_formatted_ledger = df_master_ledger[
        ["Claim ID", "Anatomy Target", "Status"]
    ].copy()
    df_formatted_ledger["Claim ID"] = df_formatted_ledger["Claim ID"].map(
        sanitize_claim_token
    )
    df_formatted_ledger["Anatomy Target"] = df_formatted_ledger["Anatomy Target"].map(
        lambda v: sanitize_plain_text(v, max_chars=MAX_FIELD_CHARS)
    )
    df_formatted_ledger["Status"] = df_formatted_ledger["Status"].map(
        sanitize_status_label
    )
    st.table(df_formatted_ledger)

    st.markdown("---")
    st.markdown("### AGGREGATE SCHEME CAPEX VELOCITY TRAJECTORY")

    days_series = np.arange(0, 121, 10)
    standard_macro = 25000 * 3 * (days_series / 90)
    standard_macro = np.clip(standard_macro, 0, 25000 * 3)
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
        color=["#10b981", "#ef4444"],
    )

# ==============================================================================
# INTERFACE LAYER B: INDIVIDUAL / NEW CLAIM (EXECUTIVE CARD CONSOLIDATED)
# ==============================================================================
else:
    is_new_claim = view_selection == NEW_CLAIM_VIEW

    if is_new_claim:
        st.markdown("### LOG NEW CLAIMANT PROFILE")
        st.caption("Unlocked triage intake · dossier recalculates live")
        edit_c1, edit_c2, edit_c3 = st.columns(3)
        with edit_c1:
            subject_token = st.text_input(
                "Participant Identifier Token",
                value="",
                placeholder="e.g., AAT-Claimant-Theta-2026",
                max_chars=MAX_TOKEN_CHARS,
            )
            anatomy = st.selectbox(
                "Anatomy Target",
                ANATOMY_OPTIONS,
                index=0,
            )
        with edit_c2:
            age = st.number_input(
                "Actuarial Chronological Age",
                min_value=18,
                max_value=75,
                value=25,
            )
            duty_tier = st.selectbox(
                "Occupational Demands Tier",
                DUTY_OPTIONS,
                index=DUTY_OPTIONS.index("Sedentary Clerical"),
            )
        with edit_c3:
            dict_txt = st.text_area(
                "Clinical Summary Ingest Log",
                value="Type or dictate clinical triage notes here...",
                max_chars=MAX_NOTES_CHARS,
            )
        subject_token = sanitize_claim_token(subject_token)
        dict_txt = sanitize_plain_text(dict_txt, max_chars=MAX_NOTES_CHARS)
        actual_rom, actual_spend = emulate_live_telemetry(int(age), str(duty_tier))
        display_token = subject_token or "NEW-CLAIMANT-DRAFT"
    else:
        selected_row = df_master_ledger[
            df_master_ledger["Claim ID"] == view_selection
        ].iloc[0]

        subject_token = sanitize_claim_token(selected_row["Claim ID"])
        anatomy = str(selected_row["Anatomy Target"])
        age = int(selected_row["Age"])
        duty_tier = str(selected_row["Demands"])
        actual_rom = float(selected_row["ROM_Actual"])
        actual_spend = float(selected_row["Spend_To_Date"])
        display_token = subject_token
        dict_txt = dictation_for_claim(subject_token)

    metrics = compute_claim_metrics(
        age=int(age),
        duty_tier=str(duty_tier),
        actual_rom=float(actual_rom),
        actual_spend=float(actual_spend),
        cap_floor=int(cap_floor),
    )
    calibrated_base_cost = metrics["calibrated_base_cost"]
    calibrated_base_days = int(metrics["calibrated_base_days"])
    functional_drift = metrics["functional_drift"]
    ivc = metrics["ivc"]
    projected_final_cost = metrics["projected_final_cost"]
    mitigated_reserve_target = metrics["mitigated_reserve_target"]
    permanent_disability_prob = metrics["permanent_disability_prob"]

    # Set Color Logic for Display Elements
    if functional_drift > 15.0 or permanent_disability_prob > 0.50:
        status_label = "CRITICAL PATHWAY DRIFT DETECTED"
        status_color = "#ef4444"
        impact_class = "critical-impact-value"
    else:
        status_label = "NOMINAL PATHWAY ALIGNMENT"
        status_color = "#10b981"
        impact_class = "nominal-impact-value"

    # Escape every dynamic field before custom HTML dossier render (keep markup/CSS intact).
    safe_display_token = sanitize_html_text(display_token, max_chars=MAX_TOKEN_CHARS)
    safe_anatomy = sanitize_html_text(anatomy, max_chars=MAX_FIELD_CHARS)
    safe_duty = sanitize_html_text(duty_tier, max_chars=MAX_FIELD_CHARS)
    safe_status_label = sanitize_html_text(status_label, max_chars=MAX_STATUS_CHARS)
    safe_dict_html = sanitize_html_text(dict_txt, max_chars=MAX_NOTES_CHARS)
    safe_age = sanitize_html_text(int(age), max_chars=8)
    safe_cap_floor = sanitize_html_text(int(cap_floor), max_chars=8)
    safe_ppd = sanitize_html_text(f"{permanent_disability_prob * 100:.1f}", max_chars=16)
    safe_tase = sanitize_html_text(f"{projected_final_cost:,.2f}", max_chars=32)
    safe_reserve = sanitize_html_text(f"{mitigated_reserve_target:,.2f}", max_chars=32)
    lookback_amount = 5000 + (projected_final_cost * 0.12)
    safe_lookback = sanitize_html_text(f"{lookback_amount:,.2f}", max_chars=32)

    st.markdown("## PREVENTATIVE DRIFT RADAR DEEP-DIVE")

    # --- STACKED BLOCK 1: MASTER LEDGER DOSSIER (full width for tablet scanning) ---
    st.markdown("#### Comprehensive Scheme Ledger Dossier")

    if role == SCHEME_DIRECTOR:
        fee_line = (
            f'<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>\n'
            f'<div class="metric-value-green" style="font-size:1.4rem;">'
            f"${safe_lookback} NZD</div>"
        )
    else:
        fee_line = (
            '<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>\n'
            '<div style="color:#8b949e; font-style:italic; font-size:0.95rem;">'
            "🔒 SECURE LEDGER PROXIED TO EXECUTIVE SECTOR</div>"
        )

    # Left-aligned HTML payload — no indent so Streamlit does not code-fence it.
    # Metric-box / responsive table CSS classes unchanged for iPad viewport.
    html_payload = f"""<div class="metric-box" style="border-left: 4px solid {status_color}; padding: 1.5rem; height: auto;">
<div class="metric-label">Scheme Alignment Status</div>
<div style="color:{status_color}; font-weight:700; font-size:1.2rem; margin-bottom:0.8rem;">{safe_status_label}</div>
<div style="background-color:#0c1017; padding:0.8rem; border-radius:4px; border:1px solid #30363d; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#ffffff;">Claimant File Dossier Matrix</div>
<span style="font-size:0.9rem; color:#8b949e;">ID:</span> <span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{safe_display_token}</span><br/>
<span style="font-size:0.9rem; color:#8b949e;">Target Anatomy:</span> <span style="font-size:0.9rem; color:#ffffff;">{safe_anatomy}</span><br/>
<span style="font-size:0.9rem; color:#8b949e;">Demands / Age:</span> <span style="font-size:0.9rem; color:#ffffff;">{safe_duty} (Age {safe_age})</span><br/>
<p style="font-size:0.85rem; color:#8b949e; font-style:italic; margin-top:0.4rem; margin-bottom:0;"><strong>NLP Ingest:</strong> {safe_dict_html}</p>
</div>
<div class="metric-label">Probability of Permanent Disability (PPD)</div>
<div class="{impact_class}">{safe_ppd}%</div>
<hr style="border:0; border-top:1px solid #30363d; margin: 0.8rem 0;"/>
<div class="metric-label">Total Absolute System Exposure (TASE)</div>
<div class="metric-value-silver" style="font-size:1.5rem; margin-bottom:0.3rem;">${safe_tase} NZD</div>
<div class="metric-label">Mitigated Capital Reserve Target ({safe_cap_floor}% Floor Applied)</div>
<div class="metric-value-green" style="font-size:1.5rem; margin-bottom:0.3rem;">${safe_reserve} NZD</div>
{fee_line}
</div>"""
    st.markdown(html_payload, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- STACKED BLOCK 2: DATA ALIGNMENT MATRIX (full width, unscrunched) ---
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
                "On Track" if functional_drift <= 15 else "Timeline Breach",
                f"${actual_spend - calibrated_base_cost:+,.0f} NZD",
                f"-{functional_drift:.0f}% Dev",
                "Path B Active" if functional_drift > 15 else "Clear",
            ],
        }
    )
    st.table(df_vector)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- STACKED BLOCK 3: Individual Cost Trajectory Trend Graph ---
    st.markdown("### INDIVIDUAL PERFORMANCE TIME-COST AXIS")
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
    st.caption(
        f"{'Live draft' if is_new_claim else 'Individual'} axis · "
        f"`{sanitize_for_markdown(display_token)}` · "
        f"{calibrated_base_days}-day horizon (NZD)"
    )
    st.line_chart(
        df_chart,
        x="Days Elapsed",
        y=["Standard Expected Runway", "Actual Cumulative Spend Velocity"],
        color=["#10b981", "#ef4444"],
    )
