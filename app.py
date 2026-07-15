"""University Operations Vault — Kinetic sector research-node unlock console."""

from __future__ import annotations

import streamlit as st

from config import TENANT_CONFIG, THEME, research_nodes, total_unlock_cost

st.set_page_config(
    page_title="University Operations Vault",
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
        .vault-brand span {{
            color: {THEME["accent"]};
        }}
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
        .node-card.locked {{
            opacity: 0.92;
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
        div[data-testid="stMetricValue"] {{
            color: {THEME["accent"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_session() -> None:
    if "credits" not in st.session_state:
        st.session_state.credits = int(TENANT_CONFIG["initial_credits"])
    if "unlocked_nodes" not in st.session_state:
        st.session_state.unlocked_nodes = set()
    if "unlock_log" not in st.session_state:
        st.session_state.unlock_log = []


def unlock_node(node_id: str, cost: int, label: str) -> tuple[bool, str]:
    if node_id in st.session_state.unlocked_nodes:
        return False, "Already unlocked."
    if st.session_state.credits < cost:
        return False, f"Insufficient credits ({st.session_state.credits} < {cost})."
    st.session_state.credits -= cost
    st.session_state.unlocked_nodes.add(node_id)
    st.session_state.unlock_log.append(
        f"Unlocked {label} (−{cost} credits). Balance: {st.session_state.credits}."
    )
    return True, f"Unlocked. {cost} credits spent."


_inject_theme()
_init_session()

domain = TENANT_CONFIG["target_domain"]
tenant = TENANT_CONFIG["tenant_identity"]
sector = TENANT_CONFIG["active_sector_code"]
nodes = research_nodes()
unlocked = st.session_state.unlocked_nodes
credits = st.session_state.credits

with st.sidebar:
    st.markdown(f"**{tenant}**")
    st.caption(domain.title())
    st.markdown(
        f'<div class="sector-chip">{sector}</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**Research budget**")
    st.metric("Credits remaining", f"{credits:,}")
    st.progress(
        min(1.0, len(unlocked) / max(len(nodes), 1)),
        text=f"{len(unlocked)} / {len(nodes)} nodes online",
    )
    st.caption(f"Full sector unlock cost: {total_unlock_cost()} credits")
    if st.button("Reset vault session", use_container_width=True):
        st.session_state.credits = int(TENANT_CONFIG["initial_credits"])
        st.session_state.unlocked_nodes = set()
        st.session_state.unlock_log = ["Session reset to initial credit grant."]
        st.rerun()
    st.divider()
    st.caption("Open **Kinetic Lab** in the sidebar pages to run live acquisition on unlocked nodes.")

st.markdown(
    f'<div class="sector-chip">{sector} · KINETIC</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="vault-brand">{tenant.split(" ", 1)[0]} '
    f'<span>{tenant.split(" ", 1)[1] if " " in tenant else ""}</span></p>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="vault-sub">Sector research tree for {domain.lower()}. '
    "Spend operations credits to bring kinetic analysis nodes online.</p>",
    unsafe_allow_html=True,
)

top1, top2, top3, top4 = st.columns(4)
top1.metric("Credits", f"{credits:,}")
top2.metric("Nodes online", f"{len(unlocked)}/{len(nodes)}")
top3.metric("Sector", "KINETIC")
top4.metric("Domain", "Athletics")

st.markdown(
    f"""
    <div class="credit-panel">
      <div style="color:{THEME["muted"]};font-size:0.8rem;letter-spacing:0.06em;text-transform:uppercase;">
        Operations credit ledger
      </div>
      <div class="credit-value">{credits:,}</div>
      <div style="color:{THEME["muted"]};font-size:0.85rem;margin-top:0.35rem;">
        Initial grant {TENANT_CONFIG["initial_credits"]:,} · spent
        {TENANT_CONFIG["initial_credits"] - credits:,}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Research nodes")
st.caption("Unlock in any order. Each node permanently enables its Kinetic Lab channels for this session.")

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
                key=f"unlock_{node['id']}",
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
left, right = st.columns(2)
with left:
    st.subheader("Session unlock log")
    if st.session_state.unlock_log:
        for line in reversed(st.session_state.unlock_log[-12:]):
            st.text(f"· {line}")
    else:
        st.caption("No unlocks yet. Activate a research node to begin.")

with right:
    st.subheader("Sector brief")
    st.markdown(
        f"""
        **Tenant:** {tenant}  
        **Domain:** {domain}  
        **Active sector:** `{sector}`  
        **Theme:** slate-950 / slate-900 / emerald-500  

        Kinetic research covers interface shear, pelvic/deceleration asymmetry,
        and micro-tear chronology for intercollegiate performance staff.
        """
    )
