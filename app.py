"""NZ ACC Risk Orchestration Engine — AAT Scheme Performance (localized).

New Zealand Accident Compensation Corporation operational surface with
All-of-Government grids: IRD Income Exchange, MSD Workforce Pipeline, and
Health NZ Clinical Grid. NZD ledger, MSD certified CV pivot matrices.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

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
    .metric-value-purple {
        font-size: 1.8rem;
        font-weight: 700;
        color: #a855f7;
        line-height: 1.2;
    }
    .metric-subtext {
        font-size: 0.85rem;
        color: #8b949e;
        margin-top: 0.3rem;
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

    /* In-flow primary nav strip */
    .ipad-top-nav {
      position: relative !important;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      width: 100%;
      box-sizing: border-box;
      padding-top: max(16px, env(safe-area-inset-top, 0px));
      margin-top: max(24px, env(safe-area-inset-top, 0px));
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
    }
    .ipad-top-nav .nav-hint {
      color: #8b949e;
      font-size: 0.82rem;
      font-weight: 600;
      line-height: 1.35;
    }

    /* Tablet / mobile: hard floor — top-left hit targets ≥40px from screen top */
    @media (max-width: 1024px) {
      header[data-testid="stHeader"],
      .stAppHeader,
      [data-testid="stHeader"],
      .ipad-top-nav {
        margin-top: max(24px, env(safe-area-inset-top, 0px)) !important;
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
        /* Clear iPadOS Multitasking pill (...) and status bar */
        margin-top: max(40px, calc(env(safe-area-inset-top, 0px) + 16px)) !important;
        position: relative !important;
        top: auto !important;
        left: auto !important;
      }

      div[data-testid="stMainBlockContainer"],
      .block-container {
        padding-top: max(1.5rem, calc(env(safe-area-inset-top, 0px) + 1rem)) !important;
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


df_master_ledger = load_internal_portfolio_ledger()

# --- SIDEBAR: GOVERNANCE LAYER FILTERS ---
with st.sidebar:
    st.markdown("### NZ ACC SCHEME GOVERNANCE")
    role = st.selectbox(
        "Active User Role Matrix",
        ["Scheme Director (GM)", "Claims Officer / Analyst", "Reviewing Specialist"],
    )
    st.markdown("---")
    st.markdown("### SCHEME MANDATE INJECTION")
    cap_floor = st.slider("Enforce Liability Mitigation Floor (%)", 0, 50, 15)
    st.text_input(
        "Disseminate Performance Mandate",
        placeholder="e.g., Accelerate Pathway Interventions",
    )
    st.caption("Localized NZ ACC · IRD · MSD · Health NZ AoG grids")

# --- MAIN PERFORMANCE DASHBOARD TITLE ---
st.title("NZ ACC RISK ORCHESTRATION ENGINE")
st.markdown(
    "<p style='color:#8b949e; margin-top:-10px;'>"
    "AAT Scheme Performance · Predictive Operational Risk & Long-Tail Claims "
    "Governance (NZD) · All-of-Government Integration</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- INITIATIVE 1: ALL-OF-GOVERNMENT DATA INTEGRATION GRID ---
st.markdown("### 🛰️ ALL-OF-GOVERNMENT DATA INTEGRATION GRID")
st.markdown(
    "<p style='color:#8b949e; margin-top:-10px; font-size:0.9rem;'>Real-time inter-agency data synchronization pipeline and encrypted security verification tokens.</p>",
    unsafe_allow_html=True,
)

gov_col1, gov_col2, gov_col3 = st.columns(3)

with gov_col1:
    with st.expander("🟢 IRD INCOME EXCHANGE", expanded=False):
        st.markdown(
            """
<div style="font-family:monospace; font-size:0.8rem; color:#8b949e; line-height:1.4;">
<strong>Status:</strong> SECURE LIVE SYNC<br/>
<strong>Last Harvest:</strong> Today, 11:42 AM<br/>
<strong>Channel Hash:</strong> IRD-2026-99X4<br/>
<hr style="border:0; border-top:1px solid #30363d; margin:0.4rem 0;"/>
<span style="color:#10b981;">✓ 12-Month wage ledger verified.</span>
</div>
""",
            unsafe_allow_html=True,
        )

with gov_col2:
    with st.expander("🟢 MSD WORKFORCE PIPELINE", expanded=False):
        st.markdown(
            """
<div style="font-family:monospace; font-size:0.8rem; color:#8b949e; line-height:1.4;">
<strong>Status:</strong> LIVE INTEGRATION<br/>
<strong>Last Harvest:</strong> Today, 11:40 AM<br/>
<strong>Channel Hash:</strong> MSD-AX-7710<br/>
<hr style="border:0; border-top:1px solid #30363d; margin:0.4rem 0;"/>
<span style="color:#10b981;">✓ 14 Modified light-duty matches found.</span>
</div>
""",
            unsafe_allow_html=True,
        )

with gov_col3:
    with st.expander("🔵 HEALTH NZ CLINICAL GRID", expanded=False):
        st.markdown(
            """
<div style="font-family:monospace; font-size:0.8rem; color:#8b949e; line-height:1.4;">
<strong>Status:</strong> PROXIED / OPERATIONAL<br/>
<strong>Last Harvest:</strong> Today, 10:15 AM<br/>
<strong>Channel Hash:</strong> HNZ-MED-4402<br/>
<hr style="border:0; border-top:1px solid #30363d; margin:0.4rem 0;"/>
<span style="color:#38bdf8;">i Historical orthopaedic records linked.</span>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("---")

# --- CENTRAL ROUTING SELECTOR ---
view_selection = st.selectbox(
    "📂 AUDIT VIEW COMMAND SECTOR",
    [
        "Global Scheme Portfolio (All Active Claims)",
        "AAT-Claimant-Delta-2026",
        "AAT-Claimant-Epsilon-2026",
        "AAT-Claimant-Zeta-2026",
        "AAT-Claimant-Eta-2026",
    ],
)
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# INTERFACE LAYER A: GLOBAL SCHEME PORTFOLIO VIEW
# ==============================================================================
if view_selection == "Global Scheme Portfolio (All Active Claims)":

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Total Scheme Claims</div><div class="metric-value-silver">142 Active</div><div class="metric-subtext">Regional Portfolio Intake</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Critical Pathway Drift</div><div class="metric-value-crimson">18 Subjects</div><div class="metric-subtext">Targeted Escalations Pending</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="metric-box"><div class="metric-label">Performance Index</div><div class="metric-value-green">85.9%</div><div class="metric-subtext">Baseline Trajectory Alignment</div></div>',
            unsafe_allow_html=True,
        )

    if role == "Claims Officer / Analyst":
        st.markdown("### 📋 CLAIMS OFFICER / ANALYST — ACTION TASK")

        html_task_co = f"""<div class="metric-box" style="border-left: 4px solid #ef4444; padding: 1.2rem;">
<div class="metric-label" style="color:#ef4444;">TASK ID: CO-AAT-2026-031</div>
<div class="metric-subtext" style="color:#ffffff; font-weight:600; margin-bottom:0.4rem;">Clear the CRITICAL DRIFT files before they harden into long-tail PPD exposure.</div>
<div style="font-size:0.85rem; color:#8b949e;">Active Mandate: {cap_floor}% CapEx Mitigation Control Active</div>
</div>"""
        st.markdown(html_task_co, unsafe_allow_html=True)

        st.markdown("#### 🚨 Operational Priority Queue")
        df_co_queue = pd.DataFrame(
            {
                "Priority": ["P0", "P1", "Watch"],
                "Claim ID": [
                    "AAT-Claimant-Zeta-2026",
                    "AAT-Claimant-Delta-2026",
                    "Eta / Epsilon Cohort",
                ],
                "Escalation Core": [
                    "Highest PPD Risk Vector",
                    "Critical Pathway Deviation",
                    "Nominal Runway Alignment",
                ],
                "Target Operational Status": [
                    "Action Required (Shift 1)",
                    "Review Required (Shift 1)",
                    "Watch-Only Status Log",
                ],
            }
        )
        st.table(df_co_queue)

    elif role == "Reviewing Specialist":
        st.markdown("### 🩻 REVIEWING SPECIALIST — CLINICAL ESCALATION AUDIT DECK")

        html_task_rs = """<div class="metric-box" style="border-left: 4px solid #a855f7; padding: 1.2rem;">
<div class="metric-label" style="color:#a855f7;">TASK ID: RS-AAT-2026-042</div>
<div class="metric-subtext" style="color:#ffffff; font-weight:600; margin-bottom:0.4rem;">Validate physical telemetry variance anomalies and verify Independent Medical Examination (IME) compliance directives.</div>
<div style="font-size:0.85rem; color:#8b949e;">Clinical Mandate: Audit structural tissue guarding thresholds and execute medical capacity validations.</div>
</div>"""
        st.markdown(html_task_rs, unsafe_allow_html=True)

        st.markdown("#### 📡 Clinical Escalation & Validation Matrix")
        df_rs_queue = pd.DataFrame(
            {
                "Audit Class": ["Critical Triage", "Path Variance", "Nominal Clear"],
                "Claim Token Target": [
                    "AAT-Claimant-Zeta-2026",
                    "AAT-Claimant-Delta-2026",
                    "Epsilon / Eta Files",
                ],
                "Ingested Telemetry Drivers": [
                    "ROM 48% • High Joint Guarding",
                    "ROM 62% • Psychosocial Guarding",
                    "ROM >85% • Natural Recovery Arc",
                ],
                "IME Verification State": [
                    "⚠️ PENDING SPECIALIST AUDIT",
                    "⚠️ VERIFICATION REQUIRED",
                    "✅ CLINICALLY RESOLVED",
                ],
                "Required Sign-Off Command": [
                    "Execute Independent Medical Audit",
                    "Verify Behavioral Compliance Log",
                    "Authorize Standard Billing Track",
                ],
            }
        )
        st.table(df_rs_queue)

    else:
        st.markdown("### 📋 MASTER CLAIMS ACCOUNTABILITY LEDGER")
        df_formatted_ledger = df_master_ledger[
            ["Claim ID", "Anatomy Target", "Status"]
        ].copy()
        st.table(df_formatted_ledger)

        st.markdown("---")
        st.markdown("### 📈 AGGREGATE SCHEME CAPEX VELOCITY TRAJECTORY")
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
    if "Zeta" in subject_token:
        dict_txt = (
            "Advanced structural vulnerability noted in knee construct. High manual "
            "occupational exposures compounding timeline variance."
        )

        protocol_html = f"""<div style="background-color:#1b1416; padding:0.8rem; border-radius:4px; border:1px solid #6b21a8; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#ef4444; font-weight:700;">🤖 AUTOMATED MITIGATION PROTOCOL</div>
<ul style="color:#f8fafc; font-size:0.88rem; margin:0; padding-left:1.2rem; line-height:1.4;">
<li><strong>⚠️ Commutation Target:</strong> Initiate immediate Lump-Sum settlement review range (${mitigated_reserve_target:,.0f} - ${projected_final_cost:,.0f} NZD) to transfer long-tail structural risk off ledger balance sheets.</li>
<li><strong>🩺 IME Authorization:</strong> Issue urgent Independent Medical Examination directive to challenge current permanent incapacity ceiling.</li>
<li><strong>⚙️ Demands Override:</strong> Force immediate drop in Occupational Tier from Heavy Manual to Clerical/Supervisory.</li>
</ul>
</div>"""

        adaptive_cv_html = """<div style="background-color:#18141c; padding:0.8rem; border-radius:4px; border:1px solid #a855f7; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#c084fc; font-weight:700; display:flex; justify-content:between; align-items:center;">
<span>💼 ADAPTIVE CAREER TRAJECTORY & CV PIVOT MATRIX</span>
<span style="background-color:#10b981; color:#0c1017; font-size:0.7rem; padding:1px 5px; border-radius:3px; font-weight:700; margin-left:10px;">🎖️ MSD CERTIFIED ADOPTION MANDATORY</span>
</div>
<div style="font-size:0.84rem; color:#8b949e; margin-bottom:0.4rem; font-style:italic;">Mental Preparation Lifeline & Supportive Path Forward via Inter-Agency Ingest. Adherence is state-certified.</div>
<table style="width:100%; border-collapse:collapse; font-size:0.85rem; color:#f8fafc;">
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">Obsolete Vector:</td><td>Heavy Industrial Operations (Physically Incapacitated)</td></tr>
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">Cognitive Harvest:</td><td>Blueprint Interpretation, Logistics Coordination, OHS Enforcement</td></tr>
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">New Target CV:</td><td><strong>Site Quality & Safety Compliance Auditor</strong> (MSD Legally Registered Blueprint)</td></tr>
<tr><td style="color:#8b949e; padding:4px 0; vertical-align:middle;">MSD Training Bridge:</td><td>
<div style="display:inline-block; background-color:#166534; color:#4ade80; border:1px solid #14532d; font-size:0.72rem; padding:1px 6px; border-radius:3px; font-weight:600; margin-bottom:3px;">⚡ SYSTEM AUTOMATION ACTIVE</div><br/>
<span style="color:#38bdf8; font-family:monospace;">📁 MSD Registry Slot Reserved → Digital Site Log Systems Cert #AAT-2026</span>
</td></tr>
</table>
</div>"""

    elif "Delta" in subject_token:
        dict_txt = (
            "Claimant presents with severe shoulder disruption. Cellular age curves "
            "indicate prolonged recovery runway."
        )

        protocol_html = """<div style="background-color:#141b1f; padding:0.8rem; border-radius:4px; border:1px solid #0369a1; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#38bdf8; font-weight:700;">🤖 AUTOMATED MITIGATION PROTOCOL</div>
<ul style="color:#f8fafc; font-size:0.88rem; margin:0; padding-left:1.2rem; line-height:1.4;">
<li><strong>🧠 Clinical Triage:</strong> Deploy proactive psychological resilience and behavioral counseling within 7 days to address elevated psychosocial barrier spikes.</li>
<li><strong>🤝 Light-Duty Matching:</strong> Initialize structured transitional employer-return tracking protocol to halt ongoing baseline drift velocity.</li>
</ul>
</div>"""

        adaptive_cv_html = """<div style="background-color:#141b1f; padding:0.8rem; border-radius:4px; border:1px solid #0284c7; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#38bdf8; font-weight:700; display:flex; justify-content:between; align-items:center;">
<span>💼 ADAPTIVE CAREER TRAJECTORY & CV PIVOT MATRIX</span>
<span style="background-color:#10b981; color:#0c1017; font-size:0.7rem; padding:1px 5px; border-radius:3px; font-weight:700; margin-left:10px;">🎖️ MSD CERTIFIED ADOPTION MANDATORY</span>
</div>
<div style="font-size:0.84rem; color:#8b949e; margin-bottom:0.4rem; font-style:italic;">Mental Preparation Lifeline & Supportive Path Forward via Inter-Agency Ingest. Adherence is state-certified.</div>
<table style="width:100%; border-collapse:collapse; font-size:0.85rem; color:#f8fafc;">
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">Obsolete Vector:</td><td>Active Logistics Manual Handling (Glenohumeral Traumatic Deviation)</td></tr>
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">Cognitive Harvest:</td><td>Fleet Routing Management, Procurement Sourcing, Manifest Tracking</td></tr>
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">New Target CV:</td><td><strong>Supply Chain Procurement Analyst / Dispatch Supervisor</strong></td></tr>
<tr><td style="color:#8b949e; padding:4px 0; vertical-align:middle;">MSD Training Bridge:</td><td>
<div style="display:inline-block; background-color:#166534; color:#4ade80; border:1px solid #14532d; font-size:0.72rem; padding:1px 6px; border-radius:3px; font-weight:600; margin-bottom:3px;">⚡ SYSTEM AUTOMATION ACTIVE</div><br/>
<span style="color:#38bdf8; font-family:monospace;">📁 MSD Registry Slot Reserved → Public Service Transit Admin Pipeline</span>
</td></tr>
</table>
</div>"""

    else:
        dict_txt = (
            "Favorable tissue consistency. Functional path trajectory arc tracking "
            "nominal. Low stress metrics."
        )
        protocol_html = """<div style="background-color:#141f17; padding:0.8rem; border-radius:4px; border:1px solid #15803d; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#4ade80; font-weight:700;">🤖 AUTOMATED MITIGATION PROTOCOL</div>
<p style="color:#f8fafc; font-size:0.88rem; margin:0; line-height:1.4;">
<strong>✅ Path Alignment Secure:</strong> Maintain standard vocational rehabilitation baseline track. Clear file for regular automated payment processing. No structural intervention required this cycle.
</p>
</div>"""

        adaptive_cv_html = """<div style="background-color:#141f17; padding:0.8rem; border-radius:4px; border:1px solid #166534; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#4ade80; font-weight:700;">💼 ADAPTIVE CAREER TRAJECTORY STATUS</div>
<p style="color:#f8fafc; font-size:0.88rem; margin:0; line-height:1.4;">
Baseline capacity holds. Pre-injury CV requires zero structural alterations. Natural track recovery trajectory validated. Verified via MSD National Framework.
</p>
</div>"""

    st.markdown("## 📡 PREVENTATIVE DRIFT RADAR DEEP-DIVE")

    # --- STACKED BLOCK 1: MASTER LEDGER DOSSIER BOX ---
    st.markdown("#### Comprehensive Scheme Ledger Dossier")

    if role == "Scheme Director (GM)":
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
<span style="font-size:0.9rem; color:#8b949e;">ID:</span> <span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{subject_token}</span><br/>
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
