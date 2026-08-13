from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from config import get_sector_book, resolve_sector_co, sector_book_options, sector_co_short

# Notebook Lane targets — swap GEMINI_NOTEBOOK_URL for the live project notebook when ready.
GEMINI_NOTEBOOK_URL = "https://colab.research.google.com/"
BRIEFING_AUDIO_PATH = Path(__file__).resolve().parent / "public" / "briefing.mp3"
QUERY_INPUT_KEY = "notebook_lane_query_input"
DEFAULT_QUERY_KEY = "notebook_lane_default_query"
LAST_SECTOR_KEY = "notebook_lane_last_sector"

# NameError shield: bound before any widget / sector logic can run.
default_query = ""

st.set_page_config(
    page_title="Executive Board Glass Command Surface",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 0. URL QUERY ROUTING (runs BEFORE sidebar / board glass draw)
# Safari deep links: ?co=PJM or ?cl=PJM → force GRID_PJM into session state
# so the dropdown and live glass open on the power-grid board, not ACC.
# -----------------------------------------------------------------------------
_SECTOR_OPTIONS = sector_book_options()
_SECTOR_KEYS = list(_SECTOR_OPTIONS.keys())


def _read_co_query_param():
    """Read ?co= or ?cl= from the URL (case-insensitive value)."""
    qp = st.query_params
    for name in ("co", "cl"):
        if name not in qp:
            continue
        raw = qp.get(name)
        if isinstance(raw, (list, tuple)):
            raw = raw[0] if raw else ""
        raw = str(raw or "").strip()
        if raw:
            return raw, name
    return "", "co"


_co_raw, _co_param_name = _read_co_query_param()
_matched_sector = resolve_sector_co(_co_raw, default=None)

# Explicit overwrite: URL match wins over any prior ACC session state
if _matched_sector and _matched_sector in _SECTOR_KEYS:
    st.session_state["sector_book_key"] = _matched_sector
    st.session_state["_co_url_applied"] = {
        "raw": _co_raw,
        "param": _co_param_name,
        "key": _matched_sector,
    }
elif "sector_book_key" not in st.session_state or st.session_state.get("sector_book_key") not in _SECTOR_KEYS:
    st.session_state["sector_book_key"] = "ACC_BASELINE"

# -----------------------------------------------------------------------------
# 1. TOTAL STEALTH CSS OVERRIDE (Eradicates Manage App, Header, Footer & Badges)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    /* Absolute Hide for Streamlit Host Chrome, Header, Footer, Watermarks & Manage App Badge */
    header, footer, #MainMenu, .stDeployButton, 
    [data-testid="stHeader"], 
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"], 
    [data-testid="stAppDeployButton"],
    [data-testid="stSidebarNav"],
    [data-testid="manage-app-button"],
    .viewerBadge_container__1A53K,
    div[class*="viewerBadge"],
    div[class*="styles_viewerBadge"],
    button[title*="Manage app"],
    div[data-testid="stAppViewBlockContainer"] > header {
        visibility: hidden !important;
        display: none !important;
        height: 0px !important;
    }

    /* Bottom-right host badges (Streamlit Cloud viewer / GitHub watermark) */
    #GithubIcon,
    [class*="viewerBadge"],
    [class*="ViewerBadge"],
    [class*="styles_viewerBadge"],
    a[data-testid="viewerBadge"],
    .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_,
    .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK,
    a[href*="share.streamlit.io"],
    a[href^="https://streamlit.io"],
    a[href^="https://www.streamlit.io"] {
        visibility: hidden !important;
        display: none !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    /* Board Glass Theme Styling */
    .stApp { background-color: #0b0f17; color: #e6edf3; }
    .main-title { font-size: 2.1rem; font-weight: 800; color: #ffffff; margin-bottom: 1.2rem; }
    
    .bridge-banner { 
        background-color: #0d1e36; 
        border-left: 4px solid #2f81f7; 
        padding: 1rem 1.2rem; 
        border-radius: 6px; 
        margin-bottom: 1.2rem; 
    }
    .bridge-title { color: #58a6ff; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.2rem; }
    .bridge-text { color: #a5d6ff; font-size: 0.92rem; line-height: 1.4; }

    .metric-card { 
        background-color: #131d2a; 
        border: 1px solid #213043; 
        border-radius: 8px; 
        padding: 1.25rem; 
        height: 100%; 
    }
    .metric-label { font-size: 0.85rem; font-weight: 600; color: #8b949e; margin-bottom: 0.4rem; }
    .metric-value { font-size: 2.1rem; font-weight: 800; color: #ffffff; margin-bottom: 0.6rem; }
    .metric-basis { font-size: 0.78rem; color: #6e7681; }

    /* Active Executive Directive HUD Box */
    .directive-box {
        background-color: #0a192f;
        border: 1px solid #1e3a8a;
        border-radius: 8px;
        padding: 1.2rem;
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }
    .directive-title { font-size: 0.85rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 0.4rem; }
    .directive-text { font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 0.8rem; }
    .directive-stats { font-size: 0.88rem; color: #94a3b8; display: flex; gap: 1.5rem; margin-bottom: 0.6rem; }
    .directive-stat-highlight { color: #4ade80; font-weight: 700; }

    .footer-source { 
        background-color: #0b1626; 
        border: 1px solid #1e2d42; 
        padding: 0.6rem 1rem; 
        border-radius: 6px; 
        font-size: 0.82rem; 
        color: #58a6ff; 
        margin-top: 1.5rem; 
    }

    /* Four-Stage Clearance Tracker */
    .section-heading {
        font-size: 0.85rem;
        font-weight: 700;
        color: #58a6ff;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 1.4rem 0 0.8rem 0;
    }
    .stage-card {
        background-color: #131d2a;
        border: 1px solid #213043;
        border-radius: 8px;
        padding: 1rem;
        height: 100%;
    }
    .stage-index { font-size: 0.72rem; font-weight: 700; color: #2f81f7; text-transform: uppercase; margin-bottom: 0.35rem; }
    .stage-label { font-size: 0.92rem; font-weight: 700; color: #ffffff; margin-bottom: 0.55rem; }
    .stage-meta { font-size: 0.78rem; color: #8b949e; margin-bottom: 0.25rem; }
    .stage-status-flowing { color: #4ade80; font-weight: 700; }
    .stage-status-bottleneck { color: #f87171; font-weight: 700; }
    .stage-status-watch { color: #fbbf24; font-weight: 700; }
    .stage-status-active { color: #38bdf8; font-weight: 700; }

    /* Notebook Lane & Prompting Interface */
    .notebook-lane-panel {
        background-color: #131d2a;
        border: 1px solid #213043;
        border-left: 3px solid #2f81f7;
        border-radius: 8px;
        padding: 1rem 1.15rem;
        height: 100%;
        margin-bottom: 0.8rem;
    }
    .notebook-lane-eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        color: #2f81f7;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
    }
    .notebook-lane-copy {
        font-size: 0.9rem;
        color: #a5d6ff;
        line-height: 1.45;
        margin-bottom: 0.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SIDEBAR ROUTER — initializes from session state already set by ?co= / ?cl=
# -----------------------------------------------------------------------------
st.sidebar.title("Executive Navigation")
st.sidebar.markdown("**Active Sector Surface**")
options = _SECTOR_OPTIONS
sector_keys = _SECTOR_KEYS

# Guarantee widget key is set before selectbox draws (URL already applied above)
if st.session_state.get("sector_book_key") not in sector_keys:
    st.session_state["sector_book_key"] = "ACC_BASELINE"


def _sync_co_query_param():
    """Mirror the active sector shortcode into ?co= after a sidebar change."""
    short = sector_co_short(st.session_state["sector_book_key"])
    current = st.query_params.get("co")
    if isinstance(current, (list, tuple)):
        current = current[0] if current else ""
    if str(current or "") != short:
        st.query_params["co"] = short
    # Drop legacy ?cl= once ?co= is canonical, so Safari deep links stay stable
    if "cl" in st.query_params:
        del st.query_params["cl"]


# No index= here: session_state["sector_book_key"] (set from ?co=/?cl= above)
# is the single source of truth so the dropdown opens on PJM, not ACC.
selected_key = st.sidebar.selectbox(
    "Select Sector Book",
    options=sector_keys,
    format_func=lambda x: options[x],
    key="sector_book_key",
    on_change=_sync_co_query_param,
    label_visibility="collapsed",
)

# Keep address bar on the active shortcode (PJM, NHS, …) without snapping to ACC
_sync_co_query_param()

st.sidebar.caption(f"Deep link: `?co={sector_co_short(selected_key)}`")
if _matched_sector and _matched_sector == selected_key and _co_raw:
    st.sidebar.success(
        f"URL loaded `?{_co_param_name}={_co_raw}` → {selected_key} "
        f"({sector_co_short(selected_key)})"
    )

data = get_sector_book(selected_key)

# -----------------------------------------------------------------------------
# 3. HEADER & OPERATIONAL BRIDGE
# -----------------------------------------------------------------------------
if _matched_sector and _co_raw and selected_key == _matched_sector:
    st.caption(
        f"Board glass routed from URL `?{_co_param_name}={_co_raw}` → "
        f"**{sector_co_short(selected_key)}** / `{selected_key}`"
    )

st.markdown(f'<div class="main-title">{data["title"]}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="bridge-banner">
    <div class="bridge-title">⚡ DIRECT OPERATIONAL BRIDGE</div>
    <div class="bridge-text">{data["bridge_text"]}</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. LAYER 1: 3-KPI STRUCTURAL MIRROR CARDS
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for col, m in zip(cols, data["metrics"]):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{m['label']} 🛈</div>
            <div class="metric-value">{m['value']}</div>
            <div class="metric-basis">📊 Basis: {m['basis']}</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. CLOSED-LOOP ACTIVE DIRECTIVE TELEMETRY HUD (BOARD COMMAND LEVEL)
# -----------------------------------------------------------------------------
ad = data.get("active_directive", {})
if ad:
    st.markdown(f"""
    <div class="directive-box">
        <div class="directive-title">⚡ TIER 1: ACTIVE EXECUTIVE DIRECTIVE TELEMETRY</div>
        <div class="directive-text">{ad['title']}</div>
        <div class="directive-stats">
            <span>Progress: <span class="directive-stat-highlight">{ad['completion_pct']}% Executed</span></span>
            <span>Compliant Units: <span class="directive-stat-highlight">{ad['compliant_units']}</span></span>
            <span>Weekly Burn Reclaimed: <span class="directive-stat-highlight">{ad['burn_reclaimed']}</span></span>
            <span>Elapsed: {ad['days_active']} Days</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(ad['completion_pct'] / 100.0)

# -----------------------------------------------------------------------------
# 6. FOUR-STAGE CLEARANCE TRACKER
# -----------------------------------------------------------------------------
st.markdown('<div class="section-heading">🛤️ Four-Stage Clearance Tracker</div>', unsafe_allow_html=True)
stages = data.get("clearance_stages", [])
if stages:
    stage_cols = st.columns(4)
    status_class = {
        "Flowing": "stage-status-flowing",
        "Bottleneck": "stage-status-bottleneck",
        "Watch": "stage-status-watch",
        "Active": "stage-status-active",
    }
    for col, stage in zip(stage_cols, stages):
        with col:
            cls = status_class.get(stage["status"], "stage-status-active")
            st.markdown(f"""
            <div class="stage-card">
                <div class="stage-index">Stage {stage['stage']} of 4</div>
                <div class="stage-label">{stage['label']}</div>
                <div class="stage-meta">Units in stage: <strong style="color:#e6edf3;">{stage['units']}</strong></div>
                <div class="stage-meta">Cleared: <strong style="color:#e6edf3;">{stage['cleared_pct']}%</strong></div>
                <div class="stage-meta">Owner: {stage['owner']}</div>
                <div class="stage-meta">Status: <span class="{cls}">{stage['status']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(stage["cleared_pct"] / 100.0)

# -----------------------------------------------------------------------------
# 7. COI (COST OF INACTION) METRICS
# -----------------------------------------------------------------------------
st.markdown('<div class="section-heading">📉 COI Metrics · Cost of Inaction</div>', unsafe_allow_html=True)
coi_metrics = data.get("coi_metrics", [])
if coi_metrics:
    coi_cols = st.columns(3)
    for col, m in zip(coi_cols, coi_metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{m['label']} 🛈</div>
                <div class="metric-value">{m['value']}</div>
                <div class="metric-basis">📊 Basis: {m['basis']}</div>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. TIER 2 & 3: MANAGER OPERATIONAL DRIFT & ACTIONABLE CLEARANCE
# -----------------------------------------------------------------------------
with st.expander("🔍 TIER 2 & 3: Manager Operational View — Inspect Site Drift & Execute Clearance", expanded=True):
    st.markdown("### 📊 Operational Unit Breakdown")
    l2_data = data.get("layer2_operations", [])
    if l2_data:
        st.table(l2_data)
    
    st.markdown("---")
    st.markdown("### ⚡ Layer 3: Executive Action Trigger")
    st.info("Override administrative queue friction and issue immediate compliance sign-off.")
    if st.button("Execute Immediate Operational Clearance Directive"):
        st.success(f"Clearance Directive Logged for {selected_key}. Ground-Truth Telemetry updated.")

# -----------------------------------------------------------------------------
# 9. NOTEBOOK LANE & PROMPTING INTERFACE (main-page surface)
# Formerly pages/02_AI_Assistant.py — kept in-app after multipage removal.
# -----------------------------------------------------------------------------
def _ensure_notebook_default_query(sector_code: str) -> str:
    """Return a safe string default query; always defined, never None."""
    if DEFAULT_QUERY_KEY not in st.session_state:
        st.session_state[DEFAULT_QUERY_KEY] = ""
    if LAST_SECTOR_KEY not in st.session_state:
        st.session_state[LAST_SECTOR_KEY] = sector_code

    if st.session_state[LAST_SECTOR_KEY] != sector_code:
        st.session_state[LAST_SECTOR_KEY] = sector_code
        st.session_state[DEFAULT_QUERY_KEY] = (
            f"Summarize Structural Mirror KPIs and Layer 2 drift for {sector_code}."
        )

    raw = st.session_state.get(DEFAULT_QUERY_KEY, "")
    if raw is None:
        raw = ""
    return str(raw)


st.markdown(
    '<div class="section-heading">📓 Notebook Lane &amp; Prompting Interface</div>',
    unsafe_allow_html=True,
)
st.caption(
    f"Executive synthesis console · grounded on `{sector_co_short(selected_key)}` / `{selected_key}`"
)

default_query = _ensure_notebook_default_query(selected_key)
metrics = list(data.get("metrics", []))
layer2_ops = list(data.get("layer2_operations", []))

lane_col, prompt_col = st.columns(2)

with lane_col:
    st.markdown(
        """
        <div class="notebook-lane-panel">
            <div class="notebook-lane-eyebrow">Notebook Lane</div>
            <div class="notebook-lane-copy">
                Ground the briefing against Structural Mirror KPIs, then open the live
                Gemini Notebook Manifest for role-dynamic synthesis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if BRIEFING_AUDIO_PATH.is_file():
        st.audio(str(BRIEFING_AUDIO_PATH), format="audio/mp3")
    else:
        st.caption("Audio briefing missing (`public/briefing.mp3`).")
    st.link_button(
        "Open Live Gemini Notebook Manifest",
        GEMINI_NOTEBOOK_URL,
        use_container_width=True,
    )
    st.caption(
        "Notebook hosts typically block iframe embeds — use the button above "
        "to open the live Gemini Notebook Manifest in a new tab."
    )

with prompt_col:
    st.markdown(
        """
        <div class="notebook-lane-panel">
            <div class="notebook-lane-eyebrow">Prompting Interface</div>
            <div class="notebook-lane-copy">
                Ask for Macro Valuation, Velocity Friction, Actionable Controllable Loss,
                or Layer 2 site/queue drift clearances.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Session-state owns the widget value — do NOT pass value=default_query.
    if QUERY_INPUT_KEY not in st.session_state:
        st.session_state[QUERY_INPUT_KEY] = default_query or ""

    user_query = st.text_area(
        "Executive query",
        height=120,
        key=QUERY_INPUT_KEY,
        placeholder="e.g., Where is actionable controllable loss concentrated?",
        label_visibility="collapsed",
    )

    run_col, reset_col = st.columns(2)
    with run_col:
        run_query = st.button(
            "Run Assistant Brief",
            type="primary",
            use_container_width=True,
            key="notebook_lane_run_brief",
        )
    with reset_col:
        if st.button("Reset Query", use_container_width=True, key="notebook_lane_reset"):
            st.session_state[DEFAULT_QUERY_KEY] = ""
            st.session_state[QUERY_INPUT_KEY] = ""
            st.rerun()

    if user_query is not None:
        st.session_state[DEFAULT_QUERY_KEY] = str(user_query)
        default_query = str(user_query)

if run_query:
    prompt = str(user_query or default_query or "").strip()
    if not prompt:
        st.warning("Enter a query before running the assistant brief.")
    else:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        st.markdown("### Assistant Brief")
        st.caption(f"Generated {ts} · sector {selected_key}")

        if metrics:
            mcols = st.columns(min(len(metrics), 3))
            for col, card_cfg in zip(mcols, metrics):
                with col:
                    st.metric(
                        str(card_cfg.get("label", "KPI")),
                        str(card_cfg.get("value", "-")),
                        help=str(card_cfg.get("basis", "")),
                    )

        st.markdown("#### Response")
        st.write(
            f"Interpreted query against **{options.get(selected_key, selected_key)}**. "
            f"Prompt: _{prompt}_"
        )
        if layer2_ops:
            top = layer2_ops[0]
            st.info(
                f"Layer 2 hotspot: {top.get('site', 'Site')} · "
                f"drift {top.get('drift', '-')} · burn {top.get('burn', '-')} · "
                f"{top.get('bottleneck', '')}"
            )
            if st.button(
                "Trigger Layer 3 Actionable Clearance",
                key="notebook_lane_layer3",
                use_container_width=True,
            ):
                st.success(
                    f"Layer 3 Actionable Clearance staged for {selected_key}."
                )
        else:
            st.write(
                "No Layer 2 site/queue metrics are configured for this sector book."
            )

# -----------------------------------------------------------------------------
# 10. FOOTER GROUND-TRUTH CITATION
# -----------------------------------------------------------------------------
st.markdown(f'<div class="footer-source">{data["footer"]}</div>', unsafe_allow_html=True)
