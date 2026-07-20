"""Rugby match report audit — upload raw CSV telemetry and review player standards.

Each retraining alert answers when (observed_at), where (team / position / venue / player),
and why (sprint_below_standard, reload_above_standard, or both).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

RELOAD_LATENCY_STANDARD_S = 2.2
SPRINT_SPEED_STANDARD_M_S = 9.0

REQUIRED_ALIASES: dict[str, list[str]] = {
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

OPTIONAL_ALIASES: dict[str, list[str]] = {
    "observed_at": [
        "observed_at",
        "timestamp",
        "time",
        "event_time",
        "match_date",
        "collected_at",
    ],
    "team": ["team", "squad", "club", "side"],
    "position": ["position", "pos", "role", "jersey_position"],
    "venue": ["venue", "ground", "stadium", "pitch", "location"],
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
            "Player Name": raw[required["player_name"]].astype(str).str.strip(),
            "Sprint Speed (m/s)": pd.to_numeric(
                raw[required["sprint_speed_m_s"]], errors="coerce"
            ),
            "Reload Latency (s)": pd.to_numeric(
                raw[required["reload_latency_s"]], errors="coerce"
            ),
        }
    )

    if "observed_at" in optional:
        frame["When"] = pd.to_datetime(raw[optional["observed_at"]], errors="coerce")
    else:
        frame["When"] = pd.NaT

    for label, key in (("Team", "team"), ("Position", "position"), ("Venue", "venue")):
        if key in optional:
            frame[label] = raw[optional[key]].astype(str).str.strip()
        else:
            frame[label] = "—"

    if frame[["Sprint Speed (m/s)", "Reload Latency (s)"]].isna().any().any():
        raise ValueError(
            "Sprint speed and reload latency must be numeric values for every player."
        )

    return frame


def _classify_why(row: pd.Series) -> str:
    sprint_below = row["Sprint Speed (m/s)"] < SPRINT_SPEED_STANDARD_M_S
    reload_above = row["Reload Latency (s)"] > RELOAD_LATENCY_STANDARD_S
    if sprint_below and reload_above:
        return "sprint_below+reload_above"
    if sprint_below:
        return "sprint_below_standard"
    if reload_above:
        return "reload_above_standard"
    return "—"


def _assess_standard(row: pd.Series) -> str:
    if _classify_why(row) == "—":
        return "Passed Standard"
    return "Requires Retraining"


def _format_where(row: pd.Series) -> str:
    parts = [
        value
        for value in (row["Team"], row["Position"], row["Venue"], row["Player Name"])
        if value and value != "—"
    ]
    return " / ".join(parts) if parts else row["Player Name"]


def _load_match_report(uploaded_file) -> pd.DataFrame:
    raw = pd.read_csv(uploaded_file)
    report = _normalize_columns(raw)
    report["Why"] = report.apply(_classify_why, axis=1)
    report["Where"] = report.apply(_format_where, axis=1)
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
    f"reload latency ≤ {RELOAD_LATENCY_STANDARD_S} s  ·  "
    "Alerts answer when / where / why"
)

uploaded_csv = st.file_uploader(
    "Upload Raw Match Report CSV",
    type=["csv"],
)

if uploaded_csv is None:
    st.info("Upload a match report CSV to generate the player standards table.")
    st.markdown(
        "**Required columns** (aliases supported): "
        "`player_name`, `sprint_speed_m_s`, `reload_latency_s`"
    )
    st.markdown(
        "**Optional when/where columns**: "
        "`observed_at` (or `timestamp` / `match_date`), `team`, `position`, `venue`"
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

        display = report[
            [
                "When",
                "Where",
                "Why",
                "Player Name",
                "Team",
                "Position",
                "Venue",
                "Sprint Speed (m/s)",
                "Reload Latency (s)",
                "Standard Assessment",
            ]
        ].copy()
        display["When"] = display["When"].map(
            lambda value: value.strftime("%Y-%m-%d %H:%M:%S")
            if pd.notna(value)
            else "—"
        )
        display["Sprint Speed (m/s)"] = display["Sprint Speed (m/s)"].map(
            lambda value: f"{value:.2f}"
        )
        display["Reload Latency (s)"] = display["Reload Latency (s)"].map(
            lambda value: f"{value:.2f}"
        )

        st.subheader("Player Assessment")
        st.dataframe(display, use_container_width=True, hide_index=True)

        retraining_required = report[
            report["Standard Assessment"] == "Requires Retraining"
        ].copy()
        if not retraining_required.empty:
            st.warning(
                f"{len(retraining_required)} player(s) require retraining — "
                "each alert below includes when / where / why."
            )
            alerts = retraining_required[["When", "Where", "Why"]].copy()
            alerts["When"] = alerts["When"].map(
                lambda value: value.strftime("%Y-%m-%d %H:%M:%S")
                if pd.notna(value)
                else "—"
            )
            st.subheader("Retraining Alerts (When / Where / Why)")
            st.dataframe(alerts, use_container_width=True, hide_index=True)
