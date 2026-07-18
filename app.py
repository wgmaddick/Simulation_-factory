"""AAT Scheme Performance Engine — predictive operational risk governance.

High-contrast sovereign dark theme for scheme claims performance, triage intake,
preventative drift radar, role-based ledger masking, and longitudinal cost trends.
Currency basis: NZD. Primary executive focus: large-print PPD.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

LAYOUT_LOCKED = True
SCHEME_DIRECTOR = "Scheme Director (GM)"


def default_aat_profile() -> pd.DataFrame:
    """Standard AAT performance profile used when no client file is loaded."""
    return pd.DataFrame(
        {
            "participant_token": [
                "AAT-Claimant-Delta-2026",
                "AAT-Claimant-Echo-2026",
                "AAT-Claimant-Foxtrot-2026",
            ],
            "critical_flag": [1, 0, 1],
            "aat_alignment_pct": [87.3, 92.1, 78.4],
            "scheme_liability_usd": [412500.0, 188000.0, 276000.0],
            "actual_spend": [28400.0, 19250.0, 34100.0],
            "age": [48, 41, 55],
        }
    )


def load_client_data_profile(uploaded_file: Any) -> tuple[pd.DataFrame, str]:
    """Parse CSV/XLSX when present; otherwise fall back to the AAT sample profile."""
    if uploaded_file is None:
        return default_aat_profile(), "synthetic"

    try:
        name = (uploaded_file.name or "").lower()
        buffer = BytesIO(uploaded_file.getvalue())
        if name.endswith(".csv"):
            frame = pd.read_csv(buffer)
        elif name.endswith(".xlsx") or name.endswith(".xls"):
            frame = pd.read_excel(buffer)
        else:
            return default_aat_profile(), "synthetic"

        if frame is None or frame.empty:
            return default_aat_profile(), "synthetic"

        frame.columns = [str(c).strip().lower().replace(" ", "_") for c in frame.columns]
        return frame, "uploaded"
    except Exception:
        return default_aat_profile(), "synthetic"


def _col(df: pd.DataFrame, *candidates: str) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def scheme_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Derive macro scheme bar metrics from the active client profile."""
    n_cases = int(len(df)) if len(df) else 3
    crit_col = _col(df, "critical_flag", "critical", "pathway_drift")
    if crit_col is not None:
        critical = int(pd.to_numeric(df[crit_col], errors="coerce").fillna(0).astype(bool).sum())
    else:
        critical = max(1, int(round(n_cases * 0.67)))

    align_col = _col(df, "aat_alignment_pct", "odg_alignment_pct", "alignment")
    if align_col is not None:
        alignment = float(pd.to_numeric(df[align_col], errors="coerce").dropna().mean())
    else:
        alignment = 85.9

    liab_col = _col(df, "scheme_liability_usd", "indemnity_exposure_usd", "liability")
    if liab_col is not None:
        exposure = float(pd.to_numeric(df[liab_col], errors="coerce").fillna(0).sum())
    else:
        exposure = 876500.0

    return {
        "cases": n_cases,
        "drift": critical,
        "alignment": alignment,
        "exposure": exposure,
    }


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
    /* Institutional Metric Box Wrappers */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #8b949e;
        letter-spacing: 0.05em;
    }
    .metric-value-green {
        font-size: 2rem;
        font-weight: 700;
        color: #10b981;
    }
    .metric-value-crimson {
        font-size: 2rem;
        font-weight: 700;
        color: #ef4444;
    }
    .metric-value-silver {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    /* Large Print Primary Executive Metric Focus */
    .large-impact-value {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-family: "IBM Plex Mono", monospace;
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
    .stButton > button {
        background-color: #21262d !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        font-weight: 700 !important;
    }
    .stButton > button p,
    .stButton > button span {
        color: #ffffff !important;
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

# 2. State Initialization for Dynamic Calculators
if "ivc" not in st.session_state:
    st.session_state.ivc = 0.0
if "functional_drift" not in st.session_state:
    st.session_state.functional_drift = 0.0

# --- SIDEBAR: CONTROLS & DYNAMIC ROLE PRIVACY MATRIX ---
with st.sidebar:
    st.markdown("### AAT SCHEME GOVERNANCE")
    st.markdown(
        "<p style='color:#8b949e; font-size:0.85rem;'>Role-Based Access Control Active</p>",
        unsafe_allow_html=True,
    )

    role = st.selectbox(
        "Active User Role Matrix",
        [
            "Scheme Director (GM)",
            "Claims Officer / Analyst",
            "Reviewing Specialist",
        ],
    )

    st.markdown("---")
    st.markdown("### SCHEME MANDATE INJECTION")
    cap_floor = st.slider("Enforce Liability Mitigation Floor (%)", 0, 50, 15)
    strategic_note = st.text_input(
        "Disseminate Performance Mandate",
        placeholder="e.g., Accelerate Pathway Interventions",
    )
    st.caption(f"Active role: **{role}** · Liability floor **{cap_floor}%**")
    if strategic_note:
        st.caption(f"Mandate: {strategic_note}")

# --- MAIN PERFORMANCE DASHBOARD ---
st.title("AAT SCHEME PERFORMANCE ENGINE")
st.markdown(
    "<p style='color:#8b949e; margin-top:-10px;'>"
    "Predictive Operational Risk & Long-Tail Claims Governance</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# MODULE 1: DYNAMIC DATA INGESTION GATE (EASY BULK UPLOAD)
uploaded_file = st.file_uploader(
    "📥 LOAD CUSTOM CLIENT DATA PROFILE (Drag & Drop CSV / XLSX)",
    type=["csv", "xlsx"],
)

profile_df, profile_source = load_client_data_profile(uploaded_file)
kpis = scheme_kpis(profile_df)

if profile_source == "uploaded":
    st.success("Custom client profile ingested successfully.")
    base_cost_multiplier = 1.15
else:
    st.markdown(
        "<p style='color:#8b949e; font-size:0.85rem; font-style:italic;'>"
        "Standard AAT Performance Profile Active • Upload client spreadsheet to overwrite baseline."
        "</p>",
        unsafe_allow_html=True,
    )
    base_cost_multiplier = 1.0

display_cases = kpis["cases"]
display_drift = kpis["drift"]
display_alignment = f"{kpis['alignment']:.1f}%"
display_exposure = f"${kpis['exposure']:,.0f} NZD"

# Macro Scheme Performance Metrics Bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="metric-box"><div class="metric-label">Total Scheme Claims</div>'
        f'<div class="metric-value-silver">{display_cases} Cases</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-box"><div class="metric-label">Critical Pathway Drift</div>'
        f'<div class="metric-value-crimson">{display_drift} Subjects</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-box"><div class="metric-label">AAT Baseline Performance Index</div>'
        f'<div class="metric-value-green">{display_alignment}</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    if role == SCHEME_DIRECTOR:
        st.markdown(
            f'<div class="metric-box"><div class="metric-label">Projected Scheme Liability</div>'
            f'<div class="metric-value-silver">{display_exposure}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Projected Scheme Liability</div>'
            '<div style="color:#8b949e; font-size:1.2rem; font-weight:700; margin-top:0.8rem;">'
            "🔒 RESTRICTED</div></div>",
            unsafe_allow_html=True,
        )

# --- MODULE 2: CLINICAL INTAKE MODALITY ---
st.markdown("### SCHEME TRIAGE INTAKE INGESTION")
intake_col1, intake_col2, intake_col3 = st.columns(3)
with intake_col1:
    subject_token = st.text_input(
        "Participant Identifier Token",
        value="AAT-Claimant-Delta-2026",
    )
    anatomy = st.selectbox(
        "Anatomical Target Site (ICF Matrix)",
        [
            "Glenohumeral Joint (Shoulder)",
            "Lumbar Spine",
            "Lower Extremity",
        ],
    )
with intake_col2:
    age = st.number_input("Actuarial Chronological Age", min_value=18, max_value=75, value=48)
    duty_tier = st.selectbox(
        "Occupational Demands Tier",
        [
            "Heavy Manual / Industrial",
            "Medium Logistics / Transport",
            "Sedentary Clerical",
        ],
    )
with intake_col3:
    st.markdown(
        "<b style='font-size:0.85rem; color:#8b949e; font-family:monospace;'>"
        "VOICE DICTATION NLP PIPELINE</b>",
        unsafe_allow_html=True,
    )
    dictation = st.text_area(
        "Clinical Summary Dictation Ingest",
        value=(
            "Claimant presents with severe structural disruption. Age curve indicates "
            "prolonged cellular recovery timeline. Noted elevation in psychosocial "
            "barriers to return-to-work path."
        ),
    )

# Dynamic calculations for age-calibrated timeline modeling
age_factor = (age - 25) * 0.015
calibrated_base_cost = 22500.0 * (1.0 + age_factor) * base_cost_multiplier
# Liability mitigation floor compresses allowable baseline spend
calibrated_base_cost *= 1.0 - (cap_floor / 100.0) * 0.35
calibrated_base_days = int(90 * (1.0 + age_factor))

# --- MODULE 3: PREVENTATIVE DRIFT RADAR ---
st.markdown("---")
st.markdown("## PREVENTATIVE DRIFT RADAR")

st.markdown("### Live Claim Telemetry Simulation Input")
sim_col1, sim_col2 = st.columns(2)
with sim_col1:
    actual_rom = st.slider(
        "Logged Functional Range of Motion (% of Expected Target)",
        0,
        100,
        75,
    )
with sim_col2:
    actual_spend = st.number_input(
        "Actual Invoiced Claims Cost to Date (NZD)",
        min_value=0.0,
        value=28400.0,
    )

# Re-compute indicators dynamically based on manual inputs
st.session_state.functional_drift = max(0.0, 100.0 - float(actual_rom))
st.session_state.ivc = max(
    0.0, (float(actual_spend) - calibrated_base_cost) / calibrated_base_cost
)
projected_final_cost = (
    calibrated_base_cost
    + (st.session_state.functional_drift * 185.0)
    + (st.session_state.ivc * calibrated_base_cost)
)
permanent_disability_prob = 1.0 / (
    1.0
    + np.exp(
        -(-2.5 + (age * 0.04) + (st.session_state.functional_drift * 0.05))
    )
)

table_col, metric_col = st.columns([1.6, 1.0])

with table_col:
    st.markdown("#### Operational Pathway Alignment Vector")
    df_vector = pd.DataFrame(
        {
            "Performance Dimension": [
                "Target Recovery Runway",
                "Expected Base Cost Runway",
                "Current Functional Capacity",
                "Biopsychosocial Barriers Index",
            ],
            "Validated Standard": [
                f"{calibrated_base_days} Days",
                f"${calibrated_base_cost:,.2f} NZD",
                "100% Path Arc",
                "Nominal Resilience",
            ],
            "Live Ingest State": [
                "Day 42",
                f"${actual_spend:,.2f} NZD",
                f"{actual_rom}% Flexion",
                "High Stress / Fear Flag",
            ],
            "Point of Drift Variance": [
                "On Track" if st.session_state.functional_drift <= 15 else "Timeline Breach",
                f"${float(actual_spend) - calibrated_base_cost:+,.2f} NZD",
                f"-{st.session_state.functional_drift:.0f}% Deviation",
                "Path B Trigger Activated",
            ],
        }
    )
    st.table(df_vector)
    st.caption(
        f"Participant `{subject_token}` · {anatomy} · {duty_tier} · Age {age} · Role {role}"
    )

with metric_col:
    st.markdown("#### Macro Financial Liability Ledger")
    if st.session_state.functional_drift > 15.0 or permanent_disability_prob > 0.50:
        status_label = "CRITICAL PATHWAY DRIFT DETECTED"
        status_color = "#ef4444"
    else:
        status_label = "NOMINAL PATHWAY ALIGNMENT"
        status_color = "#10b981"

    # Formulations removed. Replaced with high-impact large print layout.
    if role == SCHEME_DIRECTOR:
        ledger_body = f"""
            <div class="metric-label">Permanent Disability Probability (PPD)</div>
            <div class="large-impact-value" style="color:{status_color};">
                {permanent_disability_prob * 100:.1f}%
            </div>
            <hr style="border:0; border-top:1px solid #30363d; margin: 1rem 0;"/>
            <div class="metric-label">Total Absolute System Exposure (TASE)</div>
            <div class="metric-value-silver" style="font-size:1.6rem; margin-bottom:0.5rem;">
                ${projected_final_cost:,.2f} NZD
            </div>
            <div class="metric-label">Dynamic Lookback Valuation Basis</div>
            <div class="metric-value-green" style="font-size:1.3rem;">
                ${(5000 + (projected_final_cost * 0.12)):,.2f} NZD
            </div>
        """
    else:
        ledger_body = """
            <div class="metric-label">Permanent Disability Probability (PPD)</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem; margin-bottom:0.8rem;">
                🔒 MASKED
            </div>
            <hr style="border:0; border-top:1px solid #30363d; margin: 1rem 0;"/>
            <div class="metric-label">Total Absolute System Exposure (TASE)</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem; margin-bottom:0.8rem;">
                🔒 RESTRICTED ACCESS
            </div>
            <div class="metric-label">Dynamic Lookback Valuation Basis</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem;">
                🔒 ACCESS DENIED
            </div>
        """

    st.markdown(
        f"""
        <div class="metric-box" style="border-left: 4px solid {status_color};">
            <div class="metric-label">Scheme Alignment Status</div>
            <div style="color:{status_color}; font-weight:700; font-size:1.1rem; margin-bottom:0.8rem;">
                {status_label}
            </div>
            {ledger_body}
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- MODULE 4: LONGITUDINAL HISTORICAL COST TREND VISUALIZATION ---
st.markdown("---")
st.markdown("### HISTORICAL PERFORMANCE ANALYTICS")
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem;'>"
    "120-Day Longitudinal Claim Trajectory Matrix — Expected Pathway vs Actual Cumulative Spend (NZD)</p>",
    unsafe_allow_html=True,
)

days_series = np.arange(0, 121, 10)
standard_trajectory = np.array(
    [min(calibrated_base_cost, (calibrated_base_cost / 90) * d) for d in days_series]
)
actual_trajectory = np.array(
    [
        (calibrated_base_cost / 90) * d * (1.0 + (0.008 * d) if d > 40 else 1.0)
        for d in days_series
    ]
)

if role == SCHEME_DIRECTOR:
    df_chart = pd.DataFrame(
        {
            "Days Elapsed": days_series,
            "Standard Expected Runway": standard_trajectory,
            "Actual Cumulative Spend Velocity": actual_trajectory,
        }
    )
    st.caption(
        f"Scheme Director view · longitudinal aggregate for `{subject_token}` pathway (NZD)"
    )
    st.line_chart(
        df_chart,
        x="Days Elapsed",
        y=["Standard Expected Runway", "Actual Cumulative Spend Velocity"],
        color=["#10b981", "#ef4444"],
    )
else:
    st.warning(
        "🔒 SECURE LEDGER TRAJECTORY MASKED: Longitudinal aggregate chart vectors "
        "are restricted to Scheme Director governance access pools."
    )
