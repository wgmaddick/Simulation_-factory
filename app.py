"""AAT Scheme Performance Engine — predictive operational risk governance.

High-contrast sovereign dark theme with a master claims ledger, global portfolio
summary deck, and individual claim drill-down (auto-hydrated clinical profiles).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

LAYOUT_LOCKED = True
SCHEME_DIRECTOR = "Scheme Director (GM)"
GLOBAL_VIEW = "Global Scheme Portfolio (All Active Claims)"
NEW_CLAIM_VIEW = "➕ Log New Claimant Profile"
DUTY_OPTIONS = [
    "Heavy Manual / Industrial",
    "Medium Logistics / Transport",
    "Sedentary Clerical",
]
ANATOMY_OPTIONS = [
    "Glenohumeral Joint (Shoulder)",
    "Lumbar Spine",
    "Lower Extremity (Knee)",
]

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

if "ivc" not in st.session_state:
    st.session_state.ivc = 0.0
if "functional_drift" not in st.session_state:
    st.session_state.functional_drift = 0.0


# --- MASTER CLAIMS DATABASE CORE (Simulating Live Institutional Records) ---
@st.cache_data
def load_internal_portfolio_ledger() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Claim_ID": "AAT-Claimant-Delta-2026",
                "Anatomy": "Glenohumeral Joint (Shoulder)",
                "Age": 48,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 62.0,
                "Spend_To_Date": 28400.0,
                "Status": "CRITICAL DRIFT",
            },
            {
                "Claim_ID": "AAT-Claimant-Epsilon-2026",
                "Anatomy": "Lumbar Spine",
                "Age": 32,
                "Demands": "Sedentary Clerical",
                "ROM_Actual": 94.0,
                "Spend_To_Date": 12100.0,
                "Status": "NOMINAL ALIGNMENT",
            },
            {
                "Claim_ID": "AAT-Claimant-Zeta-2026",
                "Anatomy": "Lower Extremity (Knee)",
                "Age": 61,
                "Demands": "Heavy Manual / Industrial",
                "ROM_Actual": 48.0,
                "Spend_To_Date": 41200.0,
                "Status": "CRITICAL DRIFT",
            },
            {
                "Claim_ID": "AAT-Claimant-Eta-2026",
                "Anatomy": "Glenohumeral Joint (Shoulder)",
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
            "Claimant presents with severe shoulder tear. Structural guard present. "
            "Psychosocial barriers tracking elevated."
        )
    if "Zeta" in claim_id:
        return (
            "Advanced tissue damage in knee construct. Cellular age curves signal slow "
            "remodeling. High risk of long-term displacement."
        )
    return (
        "Favorable tissue consistency. Functional compliance target arc tracking high. "
        "Psychological resilience nominal."
    )


def _job_params(duty_tier: str) -> tuple[float, float, float]:
    if "Heavy" in duty_tier:
        return 1.30, 28.0, 1.35
    if "Medium" in duty_tier:
        return 1.10, 15.0, 1.12
    return 0.90, 5.0, 0.95


def emulate_live_telemetry(age: int, duty_tier: str, cap_floor: int) -> tuple[float, float]:
    """Derive ROM + spend from age/duty for new claimant live editing."""
    job_multiplier, rom_loss, spend_variance = _job_params(duty_tier)
    age_factor = (age - 25) * 0.015
    base_cost = 22500.0 * (1.0 + age_factor) * job_multiplier
    base_cost *= 1.0 - (cap_floor / 100.0) * 0.35
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
    calibrated_base_cost *= 1.0 - (cap_floor / 100.0) * 0.35
    calibrated_base_days = max(1, int(90 * (1.0 + age_factor) * job_multiplier))

    functional_drift = 100.0 - actual_rom
    ivc = (actual_spend - calibrated_base_cost) / calibrated_base_cost
    projected_final_cost = (
        calibrated_base_cost
        + (functional_drift * 185.0)
        + (ivc * calibrated_base_cost)
    )
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
        "permanent_disability_prob": float(permanent_disability_prob),
    }


df_master_ledger = load_internal_portfolio_ledger()
claim_ids = df_master_ledger["Claim_ID"].tolist()

# --- SIDEBAR: GOVERNANCE LAYER FILTERS ---
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

# --- MAIN PERFORMANCE DASHBOARD TITLE ---
st.title("AAT SCHEME PERFORMANCE ENGINE")
st.markdown(
    "<p style='color:#8b949e; margin-top:-10px;'>"
    "Predictive Operational Risk & Long-Tail Claims Governance Framework</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- CENTRAL ROUTING SELECTOR: THE DRILL-DOWN MECHANISM ---
selector_col1, selector_col2 = st.columns([2, 1])
with selector_col1:
    view_selection = st.selectbox(
        "AUDIT VIEW COMMAND SECTOR",
        [GLOBAL_VIEW, NEW_CLAIM_VIEW, *claim_ids],
    )
with selector_col2:
    st.caption("Portfolio · new claimant log · or Claim_ID deep-dive.")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# INTERFACE LAYER A: GLOBAL SCHEME PORTFOLIO VIEW (THE DIRECTOR'S SUMMARY DECK)
# ==============================================================================
if view_selection == GLOBAL_VIEW:
    critical_count = int((df_master_ledger["Status"] == "CRITICAL DRIFT").sum())
    nominal_count = int((df_master_ledger["Status"] == "NOMINAL ALIGNMENT").sum())
    ledger_n = int(len(df_master_ledger))
    # Demo macro bar retains institutional scale; ledger below shows live sample cohort
    display_cases = 142
    display_drift = 18
    display_alignment = "85.9%"
    display_exposure = "$876.5K"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="metric-box"><div class="metric-label">Total Scheme Claims</div>'
            f'<div class="metric-value-silver">{display_cases}</div>'
            f'<div class="metric-subtext">Active Files Across Region'
            f' · sample ledger {ledger_n}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-box"><div class="metric-label">Critical Pathway Drift</div>'
            f'<div class="metric-value-crimson">{display_drift}</div>'
            f'<div class="metric-subtext">Requires Immediate Remediation'
            f' · sample critical {critical_count}</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-box"><div class="metric-label">Aggregate Performance Index</div>'
            f'<div class="metric-value-green">{display_alignment}</div>'
            f'<div class="metric-subtext">Baseline Trajectory Target'
            f' · sample nominal {nominal_count}</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        if role == SCHEME_DIRECTOR:
            st.markdown(
                f'<div class="metric-box"><div class="metric-label">Projected Scheme Liability</div>'
                f'<div class="metric-value-silver">{display_exposure}</div>'
                f'<div class="metric-subtext">Total Forecasted NZD Pool</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="metric-box"><div class="metric-label">Projected Scheme Liability</div>'
                '<div style="color:#8b949e; font-size:1.1rem; font-weight:700; margin-top:0.5rem;">'
                "🔒 RESTRICTED</div>"
                '<div class="metric-subtext">Requires GM Level</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("### MASTER CLAIMS ACCOUNTABILITY LEDGER")
    st.markdown(
        "<p style='color:#8b949e; font-size:0.9rem; margin-top:-10px;'>"
        "Real-time tracking of active asset classes. Select an individual token in the "
        "command sector above to deep-dive unique physical parameters.</p>",
        unsafe_allow_html=True,
    )

    df_formatted_ledger = df_master_ledger.copy()
    df_formatted_ledger["Spend_To_Date"] = df_formatted_ledger["Spend_To_Date"].map(
        lambda x: f"${x:,.2f} NZD"
    )
    df_formatted_ledger["ROM_Actual"] = df_formatted_ledger["ROM_Actual"].map(
        lambda x: f"{x:.1f}% Target Arc"
    )
    st.table(df_formatted_ledger)

    st.markdown("---")
    st.markdown("### AGGREGATE SCHEME CAPEX VELOCITY TRAJECTORY")

    days_series = np.arange(0, 121, 10)
    standard_macro = 25000 * 3 * (days_series / 90)
    standard_macro = np.clip(standard_macro, 0, 25000 * 3)
    actual_macro = 25000 * 3 * (days_series / 90) * (1.0 + (0.006 * days_series))

    if role == SCHEME_DIRECTOR:
        df_macro_chart = pd.DataFrame(
            {
                "Days Elapsed": days_series,
                "Target Operational Runway": standard_macro,
                "Actual Scheme Cumulative Outflow": actual_macro,
            }
        )
        st.caption("Scheme-wide CapEx velocity · Director clearance")
        st.line_chart(
            df_macro_chart,
            x="Days Elapsed",
            y=["Target Operational Runway", "Actual Scheme Cumulative Outflow"],
            color=["#10b981", "#ef4444"],
        )
    else:
        st.warning(
            "🔒 SECURE LEDGER TRAJECTORY MASKED: Longitudinal aggregate macro trends "
            "are restricted to Scheme Director access pools."
        )

# ==============================================================================
# INTERFACE LAYER B/C: INDIVIDUAL DRILL-DOWN OR NEW CLAIMANT LOG
# ==============================================================================
else:
    is_new_claim = view_selection == NEW_CLAIM_VIEW

    if is_new_claim:
        st.markdown("### LOG NEW CLAIMANT PROFILE")
        st.caption(
            "Unlocked triage intake · live actuarial recalculation as fields change"
        )
        claim_status = "DRAFT — UNSAVED"
        intake_col1, intake_col2, intake_col3 = st.columns(3)
        with intake_col1:
            subject_token = st.text_input(
                "Participant Identifier Token",
                value="",
                placeholder="e.g., AAT-Claimant-Theta-2026",
            )
            anatomy = st.selectbox(
                "Anatomical Target Site (ICF Matrix)",
                ANATOMY_OPTIONS,
                index=0,
            )
        with intake_col2:
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
        with intake_col3:
            st.markdown(
                "<b style='font-size:0.85rem; color:#8b949e; font-family:monospace;'>"
                "VOICE DICTATION NLP RECORD</b>",
                unsafe_allow_html=True,
            )
            dictation = st.text_area(
                "Clinical Summary Dictation Ingest",
                value="Type or dictate clinical triage notes here...",
            )
        # Live telemetry emulation from unlocked age / duty inputs
        actual_rom, actual_spend = emulate_live_telemetry(
            int(age), str(duty_tier), int(cap_floor)
        )
        display_token = subject_token.strip() or "NEW-CLAIMANT-DRAFT"
    else:
        selected_row = df_master_ledger[
            df_master_ledger["Claim_ID"] == view_selection
        ].iloc[0]

        subject_token = str(selected_row["Claim_ID"])
        anatomy = str(selected_row["Anatomy"])
        age = int(selected_row["Age"])
        duty_tier = str(selected_row["Demands"])
        actual_rom = float(selected_row["ROM_Actual"])
        actual_spend = float(selected_row["Spend_To_Date"])
        claim_status = str(selected_row["Status"])
        display_token = subject_token

        st.markdown(f"### INDIVIDUAL CLAIM AUDIT: `{subject_token}`")
        st.caption(
            f"Ledger status: **{claim_status}** · hydrated from master portfolio core"
        )

        intake_col1, intake_col2, intake_col3 = st.columns(3)
        with intake_col1:
            st.text_input(
                "Participant Identifier Token",
                value=subject_token,
                disabled=True,
            )
            st.text_input(
                "Anatomical Target Site (ICF Matrix)",
                value=anatomy,
                disabled=True,
            )
        with intake_col2:
            st.number_input(
                "Actuarial Chronological Age",
                value=age,
                disabled=True,
            )
            st.text_input(
                "Occupational Demands Tier",
                value=duty_tier,
                disabled=True,
            )
        with intake_col3:
            st.markdown(
                "<b style='font-size:0.85rem; color:#8b949e; font-family:monospace;'>"
                "VOICE DICTATION NLP RECORD</b>",
                unsafe_allow_html=True,
            )
            dictation = st.text_area(
                "Clinical Summary Dictation Ingest",
                value=dictation_for_claim(subject_token),
                disabled=True,
            )

    # Optional: enrich barrier flag from live/new dictation text
    barrier_hot = any(
        k in str(dictation).lower()
        for k in ("fear", "stress", "barrier", "tear", "damage", "risk")
    )

    metrics = compute_claim_metrics(
        age=int(age),
        duty_tier=str(duty_tier),
        actual_rom=float(actual_rom),
        actual_spend=float(actual_spend),
        cap_floor=int(cap_floor),
    )
    st.session_state.functional_drift = metrics["functional_drift"]
    st.session_state.ivc = metrics["ivc"]
    calibrated_base_cost = metrics["calibrated_base_cost"]
    calibrated_base_days = int(metrics["calibrated_base_days"])
    projected_final_cost = metrics["projected_final_cost"]
    permanent_disability_prob = metrics["permanent_disability_prob"]

    if is_new_claim:
        st.info(
            f"Live draft · `{display_token}` · {anatomy} · Age {int(age)} · {duty_tier} · "
            f"ROM {actual_rom:.1f}% · Spend ${actual_spend:,.0f} NZD (auto-calibrated)"
        )

    st.markdown("---")
    st.markdown("## PREVENTATIVE DRIFT RADAR DEEP-DIVE")

    table_col, metric_col = st.columns([1.6, 1.0])

    with table_col:
        st.markdown("#### Operational Pathway Alignment Vector")
        barrier_label = (
            "High Stress / Fear Flag"
            if (st.session_state.functional_drift > 10 or barrier_hot)
            else "Nominal"
        )
        path_label = (
            "Path B Trigger Activated"
            if st.session_state.functional_drift > 15
            else "Clear"
        )
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
                    barrier_label,
                ],
                "Point of Drift Variance": [
                    "On Track"
                    if st.session_state.functional_drift <= 15
                    else "Timeline Breach",
                    f"${actual_spend - calibrated_base_cost:+,.2f} NZD",
                    f"-{st.session_state.functional_drift:.1f}% Deviation",
                    path_label,
                ],
            }
        )
        st.table(df_vector)

    with metric_col:
        st.markdown("#### Macro Financial Liability Ledger")
        if (
            st.session_state.functional_drift > 15.0
            or permanent_disability_prob > 0.50
        ):
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

    st.markdown("### INDIVIDUAL PERFORMANCE TIME-COST AXIS")
    days_series = np.arange(0, calibrated_base_days + 31, 10)
    standard_trajectory = np.array(
        [
            min(calibrated_base_cost, (calibrated_base_cost / calibrated_base_days) * d)
            for d in days_series
        ]
    )

    if st.session_state.functional_drift > 15:
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
        actual_trajectory = standard_trajectory * (1.0 + (st.session_state.ivc * 0.5))

    if role == SCHEME_DIRECTOR:
        df_chart = pd.DataFrame(
            {
                "Days Elapsed": days_series,
                "Standard Expected Runway": standard_trajectory,
                "Actual Cumulative Spend Velocity": actual_trajectory,
            }
        )
        st.caption(
            f"{'Live draft' if is_new_claim else 'Individual'} axis · "
            f"`{display_token}` · {duty_tier} · Age {int(age)} · "
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
            "🔒 SECURE LEDGER TRAJECTORY MASKED: Specific individual target vectors "
            "are restricted to Scheme Director access pools."
        )
