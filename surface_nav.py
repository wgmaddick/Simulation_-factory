"""Shared Streamlit surface + command-level navigation.

Streamlit Community Cloud only shows multipage entries when navigation is
enabled *or* when the app renders explicit `st.page_link` controls. This app
keeps `showSidebarNavigation = false` for private iPad chrome, so pages must be
linked explicitly or they appear to be missing.
"""

from __future__ import annotations

from typing import Literal

import streamlit as st

SurfaceKey = Literal["home", "kinetic_lab", "ai_assistant"]

# Paths are relative to the app root (where `streamlit run app.py` starts).
SURFACE_PAGES: tuple[dict[str, str], ...] = (
    {
        "key": "home",
        "path": "app.py",
        "label": "Executive Command",
        "hint": "Home · Structural Mirror · Interface A/B",
    },
    {
        "key": "kinetic_lab",
        "path": "pages/1_Kinetic_Lab.py",
        "label": "Kinetic Lab",
        "hint": "Live acquisition · Adaptive Drift θ",
    },
    {
        "key": "ai_assistant",
        "path": "pages/02_AI_Assistant.py",
        "label": "AI Assistant",
        "hint": "Audio briefing · Layer 2/3 synthesis",
    },
)

COMMAND_LEVELS: tuple[dict[str, str], ...] = (
    {
        "key": "layer1",
        "label": "Layer 1 · Structural Mirror",
        "hint": "3 KPI cards (Macro · Velocity · Controllable Loss)",
    },
    {
        "key": "layer2",
        "label": "Layer 2 · Operations View",
        "hint": "Site / queue drift drill-down",
    },
    {
        "key": "layer3",
        "label": "Layer 3 · Actionable Clearance",
        "hint": "Clearance trigger on Layer 2 hotspot",
    },
    {
        "key": "interface_a",
        "label": "Interface A · Global Portfolio",
        "hint": "Scheme-wide ledger and cohort pads",
    },
    {
        "key": "interface_b",
        "label": "Interface B · Claim Drill-down",
        "hint": "Individual dossier + alignment vector",
    },
)


def render_surface_page_links(*, active: SurfaceKey = "home", compact: bool = False) -> None:
    """Render clickable links to every Streamlit multipage surface."""
    st.markdown(
        "<div class='ipad-top-nav' role='navigation' aria-label='App surfaces'>"
        "<span class='nav-mark'>SURFACES</span>"
        "<span class='nav-hint'>Pages · levels · role-gated command decks</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(len(SURFACE_PAGES))
    for col, page in zip(cols, SURFACE_PAGES):
        with col:
            label = page["label"]
            if page["key"] == active:
                label = f"● {label}"
            st.page_link(page["path"], label=label, use_container_width=True)
            if not compact:
                st.caption(page["hint"])


def render_sidebar_surface_links(*, active: SurfaceKey = "home") -> None:
    """Sidebar twin of the top surface nav (private chrome keeps host nav off)."""
    st.markdown("### APP SURFACES")
    for page in SURFACE_PAGES:
        label = page["label"]
        if page["key"] == active:
            label = f"● {label}"
        st.page_link(page["path"], label=label, use_container_width=True)
    st.caption("Kinetic Lab and AI Assistant are separate Streamlit pages.")


def render_command_level_controls(*, sector_code: str, global_view_label: str) -> str:
    """Expose Layer 1/2/3 and Interface A/B as an explicit control strip.

    Returns the selected command-level key.
    """
    st.markdown("### COMMAND LEVELS")
    st.caption(
        "Structural Mirror and Interface layers live on Executive Command — "
        "they are not separate Streamlit pages."
    )

    level_labels = [item["label"] for item in COMMAND_LEVELS]
    label_to_key = {item["label"]: item["key"] for item in COMMAND_LEVELS}
    default_label = level_labels[0]
    current_key = st.session_state.get("command_level_focus", "layer1")
    for item in COMMAND_LEVELS:
        if item["key"] == current_key:
            default_label = item["label"]
            break

    selected_label = st.radio(
        "Active command level",
        options=level_labels,
        index=level_labels.index(default_label),
        horizontal=True,
        key="command_level_radio",
        help="Jump between Structural Mirror layers and Interface A/B.",
    )
    selected_key = label_to_key[selected_label]
    st.session_state["command_level_focus"] = selected_key

    hint = next(
        (item["hint"] for item in COMMAND_LEVELS if item["key"] == selected_key),
        "",
    )
    st.caption(hint)

    # Wire level selection into existing session flags used by the dashboard.
    layer2_flag = f"layer2_open_{sector_code}"
    layer2_toggle = f"layer2_toggle_{sector_code}"
    if selected_key in {"layer1", "layer2", "layer3"}:
        # Structural Mirror layers only render on Interface A (global portfolio).
        st.session_state["audit_view_selection"] = global_view_label
        st.session_state["cohort_mode"] = False
        if selected_key in {"layer2", "layer3"}:
            st.session_state[layer2_flag] = True
            st.session_state[layer2_toggle] = True
        else:
            st.session_state[layer2_flag] = False
            st.session_state[layer2_toggle] = False

    if selected_key == "interface_a":
        st.session_state["audit_view_selection"] = global_view_label
        st.session_state["cohort_mode"] = False
        st.session_state[layer2_flag] = False
        st.session_state[layer2_toggle] = False
    elif selected_key == "interface_b":
        # Prefer an existing claim selection; otherwise seed the first known token.
        current = st.session_state.get("audit_view_selection", global_view_label)
        if current == global_view_label:
            st.session_state["audit_view_selection"] = "AAT-Claimant-Delta-2026"

    return selected_key
