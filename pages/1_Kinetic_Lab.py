"""Kinetic Lab — live acquisition console for unlocked research nodes."""

from __future__ import annotations

import time
import html

import streamlit as st

from config import TENANT_CONFIG, THEME, research_nodes
from kinetic_simulation import (
    AthleteState,
    KineticLabState,
    mean_asymmetry,
    mean_shear,
    readiness,
    step_simulation,
)

STATE_COLORS = {
    AthleteState.IDLE: "#64748b",
    AthleteState.LOADING: "#38bdf8",
    AthleteState.CUTTING: "#10b981",
    AthleteState.RECOVERING: "#f59e0b",
    AthleteState.FLAGGED: "#ef4444",
}


def _inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
        .stApp {{
            background: radial-gradient(1000px 500px at 0% 0%, #064e3b 0%, transparent 50%),
                        {THEME["bg"]};
            color: {THEME["text"]};
            font-family: "IBM Plex Sans", sans-serif;
        }}
        [data-testid="stSidebar"] {{
            background: {THEME["card"]};
            border-right: 1px solid {THEME["border"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ensure_vault_session() -> None:
    if "credits" not in st.session_state:
        st.session_state.credits = int(TENANT_CONFIG["initial_credits"])
    if "unlocked_nodes" not in st.session_state:
        st.session_state.unlocked_nodes = set()


def init_lab() -> None:
    if "kinetic_lab" not in st.session_state:
        lab = KineticLabState()
        lab.reset(athlete_count=5)
        st.session_state.kinetic_lab = lab


def render_athlete_card(athlete) -> None:
    color = STATE_COLORS.get(athlete.state, "#64748b")
    safe_name = html.escape(str(athlete.name), quote=True)
    safe_state = html.escape(str(athlete.state.value), quote=True)
    st.markdown(
        f"""
        <div style="
            border: 1px solid {THEME["border"]};
            border-left: 5px solid {color};
            background: {THEME["card"]};
            padding: 12px 14px;
            margin-bottom: 8px;
        ">
            <div style="font-weight: 600; color: {THEME["text"]};">{safe_name}</div>
            <div style="color: {color}; font-size: 0.78rem; text-transform: uppercase;
                        letter-spacing: 0.05em; font-family: IBM Plex Mono, monospace;">
                {safe_state}
            </div>
            <div style="font-size: 0.8rem; color: {THEME["muted"]}; margin-top: 6px;">
                Shear: {athlete.shear_peak_n:.1f} N &nbsp;|&nbsp;
                Asym: {athlete.asymmetry_pct:.1f}% &nbsp;|&nbsp;
                Tissue debt: {athlete.tissue_debt:.1f} &nbsp;|&nbsp;
                Samples: {athlete.samples}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_inject_theme()
_ensure_vault_session()
init_lab()

lab: KineticLabState = st.session_state.kinetic_lab
lab.unlocked_nodes = set(st.session_state.unlocked_nodes)
nodes = research_nodes()
unlocked = st.session_state.unlocked_nodes

st.title("Kinetic Lab")
st.caption(
    f"{TENANT_CONFIG['tenant_identity']} · {TENANT_CONFIG['active_sector_code']} · "
    "Live athlete acquisition driven by unlocked research nodes."
)

with st.sidebar:
    st.markdown("**Lab controls**")
    st.caption(f"Credits on vault: {st.session_state.credits:,}")
    athlete_count = st.slider(
        "Athletes",
        min_value=3,
        max_value=8,
        value=len(lab.athletes),
        step=1,
    )
    lab.speed = st.slider(
        "Tick speed (sec)",
        min_value=0.2,
        max_value=2.0,
        value=float(lab.speed),
        step=0.1,
    )

    st.markdown("**Node channels**")
    for node in nodes:
        mark = "●" if node["id"] in unlocked else "○"
        st.text(f"{mark} {node['short_name']}")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Start", use_container_width=True):
            if not unlocked:
                st.warning("Unlock at least one research node on the Vault page.")
            else:
                lab.running = True
                lab.log.append("[CMD] Acquisition started.")
    with c2:
        if st.button("Pause", use_container_width=True):
            lab.running = False
            lab.log.append("[CMD] Acquisition paused.")
    with c3:
        if st.button("Reset", use_container_width=True):
            lab.reset(athlete_count=athlete_count)
            lab.unlocked_nodes = set(unlocked)
            st.rerun()

if not unlocked:
    st.info(
        "No research nodes are online. Return to **University Operations Vault** "
        "and spend credits to unlock Node 1.1–1.3."
    )

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Tick", f"{lab.tick:,}")
k2.metric("Squad readiness", f"{readiness(lab)}%")
k3.metric("Mean shear", f"{mean_shear(lab)} N")
k4.metric("Mean asymmetry", f"{mean_asymmetry(lab)}%")
k5.metric(
    "Alerts",
    f"{lab.shear_alerts + lab.asymmetry_alerts}",
)

status = "RUNNING" if lab.running else "PAUSED"
st.caption(
    f"Status: {status} · Speed: {lab.speed}s/tick · "
    f"Channels: {len(unlocked)}/{len(nodes)} · "
    f"Recovery clears: {lab.recovery_clears}"
)

st.divider()
left, right = st.columns([1, 1.15])

with left:
    st.subheader("Athlete channels")
    for athlete in lab.athletes:
        render_athlete_card(athlete)

with right:
    st.subheader("Acquisition log")
    log_text = "\n".join(reversed(lab.log[-30:]))
    st.text_area(
        "Events",
        value=log_text,
        height=520,
        disabled=True,
        label_visibility="collapsed",
    )

if lab.running:
    step_simulation(lab)
    time.sleep(lab.speed)
    st.rerun()
