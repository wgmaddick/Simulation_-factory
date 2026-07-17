"""University Operations Vault — Kinetic sector research-node unlock console.

Hosts the foreground timeline-divergence UI (Column 3) and dispatches Path A /
Path B dual-tranche handling via ``ledger.handle_timeline_divergence``.
"""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

import streamlit as st

from config import TENANT_CONFIG, THEME, research_nodes, total_unlock_cost
from ledger import (
    DivergenceUIStatus,
    TimelineDivergenceResult,
    export_sovereign_report_sync,
    format_sovereign_intelligence_report,
    generate_sovereign_intelligence_segment,
    handle_timeline_divergence as _ledger_handle_timeline_divergence,
)

st.set_page_config(
    page_title="University Operations Vault",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Timeline divergence — Column 3 UI + Path A / Path B dispatch
# ---------------------------------------------------------------------------


def update_column_3_ui(
    session_data: MutableMapping[str, Any] | Mapping[str, Any],
    status: str = "PENDING",
) -> None:
    """Update foreground Column 3 to reflect timeline-divergence status.

    Path A → COMPLIANT (standard loop; await manual UI request)
    Path B → OVERRIDE_HAZARD (mutated reality readout)
    """
    normalized = str(status).strip().upper()
    try:
        ui_status = DivergenceUIStatus(normalized)
    except ValueError:
        ui_status = DivergenceUIStatus.PENDING

    st.session_state.column_3_status = ui_status.value
    st.session_state.divergence_session = dict(session_data)
    ui_bucket = st.session_state.divergence_session.setdefault("ui", {})
    ui_bucket["column_3_status"] = ui_status.value

    if isinstance(session_data, dict):
        session_data.setdefault("ui", {})["column_3_status"] = ui_status.value


def handle_timeline_divergence(
    session_data: MutableMapping[str, Any] | Mapping[str, Any],
    path_selection: str,
) -> TimelineDivergenceResult:
    """Conceptual architecture entry-point for Path A / Path B divergence.

    PATH_A — keep process in the standard loop; Column 3 → COMPLIANT.
    PATH_B — dual-tranche: Column 3 → OVERRIDE_HAZARD, then fire
    ``execute_silent_background_export`` for absolute system protection.
    """
    result = _ledger_handle_timeline_divergence(
        session_data,
        path_selection,
        ui_updater=update_column_3_ui,
        start_background_export=True,
    )
    st.session_state.column_3_status = result.ui_status.value
    st.session_state.last_divergence_result = {
        "path": result.path,
        "ui_status": result.ui_status.value,
        "fork_id": result.fork_id,
        "background_export_started": result.background_export_started,
        "audit_filename": result.audit_filename,
        "notes": result.notes,
    }
    if result.audit_filename:
        st.session_state.last_audit_filename = result.audit_filename
    return result


def _live_session_frame() -> dict[str, Any]:
    """Deterministically assemble the current live frame for manual export."""
    base = dict(st.session_state.get("divergence_session") or {})
    status = st.session_state.get(
        "column_3_status", DivergenceUIStatus.PENDING.value
    )
    path = "PATH_A" if status == DivergenceUIStatus.COMPLIANT.value else (
        "PATH_B" if status == DivergenceUIStatus.OVERRIDE_HAZARD.value else "PENDING"
    )
    # Overlay live vault session signals so Path A / Path B both map current state.
    base.setdefault("user_input", {})
    base["user_input"] = {
        **dict(base.get("user_input") or {}),
        "manual_export": True,
        "path_selection": path,
        "credits": int(st.session_state.get("credits", 0)),
        "unlocked_nodes": sorted(
            str(n) for n in (st.session_state.get("unlocked_nodes") or set())
        ),
        "conversation": (
            (base.get("user_input") or {}).get("conversation")
            or f"Manual Column-3 export during {path}"
        ),
    }
    base.setdefault("system_context", {})
    base["system_context"] = {
        **dict(base.get("system_context") or {}),
        "tenant": TENANT_CONFIG.get("tenant_identity"),
        "sector": TENANT_CONFIG.get("active_sector_code"),
        "column_3_status": status,
        "nodes_online": len(st.session_state.get("unlocked_nodes") or set()),
    }
    base.setdefault("avatar_output", {})
    base["avatar_output"] = {
        **dict(base.get("avatar_output") or {}),
        "verbal_declaration": (
            (base.get("avatar_output") or {}).get("verbal_declaration")
            or "Sentinel & Advisory Panel — manual sovereign diagnostic requested."
        ),
        "directive": path,
    }
    base.setdefault("systemic_interpretation", {})
    base["systemic_interpretation"] = {
        **dict(base.get("systemic_interpretation") or {}),
        "path": path,
        "manual_frame": True,
        "credit_burn": int(TENANT_CONFIG["initial_credits"])
        - int(st.session_state.get("credits", 0)),
    }
    base.setdefault("ui", {})["column_3_status"] = status
    return base


def render_column_3_divergence_panel() -> None:
    """Column 3 — The Sentinel & Advisory Panel (timeline + manual export)."""
    status = st.session_state.get("column_3_status", DivergenceUIStatus.PENDING.value)
    last = st.session_state.get("last_divergence_result") or {}
    audit_file = st.session_state.get("last_audit_filename")

    if status == DivergenceUIStatus.COMPLIANT.value:
        accent = THEME["accent"]
        label = "COMPLIANT · Path A"
        detail = "Standard loop active. Awaiting manual UI request."
    elif status == DivergenceUIStatus.OVERRIDE_HAZARD.value:
        accent = "#ef4444"
        label = "OVERRIDE_HAZARD · Path B"
        detail = "Mutated reality engaged. Silent audit export dispatched."
    else:
        accent = THEME["muted"]
        label = "PENDING · No divergence"
        detail = "Sentinel idle until a Moment of Drift is resolved."

    st.markdown(
        f"""
        <div class="node-card" style="border-left-color:{accent};">
          <div class="node-meta">COLUMN 3 · THE SENTINEL &amp; ADVISORY PANEL</div>
          <div class="node-title" style="color:{accent};">{label}</div>
          <div class="node-body">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if last:
        st.caption(
            f"Last path: `{last.get('path', '—')}` · "
            f"export: {'yes' if last.get('background_export_started') else 'no'}"
        )
    if audit_file:
        st.code(audit_file, language=None)

    # Low-profile utility block — manual foreground printing / export.
    st.markdown(
        f"""
        <div class="node-card" style="border-left-color:{THEME["border"]};padding:0.85rem 1rem;">
          <div class="node-meta">UTILITY · SOVEREIGN REPORTING</div>
          <div class="node-body" style="margin:0;">
            View the live Holistic Audit Segment or export a stamped Sovereign
            Intelligence Report for save / print on demand. Independent of the
            Path B black-box vault writer.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2 = st.columns(2)
    with b1:
        view_clicked = st.button(
            "View Sovereign Diagnostic",
            key="col3_view_sovereign",
            use_container_width=True,
        )
    with b2:
        export_clicked = st.button(
            "Export Stamped Audit Record",
            key="col3_export_sovereign",
            type="primary",
            use_container_width=True,
        )

    if view_clicked:
        frame = _live_session_frame()
        segment = generate_sovereign_intelligence_segment(frame)
        report = format_sovereign_intelligence_report(segment)
        st.session_state.sovereign_diagnostic_text = report
        st.session_state.sovereign_diagnostic_hash = segment.block_hash
        st.success("Sovereign diagnostic compiled from live frame.")

    if export_clicked:
        frame = _live_session_frame()
        dossier = export_sovereign_report_sync(frame, write_vault=False)
        st.session_state.sovereign_diagnostic_text = dossier.binary_payload.decode(
            "utf-8"
        )
        st.session_state.sovereign_diagnostic_hash = dossier.hash
        st.session_state.last_manual_export_hash = dossier.hash
        st.success("Stamped audit record ready — hash sealed below.")

    sealed_hash = st.session_state.get("sovereign_diagnostic_hash")
    if sealed_hash:
        st.markdown("**Un-alterable SHA-256 seal**")
        st.code(sealed_hash, language=None)

    report_text = st.session_state.get("sovereign_diagnostic_text")
    if report_text:
        with st.expander("Sovereign Intelligence Report", expanded=bool(view_clicked)):
            st.text(report_text)
        st.download_button(
            label="Download / Print Sovereign Intelligence Report",
            data=report_text,
            file_name=f"AUDIT_{sealed_hash or 'PENDING'}.txt",
            mime="text/plain",
            key="col3_download_sir",
            use_container_width=True,
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
    if "column_3_status" not in st.session_state:
        st.session_state.column_3_status = DivergenceUIStatus.PENDING.value
    if "divergence_session" not in st.session_state:
        st.session_state.divergence_session = {}
    if "last_divergence_result" not in st.session_state:
        st.session_state.last_divergence_result = None
    if "last_audit_filename" not in st.session_state:
        st.session_state.last_audit_filename = None
    if "sovereign_diagnostic_text" not in st.session_state:
        st.session_state.sovereign_diagnostic_text = None
    if "sovereign_diagnostic_hash" not in st.session_state:
        st.session_state.sovereign_diagnostic_hash = None
    if "last_manual_export_hash" not in st.session_state:
        st.session_state.last_manual_export_hash = None


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
left, mid, right = st.columns(3)
with left:
    st.subheader("Session unlock log")
    if st.session_state.unlock_log:
        for line in reversed(st.session_state.unlock_log[-12:]):
            st.text(f"· {line}")
    else:
        st.caption("No unlocks yet. Activate a research node to begin.")

with mid:
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

with right:
    st.subheader("Sentinel & Advisory")
    render_column_3_divergence_panel()
    st.caption(
        "Path A → COMPLIANT (manual export on demand). Path B → OVERRIDE_HAZARD "
        "+ silent `secure_audit_vault/AUDIT_[SHA256].txt` black-box writer."
    )
