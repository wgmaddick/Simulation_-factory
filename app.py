"""US Risk Orchestration Engine — executive operational risk governance.

Stark dark-theme portfolio surface with Clinical Triage Intake, Preventative
Drift Radar (asymmetrical high-real-estate layout), and Lookback License Fee
basis. Vault session keys remain initialized for Kinetic Lab continuity.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from capital_market import (
    DEFAULT_LOOKBACK_BASE_FEE_USD,
    compute_lookback_license_fee,
)
from config import TENANT_CONFIG

st.set_page_config(
    layout="wide",
    page_title="US Risk Orchestration Engine",
    page_icon="⬡",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 1. Stark Executive Dark Theme & Contrast UI Rig
# ---------------------------------------------------------------------------
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
    /* Industry Metric Card Highlights */
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
    /* Table Accessibility Wrap Overrides — no truncation on iPad */
    th, td,
    [data-testid="stTable"] th,
    [data-testid="stTable"] td,
    [data-testid="stTable"] table {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
        text-overflow: clip !important;
        overflow: visible !important;
        line-height: 1.4 !important;
        vertical-align: top !important;
    }
    [data-testid="stTable"] {
        width: 100% !important;
    }
    [data-testid="stTable"] table {
        width: 100% !important;
        table-layout: auto !important;
    }
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 2. Dynamic Variable Ingestion Layer (State Initialization)
# ---------------------------------------------------------------------------
def _init_session() -> None:
    if "ivc" not in st.session_state:
        st.session_state.ivc = 0.0
    if "functional_drift" not in st.session_state:
        st.session_state.functional_drift = 0.0
    # Kinetic Lab / vault continuity
    if "credits" not in st.session_state:
        st.session_state.credits = int(TENANT_CONFIG["initial_credits"])
    if "unlocked_nodes" not in st.session_state:
        st.session_state.unlocked_nodes = set()


_init_session()

# --- SIDEBAR: CONTROLS & DYNAMIC PARAMETER INJECTION ---
with st.sidebar:
    st.markdown("### GOVERNANCE LAYER")
    st.markdown(
        "<p style='color:#8b949e; font-size:0.85rem;'>"
        "Tiered Access Enforced • Secure Executive Vault</p>",
        unsafe_allow_html=True,
    )

    role = st.selectbox(
        "Active User Role Matrix",
        [
            "General Manager",
            "Caseworker / Analyst",
            "Technical Expert ('Docteur')",
        ],
    )

    st.markdown("---")
    st.markdown("### DYNAMIC MANDATE INJECTION")
    st.markdown(
        "<p style='color:#8b949e; font-size:0.85rem;'>"
        "Uncodified Parameter Override</p>",
        unsafe_allow_html=True,
    )

    target_reduction = st.slider("Enforce CapEx Mitigation Floor (%)", 0, 50, 15)
    custom_mandate = st.text_input(
        "Disseminate Strategic Mandate",
        placeholder="e.g., Prioritize Conservative Therapy Paths",
    )

    st.markdown("---")
    st.caption(
        f"Role: **{role}** · CapEx floor {target_reduction}% · "
        f"Vault credits {st.session_state.credits:,}"
    )
    if custom_mandate:
        st.caption(f"Active mandate: {custom_mandate}")
    st.caption("Open **Kinetic Lab** for live acquisition on unlocked research nodes.")


# --- MAIN EXECUTIVE VIEW: PORTFOLIO & ASSET LIFE RUNWAY ---
st.title("US RISK ORCHESTRATION ENGINE")
st.markdown(
    "<p style='color:#8b949e; margin-top:-10px;'>"
    "Sophisticated Operational Risk Governance in Simple Terms · "
    "Sovereign Case Management Surface</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Global Portfolio Layer 1 Widgets (The Top Metrics Bar)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        '<div class="metric-box"><div class="metric-label">Total Assets Protected</div>'
        '<div class="metric-value-silver">142 Cases</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        '<div class="metric-box"><div class="metric-label">Critical Point of Drift</div>'
        '<div class="metric-value-crimson">18 Subjects</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        '<div class="metric-box"><div class="metric-label">ODG Timeline Baseline Alignment</div>'
        '<div class="metric-value-green">87.3%</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        '<div class="metric-box"><div class="metric-label">Projected Indemnity Exposure</div>'
        '<div class="metric-value-silver">$412.5K</div></div>',
        unsafe_allow_html=True,
    )

# --- NESTED AUDIT ORACLE MATRIX (Drill-Down Framework) ---
st.markdown("### HIERARCHICAL AUDIT PORTALS")
with st.expander("AUDIT ORACLE: Operations & Asset Availability Tranche"):
    st.markdown("#### Dynamic Allocation Router (Central Funding Ledger)")
    st.info(
        "Central Capital approved. Current allocations meticulously tagged: "
        "[TARGET: Rehabilitation Substrate] - [SOURCE: Corporate Reserves] - "
        "[STATUS: Audited]"
    )

with st.expander("AUDIT ORACLE: R&D Funding & Intellectual Property Allocations"):
    st.info(
        "Research-node credit burn and kinetic methodology IP claims remain "
        "ledger-visible without exposing raw biometric source logs."
    )
    r1, r2 = st.columns(2)
    r1.metric("R&D Credit Burn", f"{int(TENANT_CONFIG['initial_credits']) - int(st.session_state.credits)}")
    r2.metric("Nodes Online", f"{len(st.session_state.unlocked_nodes)}")

with st.expander("AUDIT ORACLE: Marketing & Localized Consortium Cost-Offsets"):
    st.info(
        "Localized cost-offsets and early-adopter skin-in-the-game tracers for "
        "the Strategic Consortium Anchor — display-only, vault intact."
    )

# --- CLINICAL TRIAGE INTAKE (Multi-Modal Ingestion Gate) ---
st.markdown("### MODULE 1: CLINICAL TRIAGE INTAKE")
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem;'>"
    "Clinician Zero-Friction Capture (Video, Photographic & Speech NLP Pipeline)</p>",
    unsafe_allow_html=True,
)

intake_col1, intake_col2, intake_col3 = st.columns(3)
with intake_col1:
    subject_id = st.text_input(
        "Anonymized Subject Token",
        value="Asset_ID_Crypt_Delta_2026",
    )
    anatomy = st.selectbox(
        "Anatomical Target Site (ICF Matrix)",
        [
            "Glenohumeral Joint (Shoulder)",
            "Lumbar Spine",
            "Knee Extensor Mechanism",
        ],
    )
with intake_col2:
    age = st.number_input(
        "Actuarial Chronological Age",
        min_value=18,
        max_value=75,
        value=48,
    )
    occupation = st.selectbox(
        "Occupational Duty Tier",
        [
            "Heavy Industrial Laborer",
            "Medium Logistics / Operator",
            "Sedentary / Administrative",
        ],
    )
with intake_col3:
    st.markdown(
        "<b style='font-size:0.85rem; color:#8b949e; font-family:monospace;'>"
        "VOICE DICTATION NLP INGESTION</b>",
        unsafe_allow_html=True,
    )
    dictation = st.text_area(
        "Ambient Speech Notes",
        value=(
            "Patient exhibits partial thickness tear of the supraspinatus tendon. "
            "Chronological age capacity inflates baseline time metrics. High fear "
            "of re-injury noted, cognitive resilience score tracking low."
        ),
    )

# Dynamically modulate baseline cost and timeline using the core logic formulas
age_factor = (age - 25) * 0.015
base_cost = 22500.0 * (1.0 + age_factor)
base_days = int(90 * (1.0 + age_factor))

# Occupation duty multiplier for indemnity path pressure
occupation_mult = {
    "Heavy Industrial Laborer": 1.18,
    "Medium Logistics / Operator": 1.08,
    "Sedentary / Administrative": 1.0,
}.get(occupation, 1.0)
base_cost *= occupation_mult

# --- THE PREVENTATIVE DRIFT RADAR (High Real-Estate Vertical Realignment) ---
st.markdown("---")
st.markdown("## PREVENTATIVE DRIFT RADAR")
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem;'>"
    "Live Divergence Mapping and Retrospective Lookback Allocation Controls · "
    f"Subject <code>{subject_id}</code> · {anatomy}</p>",
    unsafe_allow_html=True,
)

# Interactive simulation controls mimicking the caseworker input loops
st.markdown("### Live Telemetry Simulation Overrides")
sim_col1, sim_col2 = st.columns(2)
with sim_col1:
    actual_rom = st.slider(
        "Current Functional Range of Motion (% of Expected)",
        0,
        100,
        75,
    )
with sim_col2:
    actual_spend = st.number_input(
        "Actual Invoiced Expense to Date (USD)",
        min_value=0.0,
        value=28400.0,
    )

# Calculate live functional drift and input variance metrics
st.session_state.functional_drift = max(0.0, 100.0 - float(actual_rom))
st.session_state.ivc = max(0.0, (float(actual_spend) - base_cost) / base_cost)

# Dynamic cost escalation math projection
projected_final_cost = (
    base_cost
    + (st.session_state.functional_drift * 185.0)
    + (st.session_state.ivc * base_cost)
)
permanent_disability_prob = 1.0 / (
    1.0
    + np.exp(
        -(
            -2.5
            + (float(age) * 0.04)
            + (st.session_state.functional_drift * 0.05)
        )
    )
)

# Lookback License Fee — performance valuation (drift index from IVC + functional drift)
composite_drift_index = min(
    3.0,
    (st.session_state.ivc * 0.55)
    + (st.session_state.functional_drift / 100.0 * 0.90),
)
lookback = compute_lookback_license_fee(
    {"composite_drift_index": composite_drift_index},
    base_fee_usd=max(DEFAULT_LOOKBACK_BASE_FEE_USD * 0.04, 5000.0),
)
# Presentation fee also tracks TASE premium path from the executive brief
lookback_display = 5000.0 + (projected_final_cost * 0.12)

# CapEx mitigation floor from sidebar mandate
mitigated_exposure = projected_final_cost * (1.0 - target_reduction / 100.0)

# The Asymmetrical Layout Matrix to maximize iPad readability
table_col, metric_col = st.columns([1.6, 1.0])

with table_col:
    st.markdown("#### Physical Alignment Vector vs. Expected Target")
    df_physical = pd.DataFrame(
        {
            "Metric Dimension": [
                "ODG Timeline Envelope",
                "Expected Base Cost",
                "Functional Range of Motion",
                "Biopsychosocial Risk (ICF)",
            ],
            "Validated Baseline": [
                f"{base_days} Days",
                f"${base_cost:,.2f}",
                "100% Target Arc",
                "Nominal Resilience",
            ],
            "Live Ingestion State": [
                "Day 42",
                f"${actual_spend:,.2f}",
                f"{actual_rom}% Flexion",
                "High Fear/Stress Flag",
            ],
            "Point of Drift Delta": [
                "On Track",
                f"${float(actual_spend) - base_cost:+,.2f}",
                f"-{st.session_state.functional_drift}% Variance",
                "Path B Trigger Alert",
            ],
        }
    )
    st.table(df_physical)
    if dictation:
        with st.expander("Ambient Speech Notes (NLP capture)", expanded=False):
            st.text(dictation)

with metric_col:
    st.markdown("#### Macro Financial Liability & Lookback Valuation")

    # Check conditional severity to alter lookback warnings
    if st.session_state.functional_drift > 15.0 or permanent_disability_prob > 0.50:
        status_color = "crimson"
        status_label = "CRITICAL PATHWAY DRIFT WARNING"
    else:
        status_color = "green"
        status_label = "NOMINAL SYSTEMIC ALIGNMENT"

    border = "#ef4444" if status_color == "crimson" else "#10b981"
    label_color = border
    ppd_color = "#ef4444" if permanent_disability_prob > 0.50 else "#e2e8f0"

    st.markdown(
        f"""
        <div class="metric-box" style="border-left: 4px solid {border};">
            <div class="metric-label">Platform Governance Status</div>
            <div style="color:{label_color}; font-weight:700; font-size:1.1rem; margin-bottom:0.8rem;">
                {status_label}
            </div>
            <div class="metric-label">Projected Total Case Cost (TASE)</div>
            <div class="metric-value-silver">${projected_final_cost:,.2f}</div>
            <div class="metric-label" style="margin-top:0.8rem;">
                CapEx-Mitigated Exposure ({target_reduction}% floor)
            </div>
            <div class="metric-value-silver" style="font-size:1.35rem;">
                ${mitigated_exposure:,.2f}
            </div>
            <div class="metric-label" style="margin-top:0.8rem;">
                Probability of Permanent Disability (PPD)
            </div>
            <div class="metric-value-crimson" style="color: {ppd_color};">
                {permanent_disability_prob * 100:.1f}%
            </div>
            <div class="metric-label" style="margin-top:0.8rem;">
                Dynamic Lookback License Premium Fee Basis
            </div>
            <div class="metric-value-green">${lookback_display:,.2f}</div>
            <div class="metric-label" style="margin-top:0.55rem;">
                Valuation Engine Fee (drift index {composite_drift_index:.3f})
            </div>
            <div style="color:#10b981; font-weight:700; font-size:1.1rem;">
                ${lookback["live_lookback_license_fee_usd"]:,.2f}
            </div>
            <div class="metric-label" style="margin-top:0.55rem;">Input Variance Coefficient (IVC)</div>
            <div style="color:#e2e8f0; font-weight:700; font-size:1.2rem;">
                {st.session_state.ivc:.4f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Automated Remediate / Escalate Action Panel Gate
    if status_color == "crimson":
        st.error(
            "SYSTEMIC DRIFT THRESHOLD BREACHED: Unaddressed drift is inflating "
            "long-tail capital liabilities."
        )
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Initiate Pathway Acceleration", use_container_width=True):
                st.success(
                    "Authorized: Swapping to dynamic ODG rehabilitation sub-pathway."
                )
        with btn_col2:
            if st.button("Log Mandate Compliance Exception", use_container_width=True):
                st.info(
                    "Cryptographic data provenance receipt stamped into vault."
                )
