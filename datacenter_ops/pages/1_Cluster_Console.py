"""Cluster operations console — live request-processing simulation page.

Alerts surface when (clock + tick), where (region / AZ / rack / node), and why
(cause codes such as queue_overflow, disk_failure, dependency_timeout).
"""

from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from simulation import (
    ClusterState,
    NodeState,
    error_rate,
    step_simulation,
    throughput,
    utilization,
)

STATE_COLORS = {
    NodeState.IDLE: "#6b7280",
    NodeState.PROCESSING: "#22c55e",
    NodeState.THROTTLED: "#f59e0b",
    NodeState.DOWN: "#ef4444",
}


def init_state() -> None:
    if "cluster" not in st.session_state:
        cluster = ClusterState()
        cluster.reset(node_count=5)
        st.session_state.cluster = cluster


def render_node_card(node) -> None:
    color = STATE_COLORS.get(node.state, "#6b7280")
    cause_line = (
        f'<div style="font-size: 0.75rem; color: #fbbf24; margin-top: 4px;">'
        f"Why: {node.last_cause}</div>"
        if node.last_cause != "—"
        else ""
    )
    st.markdown(
        f"""
        <div style="
            border: 1px solid #34495e;
            border-left: 6px solid {color};
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 8px;
            background: #171c24;
        ">
            <div style="font-weight: 600; font-size: 0.95rem; color: #f5f5f5;">{node.name}</div>
            <div style="color: {color}; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em;">
                {node.state.value}
            </div>
            <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 4px;">
                Where: {node.region} / {node.az} / {node.rack}
            </div>
            <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 6px;">
                Queue: {node.queue}/{node.capacity} &nbsp;|&nbsp; Served: {node.served} &nbsp;|&nbsp; Errors: {node.errors}
            </div>
            {cause_line}
        </div>
        """,
        unsafe_allow_html=True,
    )


init_state()
cluster: ClusterState = st.session_state.cluster

with st.sidebar:
    st.title("🖧 Cluster Controls")
    st.caption("Request-processing tick simulation")

    node_count = st.slider("Nodes", min_value=3, max_value=8, value=len(cluster.nodes), step=1)
    cluster.speed = st.slider("Tick speed (sec)", min_value=0.2, max_value=2.0, value=float(cluster.speed), step=0.1)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("▶ Start", use_container_width=True):
            cluster.running = True
            cluster.log.append("[CMD] Simulation started.")
    with col_b:
        if st.button("⏸ Pause", use_container_width=True):
            cluster.running = False
            cluster.log.append("[CMD] Simulation paused.")
    with col_c:
        if st.button("↺ Reset", use_container_width=True):
            cluster.reset(node_count=node_count)
            st.rerun()

st.title("Cluster Operations Console")
st.markdown(
    "Live cluster metrics, node status, and alerts that answer "
    "**when** / **where** / **why**."
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Tick", f"{cluster.tick:,}")
k2.metric("Served", f"{cluster.total_served:,}")
k3.metric("Errors", f"{cluster.total_errors:,}")
k4.metric("Utilization", f"{utilization(cluster)}%")
k5.metric("Throughput", f"{throughput(cluster)}/min")

status_label = "🟢 RUNNING" if cluster.running else "⏸ PAUSED"
st.caption(
    f"Status: {status_label}  ·  Speed: {cluster.speed}s/tick  ·  "
    f"Nodes: {len(cluster.nodes)}  ·  Error rate: {error_rate(cluster)}%  ·  "
    f"Alerts: {len(cluster.alerts)}"
)

st.divider()

left, right = st.columns([1, 1.2])

with left:
    st.subheader("Cluster Nodes")
    for node in cluster.nodes:
        render_node_card(node)

with right:
    st.subheader("Alerts (When / Where / Why)")
    if cluster.alerts:
        alert_rows = [
            {
                "When": alert.when,
                "Tick": alert.tick,
                "Where": alert.where,
                "Why": alert.why,
                "Detail": alert.detail,
            }
            for alert in reversed(cluster.alerts[-30:])
        ]
        st.dataframe(
            pd.DataFrame(alert_rows),
            use_container_width=True,
            hide_index=True,
            height=320,
        )
    else:
        st.info("No alerts yet. Start the simulation to emit when/where/why events.")

    st.subheader("Request Log")
    log_text = "\n".join(reversed(cluster.log[-30:]))
    st.text_area(
        "Events (newest first)",
        value=log_text,
        height=220,
        disabled=True,
        label_visibility="collapsed",
    )

if cluster.running:
    step_simulation(cluster)
    time.sleep(cluster.speed)
    st.rerun()
