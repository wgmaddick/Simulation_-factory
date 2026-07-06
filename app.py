"""Simulation Factory — live console display for Streamlit Community Cloud."""

from __future__ import annotations

import time

import streamlit as st

from simulation import SimulationState, StationState, efficiency, step_simulation, throughput

st.set_page_config(
    page_title="Simulation Factory Console",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

STATE_COLORS = {
    StationState.IDLE: "#6b7280",
    StationState.RUNNING: "#22c55e",
    StationState.BLOCKED: "#f59e0b",
    StationState.MAINTENANCE: "#ef4444",
}


def init_state() -> None:
    if "sim" not in st.session_state:
        sim = SimulationState()
        sim.reset(station_count=5)
        st.session_state.sim = sim


def render_station_card(station) -> None:
    color = STATE_COLORS.get(station.state, "#6b7280")
    st.markdown(
        f"""
        <div style="
            border: 1px solid #e5e7eb;
            border-left: 6px solid {color};
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 8px;
            background: #fafafa;
        ">
            <div style="font-weight: 600; font-size: 0.95rem;">{station.name}</div>
            <div style="color: {color}; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em;">
                {station.state.value}
            </div>
            <div style="font-size: 0.8rem; color: #4b5563; margin-top: 6px;">
                Queue: {station.queue} &nbsp;|&nbsp; Processed: {station.processed} &nbsp;|&nbsp; Defects: {station.defects}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


init_state()
sim: SimulationState = st.session_state.sim

# --- Sidebar controls ---
with st.sidebar:
    st.title("🏭 Factory Controls")
    st.caption("Simulation console — deploy via share.streamlit.io")

    station_count = st.slider("Stations", min_value=3, max_value=8, value=len(sim.stations), step=1)
    sim.speed = st.slider("Tick speed (sec)", min_value=0.2, max_value=2.0, value=float(sim.speed), step=0.1)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("▶ Start", use_container_width=True):
            sim.running = True
            sim.log.append("[CMD] Simulation started.")
    with col_b:
        if st.button("⏸ Pause", use_container_width=True):
            sim.running = False
            sim.log.append("[CMD] Simulation paused.")
    with col_c:
        if st.button("↺ Reset", use_container_width=True):
            sim.reset(station_count=station_count)
            st.rerun()

    st.divider()
    st.markdown("**Deploy checklist**")
    st.markdown(
        "- Push this repo to GitHub\n"
        "- Go to [share.streamlit.io](https://share.streamlit.io)\n"
        "- Create app → select `app.py`"
    )

# --- Header ---
st.title("Simulation Factory Console")
st.markdown("Live production floor metrics, station status, and event log.")

# --- KPI row ---
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Tick", f"{sim.tick:,}")
k2.metric("Output", f"{sim.total_output:,}")
k3.metric("Defects", f"{sim.total_defects:,}")
k4.metric("Efficiency", f"{efficiency(sim)}%")
k5.metric("Throughput", f"{throughput(sim)}/min")

status_label = "🟢 RUNNING" if sim.running else "⏸ PAUSED"
st.caption(f"Status: {status_label}  ·  Speed: {sim.speed}s/tick  ·  Stations: {len(sim.stations)}")

st.divider()

# --- Main layout ---
left, right = st.columns([1, 1.2])

with left:
    st.subheader("Production Floor")
    for station in sim.stations:
        render_station_card(station)

with right:
    st.subheader("Console Log")
    log_text = "\n".join(reversed(sim.log[-30:]))
    st.text_area(
        "Events (newest first)",
        value=log_text,
        height=520,
        disabled=True,
        label_visibility="collapsed",
    )

# --- Auto-advance simulation ---
if sim.running:
    step_simulation(sim)
    time.sleep(sim.speed)
    st.rerun()
