"""Polymorphic Kinetic Vault — unified Streamlit shell for all tenant profiles."""

from __future__ import annotations

import hashlib
from typing import Any

import streamlit as st

from config import (
    DEFAULT_PROFILE_KEY,
    THEME,
    get_profile,
    metric_slots,
    node_by_id,
    profile_keys,
    research_nodes,
    total_unlock_cost,
)

st.set_page_config(
    page_title="Kinetic Vault",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

        .stApp {{
            background: radial-gradient(1200px 600px at 10% -10%, #064e3b 0%, transparent 55%),
                        radial-gradient(900px 500px at 100% 0%, #0f172a 0%, transparent 50%),
                        {THEME["bg"]};
            color: {THEME["text"]};
            font-family: "IBM Plex Sans", sans-serif;
        }}
        [data-testid="stSidebar"] {{
            background: {THEME["card"]};
            border-right: 1px solid {THEME["border"]};
        }}
        [data-testid="stSidebar"] * {{
            color: {THEME["text"]};
        }}
        h1, h2, h3, h4 {{
            font-family: "IBM Plex Sans", sans-serif !important;
            letter-spacing: -0.02em;
        }}
        .vault-brand {{
            font-size: clamp(1.8rem, 3vw, 2.6rem);
            font-weight: 700;
            color: {THEME["text"]};
            margin: 0 0 0.25rem 0;
            line-height: 1.15;
        }}
        .vault-brand span {{ color: {THEME["accent"]}; }}
        .vault-sub {{
            color: {THEME["muted"]};
            font-size: 0.95rem;
            margin-bottom: 1.25rem;
        }}
        .sector-chip {{
            display: inline-block;
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            color: {THEME["accent"]};
            border: 1px solid {THEME["accent"]};
            background: {THEME["accent_soft"]};
            padding: 0.35rem 0.7rem;
            margin-bottom: 0.75rem;
        }}
        .node-card {{
            border: 1px solid {THEME["border"]};
            background: {THEME["card"]};
            padding: 1.1rem 1.2rem;
            margin-bottom: 0.85rem;
            border-left: 4px solid {THEME["border"]};
        }}
        .node-card.unlocked {{
            border-left-color: {THEME["accent"]};
            box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.25);
        }}
        .node-meta {{
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.78rem;
            color: {THEME["muted"]};
            margin-bottom: 0.35rem;
        }}
        .node-title {{
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.45rem;
            color: {THEME["text"]};
        }}
        .node-body {{
            font-size: 0.9rem;
            color: {THEME["muted"]};
            line-height: 1.45;
        }}
        .yield-line {{
            margin-top: 0.65rem;
            font-size: 0.85rem;
            color: {THEME["accent"]};
        }}
        .credit-panel {{
            border: 1px solid {THEME["border"]};
            background: linear-gradient(160deg, {THEME["card"]} 0%, #022c22 140%);
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
        }}
        .credit-value {{
            font-family: "IBM Plex Mono", monospace;
            font-size: 2rem;
            font-weight: 500;
            color: {THEME["accent"]};
            line-height: 1;
        }}
        .panel {{
            border: 1px solid {THEME["border"]};
            background: {THEME["card"]};
            padding: 1rem 1.1rem;
            min-height: 220px;
        }}
        .panel-title {{
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {THEME["muted"]};
            margin-bottom: 0.75rem;
            font-weight: 600;
        }}
        .drop-zone {{
            border: 2px dashed {THEME["border"]};
            background: rgba(2, 6, 23, 0.45);
            padding: 1.5rem 1rem;
            text-align: center;
            color: {THEME["muted"]};
        }}
        .sentinel-box {{
            border: 1px solid rgba(127, 29, 29, 0.55);
            background: rgba(69, 10, 10, 0.25);
            padding: 0.9rem 1rem;
            margin-top: 0.75rem;
        }}
        .heal-box {{
            border: 1px solid {THEME["accent"]};
            background: {THEME["accent_soft"]};
            padding: 0.85rem 1rem;
            margin-top: 0.75rem;
            color: {THEME["text"]};
            font-size: 0.88rem;
        }}
        div[data-testid="stMetricValue"] {{
            color: {THEME["accent"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _empty_profile_state(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "credits": int(profile["initial_credits"]),
        "unlocked_nodes": set(),
        "unlock_log": [],
        "media_name": None,
        "media_kind": None,
        "selected_node_id": None,
        "speech": "",
        "verdict": None,
        "sentinel": None,
        "heal_notice": None,
    }


def _init_session() -> None:
    if "active_profile_key" not in st.session_state:
        st.session_state.active_profile_key = DEFAULT_PROFILE_KEY
    if "vault_state" not in st.session_state:
        st.session_state.vault_state = {
            key: _empty_profile_state(get_profile(key)) for key in profile_keys()
        }


def _active_state() -> dict[str, Any]:
    return st.session_state.vault_state[st.session_state.active_profile_key]


def _switch_profile(profile_key: str) -> None:
    if profile_key == st.session_state.active_profile_key:
        return
    st.session_state.active_profile_key = profile_key


def unlock_node(node_id: str, cost: int, label: str) -> tuple[bool, str]:
    state = _active_state()
    if node_id in state["unlocked_nodes"]:
        return False, "Already unlocked."
    if state["credits"] < cost:
        return False, f"Insufficient credits ({state['credits']} < {cost})."
    state["credits"] -= cost
    state["unlocked_nodes"].add(node_id)
    state["unlock_log"].append(
        f"Unlocked {label} (−{cost} credits). Balance: {state['credits']}."
    )
    if state["selected_node_id"] is None:
        state["selected_node_id"] = node_id
    return True, f"Unlocked. {cost} credits spent."


def _should_trigger_sentinel(node_id: str, speech: str) -> bool:
    triggers = (
        "hamstring",
        "tension",
        "asymmetry",
        "torque",
        "pain",
        "spike",
        "override",
        "risk",
        "shear",
        "overload",
        "thermal",
        "vibration",
        "ankle",
    )
    lowered = speech.lower()
    hits = sum(1 for word in triggers if word in lowered)
    digest = hashlib.sha256(f"sentinel:{node_id}:{lowered}".encode()).hexdigest()
    rnd = int(digest[:8], 16) / 0xFFFFFFFF
    return hits >= 1 or rnd < 0.22


def _execute_analysis(profile: dict[str, Any], node_id: str, speech: str) -> None:
    state = _active_state()
    node = node_by_id(profile["key"], node_id)
    if node is None or node_id not in state["unlocked_nodes"]:
        st.error("Select an unlocked research node before executing analysis.")
        return

    verdicts = profile["verdicts"]
    base = verdicts.get(node_id, "Analysis complete.")
    if speech.strip():
        base = f'{base} Query context noted: “{speech.strip()[:120]}”.'
    state["verdict"] = base
    state["heal_notice"] = None

    if _should_trigger_sentinel(node_id, speech):
        state["sentinel"] = dict(profile["sentinel"].get(node_id, {}))
    else:
        state["sentinel"] = None

    state["unlock_log"].append(
        f"Deep analysis executed on {node['short_name']}"
        + (" · SENTINEL" if state["sentinel"] else " · clear")
    )


def _confirm_rotation(candidate: str) -> None:
    state = _active_state()
    state["heal_notice"] = (
        f"Rotated **{candidate}** into the active slot. Cascaded self-heal to "
        "Sports Medicine (tape profile), Equipment Logistics (spike inventory), "
        "and the athlete’s Portable Personal Vault (NIL passport)."
    )
    state["unlock_log"].append(f"Roster rotation confirmed → {candidate} · self-heal cascade dispatched.")


def _format_metric(value: float, unit: str) -> str:
    if unit == "%":
        return f"{value:.1f}%"
    if unit == "°C":
        return f"{value:.1f}°C"
    if unit == "Hz":
        return f"{value:.1f} Hz"
    if unit == "N·m":
        return f"{value:.0f} N·m"
    if unit == "N":
        return f"{value:.0f} N"
    if value == int(value):
        return f"{int(value)} {unit}".strip()
    return f"{value:.1f} {unit}".strip()


def _metric_values(profile_key: str, unlocked: set[str]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for slot in metric_slots(profile_key):
        value = slot["unlocked_boost"] if slot["node_id"] in unlocked else slot["baseline"]
        rows.append((slot["label"], _format_metric(float(value), slot["unit"])))
    return rows


_inject_theme()
_init_session()

keys = profile_keys()
labels = {key: get_profile(key)["selector_label"] for key in keys}

with st.sidebar:
    st.markdown("**Vault framework**")
    st.caption("Polymorphic single-page shell — profiles swap the bound data state.")
    selected_label = st.radio(
        "Active vault",
        options=[labels[key] for key in keys],
        index=keys.index(st.session_state.active_profile_key),
        key="vault_selector_radio",
    )
    selected_key = next(key for key, label in labels.items() if label == selected_label)
    if selected_key != st.session_state.active_profile_key:
        _switch_profile(selected_key)
        st.rerun()

    profile = get_profile(st.session_state.active_profile_key)
    state = _active_state()
    nodes = research_nodes(profile["key"])

    st.divider()
    st.markdown(f"**{profile['tenant_identity']}**")
    st.caption(profile["target_domain"].title())
    st.markdown(
        f'<div class="sector-chip">{profile["active_sector_code"]}</div>',
        unsafe_allow_html=True,
    )
    st.metric("Credits remaining", f"{state['credits']:,}")
    st.progress(
        min(1.0, len(state["unlocked_nodes"]) / max(len(nodes), 1)),
        text=f"{len(state['unlocked_nodes'])} / {len(nodes)} nodes online",
    )
    st.caption(
        f"Full unlock cost: {total_unlock_cost(profile['key'])} credits · "
        f"grant {profile['initial_credits']}"
    )
    if st.button("Reset active profile", use_container_width=True):
        st.session_state.vault_state[profile["key"]] = _empty_profile_state(profile)
        st.rerun()

profile = get_profile(st.session_state.active_profile_key)
state = _active_state()
nodes = research_nodes(profile["key"])
unlocked = state["unlocked_nodes"]
credits = state["credits"]
tenant = profile["tenant_identity"]
domain = profile["target_domain"]
sector = profile["active_sector_code"]

brand_parts = tenant.split(" ", 1)
brand_lead = brand_parts[0]
brand_rest = brand_parts[1] if len(brand_parts) > 1 else ""

st.markdown(
    f'<div class="sector-chip">{sector} · {profile["infrastructure_label"].upper()}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="vault-brand">{brand_lead} <span>{brand_rest}</span></p>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="vault-sub">Unified kinetic vault for {domain.lower()}. '
    "Switch tenants to rebind credits, research nodes, and the metrics container "
    "without leaving this page.</p>",
    unsafe_allow_html=True,
)

# --- Metrics container (profile-bound) ---
metric_rows = _metric_values(profile["key"], unlocked)
mcols = st.columns(max(len(metric_rows) + 2, 4))
mcols[0].metric("Credits", f"{credits:,}")
mcols[1].metric("Nodes online", f"{len(unlocked)}/{len(nodes)}")
for index, (label, value) in enumerate(metric_rows):
    mcols[index + 2].metric(label, value)

st.markdown(
    f"""
    <div class="credit-panel">
      <div style="color:{THEME["muted"]};font-size:0.8rem;letter-spacing:0.06em;text-transform:uppercase;">
        Operations credit ledger · {profile["selector_label"]}
      </div>
      <div class="credit-value">{credits:,}</div>
      <div style="color:{THEME["muted"]};font-size:0.85rem;margin-top:0.35rem;">
        Initial grant {profile["initial_credits"]:,} · spent
        {profile["initial_credits"] - credits:,}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Research nodes")
st.caption("Unlock in any order. Node catalog and costs are bound to the active vault profile.")

for node in nodes:
    is_open = node["id"] in unlocked
    status = "ONLINE" if is_open else "LOCKED"
    card_class = "unlocked" if is_open else "locked"
    st.markdown(
        f"""
        <div class="node-card {card_class}">
          <div class="node-meta">{node["id"].upper()} · {status} · COST {node["credit_cost"]} CR</div>
          <div class="node-title">{node["label"]}</div>
          <div class="node-body">{node["summary"]}</div>
          {"<div class='yield-line'>Yield: " + node["unlock_yield"] + "</div>" if is_open else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns([1, 1, 4])
    with cols[0]:
        if is_open:
            st.success("Unlocked")
        else:
            if st.button(
                f"Unlock ({node['credit_cost']} cr)",
                key=f"unlock_{profile['key']}_{node['id']}",
                type="primary",
                use_container_width=True,
            ):
                ok, message = unlock_node(node["id"], node["credit_cost"], node["label"])
                if ok:
                    st.toast(message)
                    st.rerun()
                else:
                    st.error(message)
    with cols[1]:
        st.caption(node["short_name"])

st.divider()
st.subheader("Intake · Orchestration · Advisory")
st.caption(
    "Merged layout from the University Operations console and the AAT Phoenix "
    "asset-infrastructure decision engine."
)

media_col, orch_col, advisory_col = st.columns([4, 3, 3], gap="medium")

with media_col:
    st.markdown(
        '<div class="panel"><div class="panel-title">Column 1 · Media canvas</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="drop-zone">
          <div style="font-weight:700;color:#e2e8f0;margin-bottom:0.35rem;">
            Take your iPhone, video your problem, talk to it, and send it.
          </div>
          Supports raw video telemetry or static images
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Structural intake",
        type=["png", "jpg", "jpeg", "mp4", "mov", "webm"],
        key=f"media_{profile['key']}",
        label_visibility="collapsed",
    )
    if uploaded is not None:
        state["media_name"] = uploaded.name
        state["media_kind"] = "video" if uploaded.type.startswith("video/") else "image"
    status = (
        f"System Intake status: Loaded · {state['media_name']} ({state['media_kind']})"
        if state["media_name"]
        else "System Intake status: Standby"
    )
    st.caption(status)
    st.markdown("</div>", unsafe_allow_html=True)

with orch_col:
    st.markdown(
        '<div class="panel"><div class="panel-title">Column 2 · Orchestration</div>',
        unsafe_allow_html=True,
    )
    unlocked_nodes = [n for n in nodes if n["id"] in unlocked]
    if not unlocked_nodes:
        st.info("Unlock at least one research node to run deep analysis.")
        selected_node_id = None
    else:
        default_id = state["selected_node_id"]
        if default_id not in {n["id"] for n in unlocked_nodes}:
            default_id = unlocked_nodes[0]["id"]
        label_to_id = {n["label"]: n["id"] for n in unlocked_nodes}
        id_to_label = {n["id"]: n["label"] for n in unlocked_nodes}
        choice = st.selectbox(
            "Select research node",
            options=list(label_to_id.keys()),
            index=list(label_to_id.values()).index(default_id),
            key=f"node_select_{profile['key']}",
        )
        selected_node_id = label_to_id[choice]
        state["selected_node_id"] = selected_node_id
        st.caption(id_to_label[selected_node_id])

    speech = st.text_input(
        "Vocal command ingestion",
        placeholder="Or describe the issue for sentinel screening...",
        key=f"speech_{profile['key']}",
    )
    state["speech"] = speech or ""

    if st.button(
        "Execute deep analysis",
        type="primary",
        use_container_width=True,
        disabled=not unlocked_nodes,
        key=f"execute_{profile['key']}",
    ):
        if selected_node_id:
            _execute_analysis(profile, selected_node_id, speech)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with advisory_col:
    st.markdown(
        '<div class="panel"><div class="panel-title">Column 3 · Advisory &amp; sentinel</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Track 1: Expert verdict**")
    st.write(state["verdict"] or "_Awaiting structural intake visualization..._")

    if state["sentinel"]:
        sentinel = state["sentinel"]
        st.markdown(
            f"""
            <div class="sentinel-box">
              <div style="color:#f87171;font-weight:700;font-size:0.72rem;letter-spacing:0.08em;">
                SENTINEL OVERRIDE SIGNAL
              </div>
              <div style="font-weight:700;margin:0.35rem 0;">{sentinel["location"]}</div>
              <div style="color:{THEME["muted"]};font-size:0.85rem;">{sentinel["description"]}</div>
              <div style="margin-top:0.65rem;font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#fca5a5;">
                {sentinel["timeline"]}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("**Roster replacement match matrix**")
        for candidate in profile["roster_replacements"]:
            c1, c2 = st.columns([3, 2])
            with c1:
                st.caption(
                    f"{candidate['name']} · fit {candidate['fit_pct']}% · "
                    f"risk {candidate['risk_band']} {candidate['risk_pct']}%"
                )
            with c2:
                if st.button(
                    "Rotate & self-heal",
                    key=f"rotate_{profile['key']}_{candidate['name']}",
                    use_container_width=True,
                ):
                    _confirm_rotation(candidate["name"])
                    st.rerun()
    else:
        st.caption("Sentinel quiet — no override on the latest analysis pass.")

    if state["heal_notice"]:
        st.markdown(
            f'<div class="heal-box">{state["heal_notice"]}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Session unlock log")
    if state["unlock_log"]:
        for line in reversed(state["unlock_log"][-12:]):
            st.text(f"· {line}")
    else:
        st.caption("No unlocks yet for this profile. Activate a research node to begin.")

with right:
    st.subheader("Bound profile brief")
    st.markdown(
        f"""
        **Tenant:** {tenant}  
        **Domain:** {domain}  
        **Sector:** `{sector}`  
        **Infrastructure:** {profile["infrastructure_label"]}  
        **Initial credits:** {profile["initial_credits"]}  
        **Nodes:** {", ".join(n["short_name"] for n in nodes)}
        """
    )
