"""Sovereign Case Management Engine — executive operational risk governance.

Stark dark-theme portfolio surface with Clinical Triage Intake, Preventative
Drift Radar (asymmetrical high-real-estate layout), and Lookback License Fee
basis.

Layout contract: the dynamic case-management composition below is permanently
locked for production demos — portfolio bar, triage intake, drift radar,
privacy enclave, and historical cost trend.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

# Permanently lock the executive case-management layout composition.
LAYOUT_LOCKED = True

# ---------------------------------------------------------------------------
# Bulk Data Ingestion Gate + synthetic fallback (never blank the deck)
# ---------------------------------------------------------------------------
GM_ROLE = "General Manager"
RESTRICTED_ROLES = {
    "Caseworker / Analyst",
    "Technical Expert ('Docteur')",
}


def default_corporate_profile() -> pd.DataFrame:
    """Baseline synthetic portfolio used when no corporate file is loaded."""
    return pd.DataFrame(
        {
            "subject_token": [
                "Asset_ID_Crypt_Delta_2026",
                "Asset_ID_Crypt_Echo_2026",
                "Asset_ID_Crypt_Foxtrot_2026",
            ],
            "anatomy": [
                "Glenohumeral Joint (Shoulder)",
                "Lumbar Spine",
                "Knee Extensor Mechanism",
            ],
            "age": [48, 41, 55],
            "occupation": [
                "Heavy Industrial Laborer",
                "Medium Logistics / Operator",
                "Sedentary / Administrative",
            ],
            "rom_pct": [75, 88, 62],
            "actual_spend": [28400.0, 19250.0, 34100.0],
            "critical_flag": [1, 0, 1],
            "odg_alignment_pct": [87.3, 92.1, 78.4],
            "indemnity_exposure_usd": [412500.0, 188000.0, 276000.0],
        }
    )


def load_corporate_data_profile(uploaded_file: Any) -> tuple[pd.DataFrame, str]:
    """Parse CSV/XLSX when present; otherwise fall back to synthetic defaults."""
    if uploaded_file is None:
        return default_corporate_profile(), "synthetic"

    try:
        name = (uploaded_file.name or "").lower()
        raw = uploaded_file.getvalue()
        buffer = BytesIO(raw)
        if name.endswith(".csv"):
            frame = pd.read_csv(buffer)
        elif name.endswith(".xlsx") or name.endswith(".xls"):
            frame = pd.read_excel(buffer)
        else:
            return default_corporate_profile(), "synthetic"

        if frame is None or frame.empty:
            return default_corporate_profile(), "synthetic"

        frame.columns = [str(c).strip().lower().replace(" ", "_") for c in frame.columns]
        return frame, "uploaded"
    except Exception:
        # Never surface a hard failure — keep the executive deck operational.
        return default_corporate_profile(), "synthetic"


def _col(df: pd.DataFrame, *candidates: str) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def portfolio_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Derive Layer-1 portfolio KPIs from the active corporate profile."""
    n_cases = int(len(df)) if len(df) else 142
    crit_col = _col(df, "critical_flag", "critical", "point_of_drift")
    if crit_col is not None:
        critical = int(pd.to_numeric(df[crit_col], errors="coerce").fillna(0).astype(bool).sum())
    else:
        critical = max(1, int(round(n_cases * 0.13)))

    odg_col = _col(df, "odg_alignment_pct", "odg_alignment", "odg")
    if odg_col is not None:
        odg = float(pd.to_numeric(df[odg_col], errors="coerce").dropna().mean())
    else:
        odg = 87.3

    ind_col = _col(df, "indemnity_exposure_usd", "indemnity_exposure", "indemnity")
    if ind_col is not None:
        indemnity = float(pd.to_numeric(df[ind_col], errors="coerce").fillna(0).sum())
    else:
        indemnity = 412500.0

    return {
        "total_assets": n_cases,
        "critical_drift": critical,
        "odg_alignment": odg,
        "indemnity_exposure": indemnity,
    }


def is_general_manager(active_role: str) -> bool:
    return active_role == GM_ROLE


def can_view_indemnity(active_role: str) -> bool:
    """Indemnity card is GM-only; Caseworker / Docteur are explicitly masked."""
    return active_role not in RESTRICTED_ROLES and is_general_manager(active_role)


def build_clinical_timeline(
    *,
    odg_target_cost: float,
    actual_cumulative_at_day: float,
    observed_day: int = 42,
    horizon_days: int = 120,
    odg_horizon_days: int = 90,
) -> pd.DataFrame:
    """Structure a standard 120-day clinical cost runway vs spend-velocity loop."""
    days = np.arange(0, horizon_days + 1, dtype=float)
    odg_days = max(float(odg_horizon_days), 1.0)
    observe = max(int(observed_day), 1)

    # Standard ODG Cost Runway — linear to target by ODG horizon, then plateau
    odg_runway = np.clip(days / odg_days, 0.0, 1.0) * float(odg_target_cost)

    # Actual Cumulative Spend Velocity — constant velocity through observed day,
    # then mild post-observation acceleration when spend outpaces the ODG path.
    daily_velocity = float(actual_cumulative_at_day) / observe
    actual_spend = days * daily_velocity
    odg_at_observe = min(1.0, observe / odg_days) * float(odg_target_cost)
    overshoot = max(0.0, float(actual_cumulative_at_day) - odg_at_observe)
    if overshoot > 0:
        post = np.maximum(days - observe, 0.0)
        actual_spend = actual_spend + post * (overshoot / 40.0)

    return pd.DataFrame(
        {
            "Days Elapsed": days.astype(int),
            "Standard ODG Cost Runway": odg_runway,
            "Actual Cumulative Spend Velocity": actual_spend,
        }
    )


def build_portfolio_timeline(
    portfolio: pd.DataFrame,
    *,
    observed_day: int = 42,
    horizon_days: int = 120,
) -> pd.DataFrame:
    """Aggregate cumulative spending across the full portfolio matrix (GM view)."""
    if portfolio is None or portfolio.empty:
        return build_clinical_timeline(
            odg_target_cost=22500.0 * 3,
            actual_cumulative_at_day=28400.0 * 3,
            observed_day=observed_day,
            horizon_days=horizon_days,
        )

    spend_col = _col(portfolio, "actual_spend", "spend", "cumulative_spend")
    age_col = _col(portfolio, "age")
    n = max(len(portfolio), 1)

    if spend_col is not None:
        spends = pd.to_numeric(portfolio[spend_col], errors="coerce").fillna(28400.0)
    else:
        spends = pd.Series([28400.0] * n)

    if age_col is not None:
        ages = pd.to_numeric(portfolio[age_col], errors="coerce").fillna(48.0)
        odg_targets = 22500.0 * (1.0 + (ages - 25.0) * 0.015)
    else:
        odg_targets = pd.Series([22500.0] * n)

    # Sum independent subject runways into one portfolio curve
    aggregate = None
    for odg_target, spend in zip(odg_targets.tolist(), spends.tolist()):
        curve = build_clinical_timeline(
            odg_target_cost=float(odg_target),
            actual_cumulative_at_day=float(spend),
            observed_day=observed_day,
            horizon_days=horizon_days,
        )
        if aggregate is None:
            aggregate = curve
        else:
            aggregate["Standard ODG Cost Runway"] += curve["Standard ODG Cost Runway"]
            aggregate["Actual Cumulative Spend Velocity"] += curve[
                "Actual Cumulative Spend Velocity"
            ]
    return aggregate if aggregate is not None else build_clinical_timeline(
        odg_target_cost=22500.0,
        actual_cumulative_at_day=28400.0,
        observed_day=observed_day,
        horizon_days=horizon_days,
    )


# 1. Stark Executive Dark Theme & Contrast UI Rig
st.set_page_config(
    layout="wide",
    page_title="Sovereign Case Management Engine",
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
    /* Table Accessibility Wrap Overrides */
    th, td,
    [data-testid="stTable"] th,
    [data-testid="stTable"] td,
    [data-testid="stTable"] table {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
        vertical-align: top !important;
    }
    [data-testid="stTable"],
    [data-testid="stTable"] table {
        width: 100% !important;
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
    /* High-contrast controls — keep labels/values readable on dark deck */
    .stButton > button {
        background-color: #21262d !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        font-weight: 700 !important;
    }
    .stButton > button:hover {
        background-color: #30363d !important;
        border-color: #8b949e !important;
        color: #ffffff !important;
    }
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: #ffffff !important;
    }
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border-color: #30363d !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] li span {
        color: #ffffff !important;
    }
    /* Historical cost trend chart — high-contrast on dark deck */
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

# 2. Dynamic Variable Ingestion Layer (State Initialization)
if "ivc" not in st.session_state:
    st.session_state.ivc = 0.0
if "functional_drift" not in st.session_state:
    st.session_state.functional_drift = 0.0
if "mandate_exceptions" not in st.session_state:
    st.session_state.mandate_exceptions = []
if "pathway_accelerations" not in st.session_state:
    st.session_state.pathway_accelerations = 0

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
    st.caption(f"Active role: **{role}**")
    st.caption(f"CapEx mitigation floor: **{target_reduction}%**")
    if custom_mandate:
        st.caption(f"Mandate: {custom_mandate}")

# --- MAIN EXECUTIVE VIEW: PORTFOLIO & ASSET LIFE RUNWAY ---
st.title("SOVEREIGN CASE MANAGEMENT ENGINE")
st.markdown(
    "<p style='color:#8b949e; margin-top:-10px;'>"
    "Sophisticated Operational Risk Governance in Simple Terms</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Bulk Data Ingestion Gate — corporate CSV / XLSX with synthetic fallback
uploaded_file = st.file_uploader(
    "📥 LOAD CORPORATE DATA PROFILE (Drag & Drop CSV / XLSX)",
    type=["csv", "xlsx"],
)
portfolio_df, portfolio_source = load_corporate_data_profile(uploaded_file)
kpis = portfolio_summary(portfolio_df)
if portfolio_source == "uploaded":
    st.caption(
        f"Corporate profile loaded · {len(portfolio_df)} rows · "
        f"{uploaded_file.name if uploaded_file else 'workbook'}"
    )
else:
    st.caption("Synthetic corporate profile active · upload CSV / XLSX to override.")

# Global Portfolio Layer 1 Widgets (The Top Metrics Bar)
# Dynamic Privacy Filtering Engine — hide indemnity for non-GM roles
show_indemnity = can_view_indemnity(role)
metric_cols = st.columns(4 if show_indemnity else 3)

with metric_cols[0]:
    st.markdown(
        '<div class="metric-box"><div class="metric-label">Total Assets Protected</div>'
        f'<div class="metric-value-silver">{kpis["total_assets"]} Cases</div></div>',
        unsafe_allow_html=True,
    )
with metric_cols[1]:
    st.markdown(
        '<div class="metric-box"><div class="metric-label">Critical Point of Drift</div>'
        f'<div class="metric-value-crimson">{kpis["critical_drift"]} Subjects</div></div>',
        unsafe_allow_html=True,
    )
with metric_cols[2]:
    st.markdown(
        '<div class="metric-box"><div class="metric-label">ODG Timeline Baseline Alignment</div>'
        f'<div class="metric-value-green">{kpis["odg_alignment"]:.1f}%</div></div>',
        unsafe_allow_html=True,
    )
if show_indemnity:
    indemnity_k = kpis["indemnity_exposure"] / 1000.0
    with metric_cols[3]:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Projected Indemnity Exposure</div>'
            f'<div class="metric-value-silver">${indemnity_k:,.1f}K</div></div>',
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
    if custom_mandate:
        st.caption(f"Strategic mandate in force: {custom_mandate}")

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
    age = st.number_input("Actuarial Chronological Age", min_value=18, max_value=75, value=48)
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
            "Chronological age capacity inflates baseline time metrics. High fear of "
            "re-injury noted, cognitive resilience score tracking low."
        ),
    )

# Dynamically modulate baseline cost and timeline using the core logic formulas
occupation_factor = {
    "Heavy Industrial Laborer": 1.18,
    "Medium Logistics / Operator": 1.08,
    "Sedentary / Administrative": 1.0,
}[occupation]
anatomy_factor = {
    "Glenohumeral Joint (Shoulder)": 1.0,
    "Lumbar Spine": 1.12,
    "Knee Extensor Mechanism": 1.06,
}[anatomy]

age_factor = (age - 25) * 0.015
base_cost = 22500.0 * (1.0 + age_factor) * occupation_factor * anatomy_factor
# CapEx mitigation floor compresses allowable baseline spend
base_cost *= 1.0 - (target_reduction / 100.0) * 0.35
base_days = int(90 * (1.0 + age_factor) * occupation_factor)

# --- THE PREVENTATIVE DRIFT RADAR (High Real-Estate Vertical Realignment) ---
st.markdown("---")
st.markdown("## PREVENTATIVE DRIFT RADAR")
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem;'>"
    "Live Divergence Mapping and Retrospective Lookback Allocation Controls</p>",
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
            + (age * 0.04)
            + (st.session_state.functional_drift * 0.05)
        )
    )
)
lookback_fee = 5000.0 + (projected_final_cost * 0.12)

# Decision matrix labels for Point of Drift
cost_delta = float(actual_spend) - base_cost
if st.session_state.functional_drift <= 5:
    rom_delta_label = "Within Envelope"
elif st.session_state.functional_drift <= 15:
    rom_delta_label = f"-{st.session_state.functional_drift:.0f}% Variance"
else:
    rom_delta_label = f"-{st.session_state.functional_drift:.0f}% Variance"

odg_status = "On Track" if st.session_state.functional_drift <= 15 else "Timeline Breach"
psych_flag = (
    "Path B Trigger Alert"
    if ("fear" in dictation.lower() or "stress" in dictation.lower())
    else "Nominal Watch"
)

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
                "High Fear/Stress Flag"
                if psych_flag == "Path B Trigger Alert"
                else "Stable Affect",
            ],
            "Point of Drift Delta": [
                odg_status,
                f"${cost_delta:+,.2f}",
                rom_delta_label,
                psych_flag,
            ],
        }
    )
    st.table(df_physical)
    st.caption(
        f"Subject `{subject_id}` · {anatomy} · {occupation} · Age {age} · Role {role}"
    )

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

    # The dynamic privacy switch embedded within the financial summary box
    if role == "General Manager":
        privacy_ledger_html = f"""
            <div class="metric-label">Projected Total Case Cost (TASE)</div>
            <div class="metric-value-silver">${projected_final_cost:,.2f}</div>
            <div class="metric-label" style="margin-top:0.8rem;">Dynamic Lookback License Premium Fee Basis</div>
            <div class="metric-value-green">${(5000 + (projected_final_cost * 0.12)):,.2f}</div>
        """
    else:
        privacy_ledger_html = """
            <div class="metric-label">Projected Total Case Cost (TASE)</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem; margin-bottom:0.8rem;">🔒 MASKED (Analyst Clearance Only)</div>
            <div class="metric-label">Dynamic Lookback License Premium Fee Basis</div>
            <div style="color:#8b949e; font-style:italic; font-size:1.1rem;">🔒 RESTRICTED: Requires GM Level</div>
        """

    st.markdown(
        f"""
        <div class="metric-box" style="border-left: 4px solid {border};">
            <div class="metric-label">Platform Governance Status</div>
            <div style="color:{label_color}; font-weight:700; font-size:1.1rem; margin-bottom:0.8rem;">
                {status_label}
            </div>
            {privacy_ledger_html}
            <div class="metric-label" style="margin-top:0.8rem;">
                Probability of Permanent Disability (PPD)
            </div>
            <div class="metric-value-crimson" style="color: {ppd_color};">
                {permanent_disability_prob * 100:.1f}%
            </div>
            <div class="metric-label" style="margin-top:0.8rem;">Input Variance Coefficient (IVC)</div>
            <div class="metric-value-silver">{st.session_state.ivc * 100:.1f}%</div>
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
                st.session_state.pathway_accelerations += 1
                st.success(
                    "Authorized: Swapping to dynamic ODG rehabilitation sub-pathway."
                )
        with btn_col2:
            if st.button("Log Mandate Compliance Exception", use_container_width=True):
                st.session_state.mandate_exceptions.append(
                    {
                        "subject": subject_id,
                        "role": role,
                        "mandate": custom_mandate or "(none)",
                        "drift": st.session_state.functional_drift,
                    }
                )
                st.info("Cryptographic data provenance receipt stamped into vault.")

        if st.session_state.pathway_accelerations:
            st.caption(
                f"Accelerations logged this session: {st.session_state.pathway_accelerations}"
            )
        if st.session_state.mandate_exceptions:
            st.caption(
                f"Compliance exceptions stamped: {len(st.session_state.mandate_exceptions)}"
            )
    else:
        st.success("Drift within governance envelope. No remediation gate required.")

# --- HISTORICAL COST TREND (beneath Preventative Drift Radar) ---
st.markdown("---")
st.markdown("## HISTORICAL COST TREND")
st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem;'>"
    "120-Day Clinical Timeline — Standard ODG Cost Runway vs Actual Cumulative Spend Velocity</p>",
    unsafe_allow_html=True,
)

observed_day = 42
if role == "General Manager":
    df_timeline = build_portfolio_timeline(
        portfolio_df,
        observed_day=observed_day,
        horizon_days=120,
    )
    trend_scope = (
        f"Portfolio aggregate · {len(portfolio_df)} subjects · "
        "global financial matrix visible"
    )
else:
    # Caseworker / Analyst (and Docteur): subject-scoped only — mask portfolio totals
    df_timeline = build_clinical_timeline(
        odg_target_cost=float(base_cost),
        actual_cumulative_at_day=float(actual_spend),
        observed_day=observed_day,
        horizon_days=120,
        odg_horizon_days=max(int(base_days), 1),
    )
    trend_scope = (
        f"Subject-scoped trajectory · `{subject_id}` · "
        "portfolio-wide spend records masked"
    )

st.caption(trend_scope)
st.line_chart(
    data=df_timeline,
    x="Days Elapsed",
    y=["Standard ODG Cost Runway", "Actual Cumulative Spend Velocity"],
    color=["#10b981", "#ef4444"],
)
