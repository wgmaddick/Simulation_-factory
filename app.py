"""AAT Scheme Performance Engine — predictive operational risk governance.

High-contrast sovereign dark theme. Clinical triage intake is the single engine
driver: age + occupational tier auto-calibrate drift, spend, PPD, and NZD exposure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

LAYOUT_LOCKED = True
SCHEME_DIRECTOR = "Scheme Director (GM)"

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
        padding: 1.2rem;
        margin-bottom: 1rem;
        min-height: 110px;
    }
    .metric-label {
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.82rem;
        text-transform: uppercase;
        color: #8b949e;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .metric-value-silver {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1.1;
    }
    .metric-value-crimson {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ef4444;
        line-height: 1.1;
    }
    .metric-value-green {
        font-size: 2.2rem;
        font-weight: 700;
        color: #10b981;
        line-height: 1.1;
    }
    .metric-subtext {
        font-size: 0.88rem;
        color: #8b949e;
        margin-top: 0.3rem;
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

# MODULE 1: CLINICAL INTAKE MODALITY (THE SINGLE ENGINE DRIVER)
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

# --- THE LIVE AUTOMATED METRIC GENERATOR ---
# A. Compute Occupation Impact Factor
if duty_tier == "Heavy Manual / Industrial":
    job_multiplier = 1.30
    simulated_rom_loss = 28.0
    spend_variance_factor = 1.35
elif duty_tier == "Medium Logistics / Transport":
    job_multiplier = 1.10
    simulated_rom_loss = 15.0
    spend_variance_factor = 1.12
else:
    job_multiplier = 0.90
    simulated_rom_loss = 5.0
    spend_variance_factor = 0.95

# B. Compute Age Curve Impact Factor
age_factor = (age - 25) * 0.015

# C. Calibrate Dynamic Baselines Natively
calibrated_base_cost = 22500.0 * (1.0 + age_factor) * job_multiplier
# Mandate floor compresses allowable baseline spend without breaking the driver loop
calibrated_base_cost *= 1.0 - (cap_floor / 100.0) * 0.35
calibrated_base_days = max(1, int(90 * (1.0 + age_factor) * job_multiplier))

# D. Automated Telemetry Emulation (Simulating data pulled from Live Invoices / ML Video)
# Older age and heavier jobs naturally scale physiological debt and cost accumulation
actual_rom = max(40.0, 100.0 - simulated_rom_loss - (age_factor * 25.0))
st.session_state.functional_drift = 100.0 - actual_rom

actual_spend = calibrated_base_cost * spend_variance_factor * (1.0 + (age_factor * 0.2))
st.session_state.ivc = (actual_spend - calibrated_base_cost) / calibrated_base_cost

projected_final_cost = (
    calibrated_base_cost
    + (st.session_state.functional_drift * 185.0)
    + (st.session_state.ivc * calibrated_base_cost)
)
permanent_disability_prob = 1.0 / (
    1.0
    + np.exp(
        -(-2.8 + (age * 0.045) + (st.session_state.functional_drift * 0.055))
    )
)

# Macro Top Metrics Bar (Reflecting dynamic output changes natively)
st.markdown("### ACTIVE PROFILE STATUS SUMMARY")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="metric-box"><div class="metric-label">Active Claim Profile</div>'
        f'<div class="metric-value-silver" style="font-size:1.3rem; padding-top:0.4rem;">'
        f"{subject_token}</div>"
        f'<div class="metric-subtext">{anatomy}</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    drift_status_txt = "CRITICAL" if st.session_state.functional_drift > 15.0 else "NOMINAL"
    drift_value_class = (
        "metric-value-crimson" if drift_status_txt == "CRITICAL" else "metric-value-green"
    )
    st.markdown(
        f'<div class="metric-box"><div class="metric-label">Drift Classification</div>'
        f'<div class="{drift_value_class}">{drift_status_txt}</div>'
        f'<div class="metric-subtext">{st.session_state.functional_drift:.1f}% Path Variance</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    perf_idx = max(10, int(100 - st.session_state.functional_drift))
    st.markdown(
        f'<div class="metric-box"><div class="metric-label">Calculated Pathway Index</div>'
        f'<div class="metric-value-green">{perf_idx}%</div>'
        f'<div class="metric-subtext">Target Alignment Arc</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    if role == SCHEME_DIRECTOR:
        st.markdown(
            f'<div class="metric-box"><div class="metric-label">Projected Liability</div>'
            f'<div class="metric-value-silver">${projected_final_cost:,.0f}</div>'
            f'<div class="metric-subtext">Total Forecasted NZD</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Projected Liability</div>'
            '<div style="color:#8b949e; font-size:1.1rem; font-weight:700; margin-top:0.5rem;">'
            "🔒 RESTRICTED</div>"
            '<div class="metric-subtext">Requires GM Level</div></div>',
            unsafe_allow_html=True,
        )

# Soft signal from dictation — does not override the automated driver
_ = dictation  # retained for future NLP enrichment of Path B flags

# --- MODULE 2: PREVENTATIVE DRIFT RADAR VECTOR MATRICES ---
st.markdown("---")
st.markdown("## PREVENTATIVE DRIFT RADAR")

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
                f"{actual_rom:.1f}% Flexion",
                "High Stress / Fear Flag",
            ],
            "Point of Drift Variance": [
                "On Track" if st.session_state.functional_drift <= 15 else "Timeline Breach",
                f"${actual_spend - calibrated_base_cost:+,.2f} NZD",
                f"-{st.session_state.functional_drift:.1f}% Deviation",
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

    if role == SCHEME_DIRECTOR:
        html_payload = f"""
        <div class="metric-box" style="border-left: 4px solid {status_color}; min-height: 290px;">
            <div class="metric-label">Scheme Alignment Status</div>
            <div style="color:{status_color}; font-weight:700; font-size:1.1rem; margin-bottom:0.8rem;">{status_label}</div>
            <div class="metric-label">Permanent Disability Probability (PPD)</div>
            <div class="large-impact-value" style="color:{status_color};">{permanent_disability_prob * 100:.1f}%</div>
            <hr style="border:0; border-top:1px solid #30363d; margin: 1rem 0;"/>
            <div class="metric-label">Total Absolute System Exposure (TASE)</div>
            <div class="metric-value-silver" style="font-size:1.6rem; margin-bottom:0.5rem;">${projected_final_cost:,.2f} NZD</div>
            <div class="metric-label">Dynamic Lookback Valuation Basis</div>
            <div class="metric-value-green" style="font-size:1.3rem;">${(5000 + (projected_final_cost * 0.12)):,.2f} NZD</div>
        </div>
        """
    else:
        html_payload = f"""
        <div class="metric-box" style="border-left: 4px solid {status_color}; min-height: 290px;">
            <div class="metric-label">Scheme Alignment Status</div>
            <div style="color:{status_color}; font-weight:700; font-size:1.1rem; margin-bottom:0.8rem;">{status_label}</div>
            <div class="metric-label">Permanent Disability Probability (PPD)</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem; margin-bottom:0.8rem;">🔒 MASKED</div>
            <hr style="border:0; border-top:1px solid #30363d; margin: 1rem 0;"/>
            <div class="metric-label">Total Absolute System Exposure (TASE)</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem; margin-bottom:0.8rem;">🔒 RESTRICTED ACCESS</div>
            <div class="metric-label">Dynamic Lookback Valuation Basis</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem;">🔒 ACCESS DENIED</div>
        </div>
        """

    st.markdown(html_payload, unsafe_allow_html=True)

# --- MODULE 3: LONGITUDINAL HISTORICAL COST TREND VISUALIZATION ---
st.markdown("---")
st.markdown("### HISTORICAL PERFORMANCE ANALYTICS")
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem;'>"
    "Dynamic Longitudinal Claim Trajectory Matrix — Calibrated Baseline Runway vs Actual Cumulative Spend</p>",
    unsafe_allow_html=True,
)

days_series = np.arange(0, calibrated_base_days + 31, 10)
standard_trajectory = np.array(
    [
        min(calibrated_base_cost, (calibrated_base_cost / calibrated_base_days) * d)
        for d in days_series
    ]
)
actual_trajectory = np.array(
    [
        (calibrated_base_cost / calibrated_base_days)
        * d
        * (1.0 + (0.007 * d) if d > (calibrated_base_days * 0.4) else 1.0)
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
        f"Auto-calibrated runway · `{subject_token}` · {duty_tier} · Age {age} · "
        f"{calibrated_base_days}-day horizon (NZD)"
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
