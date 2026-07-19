import streamlit as st
import pandas as pd
import numpy as np

# 1. Responsive & High-Contrast Sovereign Layout Configuration
st.set_page_config(layout="wide", page_title="AAT Sovereign Orchestration Engine")

st.markdown("""
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
    @media (max-width: 768px) {
        .critical-impact-value, .nominal-impact-value {
            font-size: 2.4rem !important;
        }
        .metric-value-silver, .metric-value-crimson, .metric-value-green {
            font-size: 1.4rem !important;
        }
        .floating-avatar-container {
            bottom: 20px !important;
            right: 20px !important;
            width: 46px !important;
            height: 46px !important;
        }
        .floating-avatar-icon {
            font-size: 1.1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- MASTER CLAIMS DATABASE SESSION STATE INITIALIZATION ---
if "master_ledger" not in st.session_state:
    st.session_state.master_ledger = pd.DataFrame([
        {"Claim ID": "AAT-Claimant-Delta-2026", "Anatomy Target": "Shoulder (Glenohumeral)", "Age": 48, "Demands": "Heavy Manual / Industrial", "ROM_Actual": 62.0, "Spend_To_Date": 28400.0, "Status": "CRITICAL DRIFT"},
        {"Claim ID": "AAT-Claimant-Epsilon-2026", "Anatomy Target": "Lumbar Spine Matrix", "Age": 32, "Demands": "Sedentary Clerical", "ROM_Actual": 94.0, "Spend_To_Date": 12100.0, "Status": "NOMINAL ALIGNMENT"},
        {"Claim ID": "AAT-Claimant-Zeta-2026", "Anatomy Target": "Lower Extremity (Knee)", "Age": 61, "Demands": "Heavy Manual / Industrial", "ROM_Actual": 48.0, "Spend_To_Date": 41200.0, "Status": "CRITICAL DRIFT"},
        {"Claim ID": "AAT-Claimant-Eta-2026", "Anatomy Target": "Shoulder (Glenohumeral)", "Age": 29, "Demands": "Medium Logistics / Transport", "ROM_Actual": 88.0, "Spend_To_Date": 19400.0, "Status": "NOMINAL ALIGNMENT"}
    ])

if "ministerial_override" not in st.session_state:
    st.session_state.ministerial_override = False

# --- SIDEBAR: GOVERNANCE LAYER FILTERS ---
with st.sidebar:
    st.markdown("### 🏛️ AAT SCHEME GOVERNANCE")
    role = st.selectbox("Active User Role Matrix", [
        "Cabinet Minister (Executive Authority)",
        "Scheme Director (GM)", 
        "Claims Officer / Analyst", 
        "Reviewing Specialist"
    ])
    st.markdown("---")
    st.markdown("### ⚡ SCHEME MANDATE INJECTION")
    cap_floor = st.slider("Enforce Liability Mitigation Floor (%)", 0, 50, 15)
    st.text_input("Disseminate Performance Mandate", placeholder="e.g., Accelerate Pathway Interventions")

# --- MAIN PERFORMANCE DASHBOARD TITLE ---
st.title("AAT SOVEREIGN ORCHESTRATION ENGINE")
st.markdown("<p style='color:#8b949e; margin-top:-10px;'>Predictive Operational Risk & Long-Tail Claims Governance Framework</p>", unsafe_allow_html=True)
st.markdown("---")

# --- CABINET MINISTER DIRECTIVE PANEL ---
if role == "Cabinet Minister (Executive Authority)":
    st.markdown("""<div style="background-color:#1c1112; border:1px solid #dc2626; padding:1.2rem; border-radius:6px; margin-bottom:1.5rem;">
    <div style="font-family:'IBM Plex Mono', monospace; font-size:0.75rem; color:#ef4444; font-weight:700; letter-spacing:0.05em; text-transform:uppercase;">🏛️ STATUTORY CABINET AUTHORITY PORTAL</div>
    <h3 style="margin-top:0.2rem; margin-bottom:0.5rem; color:#ffffff;">Ministerial Executive Directive Matrix</h3>
    <p style="color:#8b949e; font-size:0.88rem; margin-bottom:1rem;">As the Crown Executive, your input bypasses standard inter-departmental friction. Activating systemic overrides will force institutional data reconciliation and re-allocate capital reserves immediately.</p>
    </div>""", unsafe_allow_html=True)
    
    col_min1, col_min2 = st.columns(2)
    with col_min1:
        st.session_state.ministerial_override = st.checkbox("⚡ Force Cross-Agency Data Integration Share Mandate (Bypass Bureaucratic Silos)", value=st.session_state.ministerial_override)
    with col_min2:
        st.selectbox("Execute Macro Statutory Intervention", [
            "Maintain Standard Operations runway",
            "🚀 Emergency CapEx Liquidity Release (Settle P0 Drift Blocks In Bulk)",
            "⚙️ Direct MSD to Open 500 Immediate Training Cert Slots",
            "🩺 Fast-Track Crown Clinical Network Triage Mandate"
        ])
    st.markdown("---")

# --- INITIATIVE 1: ALL-OF-GOVERNMENT DATA INTEGRATION GRID ---
st.markdown("### 🛰️ ALL-OF-GOVERNMENT DATA INTEGRATION GRID")
gov_col1, gov_col2, gov_col3 = st.columns(3)

with gov_col1:
    with st.expander("🟢 IRD INCOME EXCHANGE", expanded=False):
        st.markdown("""<div style="font-family:monospace; font-size:0.8rem; color:#8b949e; line-height:1.4;">
        <strong>Status:</strong> SECURE LIVE SYNC<br/>
        <strong>Last Harvest:</strong> Today, 11:42 AM<br/>
        <strong>Channel Hash:</strong> IRD-2026-99X4<br/>
        <hr style="border:0; border-top:1px solid #30363d; margin:0.4rem 0;"/>
        <span style="color:#10b981;">✓ 12-Month wage ledger verified.</span>
        </div>""", unsafe_allow_html=True)

with gov_col2:
    with st.expander("🟢 MSD WORKFORCE PIPELINE", expanded=False):
        st.markdown("""<div style="font-family:monospace; font-size:0.8rem; color:#8b949e; line-height:1.4;">
        <strong>Status:</strong> LIVE INTEGRATION<br/>
        <strong>Last Harvest:</strong> Today, 11:40 AM<br/>
        <strong>Channel Hash:</strong> MSD-AX-7710<br/>
        <hr style="border:0; border-top:1px solid #30363d; margin:0.4rem 0;"/>
        <span style="color:#10b981;">✓ 14 Modified light-duty matches found.</span>
        </div>""", unsafe_allow_html=True)

with gov_col3:
    hnz_status = "🟢 SECURE SYNCED" if st.session_state.ministerial_override else "🔵 PROXIED / OPERATIONAL"
    hnz_color = "#10b981" if st.session_state.ministerial_override else "#38bdf8"
    with st.expander(f"{'🟢' if st.session_state.ministerial_override else '🔵'} HEALTH NZ CLINICAL GRID", expanded=False):
        st.markdown(f"""<div style="font-family:monospace; font-size:0.8rem; color:#8b949e; line-height:1.4;">
        <strong>Status:</strong> {hnz_status}<br/>
        <strong>Last Harvest:</strong> Today, 10:15 AM<br/>
        <strong>Channel Hash:</strong> HNZ-MED-4402<br/>
        <hr style="border:0; border-top:1px solid #30363d; margin:0.4rem 0;"/>
        <span style="color:{hnz_color};">{'✓ Ministerial Overlap Mandate Active: Encrypted patient history fully decrypted for review.' if st.session_state.ministerial_override else 'i Historical orthopaedic records linked.'}</span>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# --- CENTRAL ROUTING SELECTOR ---
dropdown_options = [
    "Global Scheme Portfolio (All Active Claims)", 
    "➕ Onboard New Claimant Matrix"
] + list(st.session_state.master_ledger["Claim ID"])

view_selection = st.selectbox("📂 AUDIT VIEW COMMAND SECTOR", dropdown_options)
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# INTERFACE LAYER A: GLOBAL SCHEME PORTFOLIO VIEW
# ==============================================================================
if view_selection == "Global Scheme Portfolio (All Active Claims)":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-box"><div class="metric-label">Total Scheme Claims</div><div class="metric-value-silver">142 Active</div><div class="metric-subtext">Regional Portfolio Intake</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box"><div class="metric-label">Critical Pathway Drift</div><div class="metric-value-crimson">18 Subjects</div><div class="metric-subtext">Targeted Escalations Pending</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box"><div class="metric-label">Performance Index</div><div class="metric-value-green">85.9%</div><div class="metric-subtext">Baseline Trajectory Alignment</div></div>', unsafe_allow_html=True)

    st.markdown("### 📋 MASTER ORCHESTRATION ACCOUNTABILITY LEDGER")
    df_formatted_ledger = st.session_state.master_ledger[["Claim ID", "Anatomy Target", "Status"]].copy()
    st.table(df_formatted_ledger)

# ==============================================================================
# INTERFACE LAYER B: NEW CLIENT INTAKE PATHWAY FORM
# ==============================================================================
elif view_selection == "➕ Onboard New Claimant Matrix":
    st.markdown("## 📥 SECURE REGISTRY INTAKE GATEWAY")
    with st.form("intake_form", clear_on_submit=True):
        f_id = st.text_input("Claimant Identification Token Label", placeholder="e.g., AAT-Claimant-Omega-2026")
        f_anatomy = st.selectbox("Target Anatomical Structure Classification", ["Lower Extremity (Knee)", "Shoulder (Glenohumeral)", "Lumbar Spine Matrix", "Cervical Alignment Structure"])
        f_age = st.number_input("Chronological Biological Age Curve", min_value=18, max_value=80, value=45)
        f_demands = st.selectbox("Occupational Demands Tier", ["Heavy Manual / Industrial", "Medium Logistics / Transport", "Sedentary Clerical"])
        f_rom = st.slider("Live Telemetry Flexion Performance Baseline (Range of Motion %)", 10, 100, 75)
        f_spend = st.number_input("Initial Intake Capital Allocation ($NZD Baseline)", min_value=0.0, value=5000.0)
        
        submit_btn = st.form_submit_button("🎖️ AUTHORIZE STATE-CERTIFIED REGISTRY INJECTION")
        if submit_btn and f_id:
            drift_calc = 100.0 - float(f_rom)
            determined_status = "CRITICAL DRIFT" if drift_calc > 15 else "NOMINAL ALIGNMENT"
            new_row = {"Claim ID": f_id, "Anatomy Target": f_anatomy, "Age": int(f_age), "Demands": f_demands, "ROM_Actual": float(f_rom), "Spend_To_Date": float(f_spend), "Status": determined_status}
            st.session_state.master_ledger = pd.concat([st.session_state.master_ledger, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"✓ Security Node Authenticated: {f_id} dynamically linked to cross-agency frameworks.")

# ==============================================================================
# INTERFACE LAYER C: INDIVIDUAL DRILL-DOWN VIEW (WITH SIMULATION)
# ==============================================================================
else:
    selected_row = st.session_state.master_ledger[st.session_state.master_ledger["Claim ID"] == view_selection].iloc[0]
    subject_token = selected_row["Claim ID"]
    anatomy = selected_row["Anatomy Target"]
    age = int(selected_row["Age"])
    duty_tier = selected_row["Demands"]
    actual_rom = float(selected_row["ROM_Actual"])
    actual_spend = float(selected_row["Spend_To_Date"])
    
    st.markdown("## 📡 PREVENTATIVE DRIFT RADAR DEEP-DIVE")
    
    st.markdown("#### 🛠️ Live Simulation Parameter Adjustment Deck")
    sim_mode = st.toggle("🔄 Enable Live Parameter Simulation Overrides", key=f"sim_{subject_token}")
    if sim_mode:
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            actual_rom = float(st.slider("Simulate Live Flexion / ROM (%)", 10, 100, int(actual_rom), key=f"sim_rom_{subject_token}"))
        with col_sim2:
            actual_spend = float(st.number_input("Simulate Live Spend to Date ($NZD)", min_value=0.0, value=float(actual_spend), key=f"sim_spend_{subject_token}"))

    # Calculations Core
    job_multiplier = 1.30 if "Heavy" in duty_tier else (1.10 if "Medium" in duty_tier else 0.90)
    age_factor = (age - 25) * 0.015
    calibrated_base_cost = 22500.0 * (1.0 + age_factor) * job_multiplier
    calibrated_base_days = int(90 * (1.0 + age_factor) * job_multiplier)
    
    functional_drift = 100.0 - actual_rom
    ivc = (actual_spend - calibrated_base_cost) / calibrated_base_cost
    
    projected_final_cost = calibrated_base_cost + (functional_drift * 185.0) + (ivc * calibrated_base_cost)
    
    if st.session_state.ministerial_override:
        projected_final_cost = projected_final_cost * 0.80 
        
    mitigated_reserve_target = projected_final_cost * (1.0 - (cap_floor / 100.0))
    permanent_disability_prob = 1.0 / (1.0 + np.exp(-(-2.8 + (age * 0.045) + (functional_drift * 0.055))))

    if functional_drift > 15.0 or permanent_disability_prob > 0.50:
        status_label = "CRITICAL PATHWAY DRIFT DETECTED"
        status_color = "#ef4444"
        impact_class = "critical-impact-value"
    else:
        status_label = "NOMINAL PATHWAY ALIGNMENT"
        status_color = "#10b981"
        impact_class = "nominal-impact-value"

    protocol_html = f"""<div style="background-color:#1b1416; padding:0.8rem; border-radius:4px; border:1px solid #6b21a8; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#ef4444; font-weight:700;">🤖 AUTOMATED MITIGATION PROTOCOL</div>
<ul style="color:#f8fafc; font-size:0.88rem; margin:0; padding-left:1.2rem; line-height:1.4;">
<li><strong>⚠️ Commutation Target:</strong> Initiate immediate Lump-Sum settlement review range (${mitigated_reserve_target:,.0f} - ${projected_final_cost:,.0f} NZD)</li>
<li><strong>🩺 IME Authorization:</strong> Issue urgent Independent Medical Examination directive.</li>
</ul>
</div>"""

    adaptive_cv_html = f"""<div style="background-color:#18141c; padding:0.8rem; border-radius:4px; border:1px solid #a855f7; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#c084fc; font-weight:700; display:flex; justify-content:between; align-items:center;">
<span>💼 ADAPTIVE CAREER TRAJECTORY & CV PIVOT MATRIX</span>
<span style="background-color:#10b981; color:#0c1017; font-size:0.7rem; padding:1px 5px; border-radius:3px; font-weight:700; margin-left:10px;">🎖️ MSD CERTIFIED ADOPTION MANDATORY</span>
</div>
<table style="width:100%; border-collapse:collapse; font-size:0.85rem; color:#f8fafc;">
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">Obsolete Vector:</td><td>{duty_tier} Matrix</td></tr>
<tr style="border-bottom:1px solid #30363d;"><td style="color:#8b949e; padding:4px 0;">New Target CV:</td><td><strong>Assigned Operational Safety Compliance Auditor</strong></td></tr>
<tr><td style="color:#8b949e; padding:4px 0; vertical-align:middle;">MSD Bridge:</td><td>
<div style="display:inline-block; background-color:#166534; color:#4ade80; border:1px solid #14532d; font-size:0.72rem; padding:1px 6px; border-radius:3px; font-weight:600; margin-bottom:3px;">⚡ SYSTEM AUTOMATION ACTIVE</div><br/>
<span style="color:#38bdf8; font-family:monospace;">📁 MSD Registry Slot Reserved</span>
</td></tr>
</table>
</div>"""

    st.markdown("#### Comprehensive Scheme Ledger Dossier")
    
    if role in ["Cabinet Minister (Executive Authority)", "Scheme Director (GM)"]:
        fee_line = f"""<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>
<div class="metric-value-green" style="font-size:1.4rem;">${(5000 + (projected_final_cost * 0.12)):,.2f} NZD</div>"""
    else:
        fee_line = """<div class="metric-label" style="margin-top:0.6rem;">Dynamic Lookback Valuation Basis</div>
<div style="color:#8b949e; font-style:italic; font-size:0.95rem;">🔒 SECURE LEDGER PROXIED TO EXECUTIVE SECTOR</div>"""
        
    html_payload = f"""<div class="metric-box" style="border-left: 4px solid {status_color}; padding: 1.5rem; height: auto;">
<div class="metric-label">Scheme Alignment Status</div>
<div style="color:{status_color}; font-weight:700; font-size:1.2rem; margin-bottom:0.8rem;">{status_label}</div>

<div style="background-color:#0c1017; padding:0.8rem; border-radius:4px; border:1px solid #30363d; margin-bottom:0.8rem;">
<div class="metric-label" style="color:#ffffff;">Claimant File Dossier Matrix</div>
<span style="font-size:0.9rem; color:#8b949e;">ID:</span> <span style="font-size:0.9rem; color:#ffffff; font-weight:600;">{subject_token}</span><br/>
<span style="font-size:0.9rem; color:#8b949e;">Target Anatomy:</span> <span style="font-size:0.9rem; color:#ffffff;">{anatomy}</span><br/>
<span style="font-size:0.9rem; color:#8b949e;">Demands / Age:</span> <span style="font-size:0.9rem; color:#ffffff;">{duty_tier} (Age {age})</span><br/>
</div>

{protocol_html}
{adaptive_cv_html}

<div class="metric-label">Probability of Permanent Disability (PPD)</div>
<div class="{impact_class}">{permanent_disability_prob*100:.1f}%</div>

<hr style="border:0; border-top:1px solid #30363d; margin: 0.8rem 0;"/>
<div class="metric-label">Total Absolute System Exposure (TASE) {'<span style="color:#10b981;">(20% Crown Directive Compression Applied)</span>' if st.session_state.ministerial_override else ''}</div>
<div class="metric-value-silver" style="font-size:1.5rem; margin-bottom:0.3rem;">${projected_final_cost:,.2f} NZD</div>
<div class="metric-label">Mitigated Capital Reserve Target</div>
<div class="metric-value-green" style="font-size:1.5rem; margin-bottom:0.3rem;">${mitigated_reserve_target:,.2f} NZD</div>
{fee_line}
</div>"""
    
    st.markdown(html_payload, unsafe_allow_html=True)

    # 📸 Empirical Evidence Matrix
    st.markdown("#### 📸 Empirical Evidence & Telemetry Capture Matrix")
    uploaded_evidence = st.file_uploader("Ingest Biometric Evidence", type=["png", "jpg", "jpeg", "mp4"], key=f"upload_{subject_token}")
    if uploaded_evidence is not None:
        file_extension = uploaded_evidence.name.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg"]:
            st.image(uploaded_evidence, use_container_width=True)
        elif file_extension in ["mp4"]:
            st.video(uploaded_evidence)
