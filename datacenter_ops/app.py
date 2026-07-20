"""Server health audit — upload raw server telemetry CSV and review SLA compliance.

Each alert answers when (observed_at), where (region / AZ / rack / server), and why
(cpu_hot, latency_spike, or both).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

CPU_UTILIZATION_STANDARD_PCT = 85.0
RESPONSE_LATENCY_STANDARD_MS = 200.0

# Required metric columns.
REQUIRED_ALIASES: dict[str, list[str]] = {
    "server_name": [
        "server_name",
        "name",
        "server",
        "host",
        "hostname",
        "node",
    ],
    "cpu_utilization_pct": [
        "cpu_utilization_pct",
        "cpu_utilization",
        "cpu_pct",
        "cpu",
        "cpu_usage",
        "cpu_usage_pct",
    ],
    "response_latency_ms": [
        "response_latency_ms",
        "response_latency",
        "latency_ms",
        "latency",
        "p95_latency_ms",
        "avg_latency_ms",
    ],
}

# Optional context columns — when / where.
OPTIONAL_ALIASES: dict[str, list[str]] = {
    "observed_at": [
        "observed_at",
        "timestamp",
        "time",
        "event_time",
        "collected_at",
    ],
    "region": ["region", "cloud_region", "geo"],
    "availability_zone": [
        "availability_zone",
        "az",
        "zone",
        "availability_zone_id",
    ],
    "rack": ["rack", "rack_id", "cabinet"],
}


def _resolve_aliases(raw: pd.DataFrame, aliases: dict[str, list[str]]) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for canonical, candidates in aliases.items():
        for alias in candidates:
            if alias in raw.columns:
                resolved[canonical] = alias
                break
    return resolved


def _normalize_columns(raw: pd.DataFrame) -> pd.DataFrame:
    lowered = {col: col.strip().lower().replace(" ", "_") for col in raw.columns}
    raw = raw.rename(columns=lowered)

    required = _resolve_aliases(raw, REQUIRED_ALIASES)
    missing = [key for key in REQUIRED_ALIASES if key not in required]
    if missing:
        readable = ", ".join(missing)
        raise ValueError(
            f"CSV is missing required columns: {readable}. "
            f"Found columns: {', '.join(raw.columns)}"
        )

    optional = _resolve_aliases(raw, OPTIONAL_ALIASES)

    frame = pd.DataFrame(
        {
            "Server Name": raw[required["server_name"]].astype(str).str.strip(),
            "CPU Utilization (%)": pd.to_numeric(
                raw[required["cpu_utilization_pct"]], errors="coerce"
            ),
            "Response Latency (ms)": pd.to_numeric(
                raw[required["response_latency_ms"]], errors="coerce"
            ),
        }
    )

    if "observed_at" in optional:
        frame["When"] = pd.to_datetime(raw[optional["observed_at"]], errors="coerce")
    else:
        frame["When"] = pd.NaT

    for label, key in (
        ("Region", "region"),
        ("AZ", "availability_zone"),
        ("Rack", "rack"),
    ):
        if key in optional:
            frame[label] = raw[optional[key]].astype(str).str.strip()
        else:
            frame[label] = "—"

    if frame[["CPU Utilization (%)", "Response Latency (ms)"]].isna().any().any():
        raise ValueError(
            "CPU utilization and response latency must be numeric values for every server."
        )

    return frame


def _classify_why(row: pd.Series) -> str:
    cpu_hot = row["CPU Utilization (%)"] > CPU_UTILIZATION_STANDARD_PCT
    latency_spike = row["Response Latency (ms)"] > RESPONSE_LATENCY_STANDARD_MS
    if cpu_hot and latency_spike:
        return "cpu_hot+latency_spike"
    if cpu_hot:
        return "cpu_hot"
    if latency_spike:
        return "latency_spike"
    return "—"


def _assess_sla(row: pd.Series) -> str:
    if _classify_why(row) == "—":
        return "Healthy"
    return "Needs Attention"


def _format_where(row: pd.Series) -> str:
    parts = [
        value
        for value in (row["Region"], row["AZ"], row["Rack"], row["Server Name"])
        if value and value != "—"
    ]
    return " / ".join(parts) if parts else row["Server Name"]


def _load_health_report(uploaded_file) -> pd.DataFrame:
    raw = pd.read_csv(uploaded_file)
    report = _normalize_columns(raw)
    report["Why"] = report.apply(_classify_why, axis=1)
    report["Where"] = report.apply(_format_where, axis=1)
    report["SLA Assessment"] = report.apply(_assess_sla, axis=1)
    return report


st.set_page_config(
    page_title="Server Health Audit",
    page_icon="🖥️",
    layout="wide",
)

st.title("Server Health Audit")
st.caption(
    f"SLA standards: CPU utilization ≤ {CPU_UTILIZATION_STANDARD_PCT}%, "
    f"response latency ≤ {RESPONSE_LATENCY_STANDARD_MS} ms  ·  "
    "Alerts answer when / where / why"
)

uploaded_csv = st.file_uploader(
    "Upload Raw Server Telemetry CSV",
    type=["csv"],
)

if uploaded_csv is None:
    st.info("Upload a server telemetry CSV to generate the SLA compliance table.")
    st.markdown(
        "**Required columns** (aliases supported): "
        "`server_name`, `cpu_utilization_pct`, `response_latency_ms`"
    )
    st.markdown(
        "**Optional when/where columns**: "
        "`observed_at` (or `timestamp`), `region`, `availability_zone` (or `az`), `rack`"
    )
else:
    try:
        report = _load_health_report(uploaded_csv)
    except (ValueError, pd.errors.ParserError) as exc:
        st.error(str(exc))
    else:
        healthy = int((report["SLA Assessment"] == "Healthy").sum())
        total = len(report)

        summary_col1, summary_col2 = st.columns(2)
        summary_col1.metric("Servers Assessed", total)
        summary_col2.metric("Healthy", f"{healthy} / {total}")

        display = report[
            [
                "When",
                "Where",
                "Why",
                "Server Name",
                "Region",
                "AZ",
                "Rack",
                "CPU Utilization (%)",
                "Response Latency (ms)",
                "SLA Assessment",
            ]
        ].copy()
        display["When"] = display["When"].map(
            lambda value: value.strftime("%Y-%m-%d %H:%M:%S")
            if pd.notna(value)
            else "—"
        )
        display["CPU Utilization (%)"] = display["CPU Utilization (%)"].map(
            lambda value: f"{value:.1f}"
        )
        display["Response Latency (ms)"] = display["Response Latency (ms)"].map(
            lambda value: f"{value:.0f}"
        )

        st.subheader("Fleet Assessment")
        st.dataframe(display, use_container_width=True, hide_index=True)

        attention_required = report[report["SLA Assessment"] == "Needs Attention"].copy()
        if not attention_required.empty:
            st.warning(
                f"{len(attention_required)} server(s) need attention — "
                "each alert below includes when / where / why."
            )
            alerts = attention_required[["When", "Where", "Why"]].copy()
            alerts["When"] = alerts["When"].map(
                lambda value: value.strftime("%Y-%m-%d %H:%M:%S")
                if pd.notna(value)
                else "—"
            )
            st.subheader("Attention Alerts (When / Where / Why)")
            st.dataframe(alerts, use_container_width=True, hide_index=True)
