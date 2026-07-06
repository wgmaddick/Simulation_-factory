"""Rugby match report audit — upload raw CSV telemetry and review player standards."""

from __future__ import annotations

import pandas as pd
import streamlit as st

RELOAD_LATENCY_STANDARD_S = 2.2
SPRINT_SPEED_STANDARD_M_S = 9.0

COLUMN_ALIASES: dict[str, list[str]] = {
    "player_name": [
        "player_name",
        "name",
        "player",
        "athlete",
        "athlete_name",
    ],
    "sprint_speed_m_s": [
        "sprint_speed_m_s",
        "sprint_speed",
        "sprint_speed_ms",
        "max_sprint_speed",
        "sprint_speed_mps",
    ],
    "reload_latency_s": [
        "reload_latency_s",
        "reload_latency",
        "reload_latency_seconds",
        "reload_speed",
        "floor_to_feet_reload",
        "floor_to_feet_reload_s",
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
            "Player Name": raw[resolved["player_name"]].astype(str).str.strip(),
            "Sprint Speed (m/s)": pd.to_numeric(
                raw[resolved["sprint_speed_m_s"]], errors="coerce"
            ),
            "Reload Latency (s)": pd.to_numeric(
                raw[resolved["reload_latency_s"]], errors="coerce"
            ),
        }
    )

    if frame[["Sprint Speed (m/s)", "Reload Latency (s)"]].isna().any().any():
        raise ValueError(
            "Sprint speed and reload latency must be numeric values for every player."
        )

    return frame


def _assess_standard(row: pd.Series) -> str:
    sprint_ok = row["Sprint Speed (m/s)"] >= SPRINT_SPEED_STANDARD_M_S
    reload_ok = row["Reload Latency (s)"] <= RELOAD_LATENCY_STANDARD_S
    if sprint_ok and reload_ok:
        return "Passed Standard"
    return "Requires Retraining"


def _load_match_report(uploaded_file) -> pd.DataFrame:
    raw = pd.read_csv(uploaded_file)
    report = _normalize_columns(raw)
    report["Standard Assessment"] = report.apply(_assess_standard, axis=1)
    return report


st.set_page_config(
    page_title="Match Report Audit",
    page_icon="📋",
    layout="wide",
)

st.title("Match Report Audit")
st.caption(
    f"Standards: sprint speed ≥ {SPRINT_SPEED_STANDARD_M_S} m/s, "
    f"reload latency ≤ {RELOAD_LATENCY_STANDARD_S} s"
)

uploaded_csv = st.file_uploader(
    "Upload Raw Match Report CSV",
    type=["csv"],
)

if uploaded_csv is None:
    st.info("Upload a match report CSV to generate the player standards table.")
    st.markdown(
        "**Expected columns** (any of the listed aliases): "
        "`player_name`, `sprint_speed_m_s`, `reload_latency_s`"
    )
else:
    try:
        report = _load_match_report(uploaded_csv)
    except (ValueError, pd.errors.ParserError) as exc:
        st.error(str(exc))
    else:
        passed = int((report["Standard Assessment"] == "Passed Standard").sum())
        total = len(report)

        summary_col1, summary_col2 = st.columns(2)
        summary_col1.metric("Players Assessed", total)
        summary_col2.metric("Passed Standard", f"{passed} / {total}")

        display = report.copy()
        display["Sprint Speed (m/s)"] = display["Sprint Speed (m/s)"].map(
            lambda value: f"{value:.2f}"
        )
        display["Reload Latency (s)"] = display["Reload Latency (s)"].map(
            lambda value: f"{value:.2f}"
        )

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
        )

        retraining_required = report[
            report["Standard Assessment"] == "Requires Retraining"
        ]
        if not retraining_required.empty:
            st.warning(
                f"{len(retraining_required)} player(s) require retraining based on "
                "the configured sprint and reload standards."
            )
