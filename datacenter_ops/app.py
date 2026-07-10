"""Server health audit — upload raw server telemetry CSV and review SLA compliance."""

from __future__ import annotations

import pandas as pd
import streamlit as st

CPU_UTILIZATION_STANDARD_PCT = 85.0
RESPONSE_LATENCY_STANDARD_MS = 200.0

COLUMN_ALIASES: dict[str, list[str]] = {
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


def _normalize_columns(raw: pd.DataFrame) -> pd.DataFrame:
    lowered = {col: col.strip().lower().replace(" ", "_") for col in raw.columns}
    raw = raw.rename(columns=lowered)

    resolved: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in raw.columns:
                resolved[canonical] = alias
                break

    missing = [key for key in COLUMN_ALIASES if key not in resolved]
    if missing:
        readable = ", ".join(missing)
        raise ValueError(
            f"CSV is missing required columns: {readable}. "
            f"Found columns: {', '.join(raw.columns)}"
        )

    frame = pd.DataFrame(
        {
            "Server Name": raw[resolved["server_name"]].astype(str).str.strip(),
            "CPU Utilization (%)": pd.to_numeric(
                raw[resolved["cpu_utilization_pct"]], errors="coerce"
            ),
            "Response Latency (ms)": pd.to_numeric(
                raw[resolved["response_latency_ms"]], errors="coerce"
            ),
        }
    )

    if frame[["CPU Utilization (%)", "Response Latency (ms)"]].isna().any().any():
        raise ValueError(
            "CPU utilization and response latency must be numeric values for every server."
        )

    return frame


def _assess_sla(row: pd.Series) -> str:
    cpu_ok = row["CPU Utilization (%)"] <= CPU_UTILIZATION_STANDARD_PCT
    latency_ok = row["Response Latency (ms)"] <= RESPONSE_LATENCY_STANDARD_MS
    if cpu_ok and latency_ok:
        return "Healthy"
    return "Needs Attention"


def _load_health_report(uploaded_file) -> pd.DataFrame:
    raw = pd.read_csv(uploaded_file)
    report = _normalize_columns(raw)
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
    f"response latency ≤ {RESPONSE_LATENCY_STANDARD_MS} ms"
)

uploaded_csv = st.file_uploader(
    "Upload Raw Server Telemetry CSV",
    type=["csv"],
)

if uploaded_csv is None:
    st.info("Upload a server telemetry CSV to generate the SLA compliance table.")
    st.markdown(
        "**Expected columns** (any of the listed aliases): "
        "`server_name`, `cpu_utilization_pct`, `response_latency_ms`"
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

        display = report.copy()
        display["CPU Utilization (%)"] = display["CPU Utilization (%)"].map(
            lambda value: f"{value:.1f}"
        )
        display["Response Latency (ms)"] = display["Response Latency (ms)"].map(
            lambda value: f"{value:.0f}"
        )

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
        )

        attention_required = report[report["SLA Assessment"] == "Needs Attention"]
        if not attention_required.empty:
            st.warning(
                f"{len(attention_required)} server(s) need attention based on "
                "the configured CPU and latency SLA standards."
            )
