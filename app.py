"""Opponent-Specific Selection Engine — weight and highlight metrics by target opponent."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Metric catalogue
# ---------------------------------------------------------------------------

# Lower-is-better metrics are inverted when scoring.
LOWER_IS_BETTER = frozenset({"Reload Latency (s)"})

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
    "post_contact_meters": [
        "post_contact_meters",
        "post_contact_m",
        "pcm",
        "metres_after_contact",
        "meters_after_contact",
    ],
    "scrum_axis": [
        "scrum_axis",
        "scrum_axis_score",
        "scrum_force",
        "set_piece_axis",
        "scrum_dominance",
    ],
    "kick_contest_wins_pct": [
        "kick_contest_wins_pct",
        "kick_contest_wins",
        "kick_pressure",
        "kick_contest",
        "aerial_kick_wins",
    ],
    "aerial_win_rate_pct": [
        "aerial_win_rate_pct",
        "aerial_win_rate",
        "aerial_wins",
        "contest_aerial_pct",
    ],
    "tackle_completion_pct": [
        "tackle_completion_pct",
        "tackle_completion",
        "tackle_success",
        "tackle_pct",
    ],
}

DISPLAY_COLUMNS: dict[str, str] = {
    "player_name": "Player Name",
    "sprint_speed_m_s": "Sprint Speed (m/s)",
    "reload_latency_s": "Reload Latency (s)",
    "post_contact_meters": "Post-Contact Meters",
    "scrum_axis": "Scrum Axis",
    "kick_contest_wins_pct": "Kick Contest Wins (%)",
    "aerial_win_rate_pct": "Aerial Win Rate (%)",
    "tackle_completion_pct": "Tackle Completion (%)",
}

METRIC_COLUMNS = [
    "Sprint Speed (m/s)",
    "Reload Latency (s)",
    "Post-Contact Meters",
    "Scrum Axis",
    "Kick Contest Wins (%)",
    "Aerial Win Rate (%)",
    "Tackle Completion (%)",
]

# ---------------------------------------------------------------------------
# Opponent profiles — weights sum to 1.0; highlight drives table styling
# ---------------------------------------------------------------------------

OPPONENT_PROFILES: dict[str, dict[str, Any]] = {
    "General Baseline": {
        "label": "General Baseline",
        "tagline": "Balanced athletic standards across the squad.",
        "focus": "Even weighting of speed, reload tempo, and contact fundamentals.",
        "highlight": [
            "Sprint Speed (m/s)",
            "Reload Latency (s)",
        ],
        "weights": {
            "Sprint Speed (m/s)": 0.22,
            "Reload Latency (s)": 0.22,
            "Post-Contact Meters": 0.14,
            "Scrum Axis": 0.14,
            "Kick Contest Wins (%)": 0.10,
            "Aerial Win Rate (%)": 0.10,
            "Tackle Completion (%)": 0.08,
        },
    },
    "France (Tactical/Kick Pressure)": {
        "label": "France (Tactical/Kick Pressure)",
        "tagline": "Contest the air, win the kick exchange, reload into shape fast.",
        "focus": "Kick contests, aerial wins, and reload latency under tactical pressure.",
        "highlight": [
            "Kick Contest Wins (%)",
            "Aerial Win Rate (%)",
            "Reload Latency (s)",
        ],
        "weights": {
            "Kick Contest Wins (%)": 0.28,
            "Aerial Win Rate (%)": 0.24,
            "Reload Latency (s)": 0.18,
            "Sprint Speed (m/s)": 0.12,
            "Tackle Completion (%)": 0.10,
            "Post-Contact Meters": 0.05,
            "Scrum Axis": 0.03,
        },
    },
    "South Africa (Physical/Set-Piece Collision)": {
        "label": "South Africa (Physical/Set-Piece Collision)",
        "tagline": "Win the collision zone and hold the scrum axis.",
        "focus": "Post-contact meters and scrum axis dominate selection weighting.",
        "highlight": [
            "Post-Contact Meters",
            "Scrum Axis",
            "Tackle Completion (%)",
        ],
        "weights": {
            "Post-Contact Meters": 0.32,
            "Scrum Axis": 0.28,
            "Tackle Completion (%)": 0.14,
            "Sprint Speed (m/s)": 0.10,
            "Reload Latency (s)": 0.08,
            "Aerial Win Rate (%)": 0.05,
            "Kick Contest Wins (%)": 0.03,
        },
    },
}

HIGHLIGHT_BG = "#fff3bf"
HIGHLIGHT_HEADER_BG = "#f59f00"


def _demo_squad() -> pd.DataFrame:
    """Built-in squad so the selection engine is usable without a CSV."""
    rows = [
        ("J. Williams", 9.4, 2.0, 4.2, 72, 58, 61, 88),
        ("T. Okonkwo", 8.7, 2.4, 6.8, 91, 41, 44, 92),
        ("M. Dupont", 9.1, 1.9, 3.1, 55, 78, 82, 85),
        ("S. Botha", 8.5, 2.5, 7.4, 94, 38, 40, 90),
        ("A. Chen", 9.6, 1.8, 3.8, 60, 71, 75, 87),
        ("R. Ndlovu", 8.9, 2.2, 6.1, 88, 45, 48, 93),
        ("L. Moreau", 9.0, 1.7, 2.9, 52, 84, 88, 84),
        ("K. Singh", 9.3, 2.1, 5.0, 70, 62, 66, 89),
        ("P. van der Berg", 8.6, 2.6, 7.1, 96, 35, 37, 91),
        ("C. O'Sullivan", 9.2, 2.0, 4.5, 68, 66, 70, 86),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "Player Name",
            "Sprint Speed (m/s)",
            "Reload Latency (s)",
            "Post-Contact Meters",
            "Scrum Axis",
            "Kick Contest Wins (%)",
            "Aerial Win Rate (%)",
            "Tackle Completion (%)",
        ],
    )


def _normalize_columns(raw: pd.DataFrame) -> pd.DataFrame:
    lowered = {col: col.strip().lower().replace(" ", "_") for col in raw.columns}
    raw = raw.rename(columns=lowered)

    resolved: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in raw.columns:
                resolved[canonical] = alias
                break

    if "player_name" not in resolved:
        raise ValueError(
            "CSV is missing a player name column. "
            f"Found columns: {', '.join(raw.columns)}"
        )

    metric_keys = [k for k in COLUMN_ALIASES if k != "player_name"]
    missing_metrics = [k for k in metric_keys if k not in resolved]
    if len(missing_metrics) == len(metric_keys):
        raise ValueError(
            "CSV must include at least one performance metric. "
            f"Found columns: {', '.join(raw.columns)}"
        )

    data: dict[str, Any] = {
        "Player Name": raw[resolved["player_name"]].astype(str).str.strip(),
    }
    for key in metric_keys:
        label = DISPLAY_COLUMNS[key]
        if key in resolved:
            data[label] = pd.to_numeric(raw[resolved[key]], errors="coerce")
        else:
            data[label] = np.nan

    frame = pd.DataFrame(data)
    present = [c for c in METRIC_COLUMNS if frame[c].notna().any()]
    if frame[present].isna().any().any():
        raise ValueError(
            "Present metric columns must be numeric for every player."
        )
    return frame


def _normalize_series(series: pd.Series, *, invert: bool) -> pd.Series:
    """Min-max normalize a metric to 0–1; invert when lower values are better."""
    values = series.astype(float)
    if values.isna().all():
        return pd.Series(0.0, index=series.index)
    lo, hi = float(values.min()), float(values.max())
    if hi == lo:
        scaled = pd.Series(0.5, index=series.index)
    else:
        scaled = (values - lo) / (hi - lo)
    return 1.0 - scaled if invert else scaled


def _selection_scores(report: pd.DataFrame, profile: dict[str, Any]) -> pd.Series:
    """Weighted opponent-fit score (0–100) from the active profile."""
    weights: dict[str, float] = profile["weights"]
    score = pd.Series(0.0, index=report.index)
    weight_used = 0.0

    for metric, weight in weights.items():
        if metric not in report.columns or report[metric].isna().all():
            continue
        normalized = _normalize_series(
            report[metric],
            invert=metric in LOWER_IS_BETTER,
        )
        score = score + normalized * weight
        weight_used += weight

    if weight_used <= 0:
        return pd.Series(0.0, index=report.index)
    return (score / weight_used * 100).round(1)


def _load_match_report(uploaded_file) -> pd.DataFrame:
    raw = pd.read_csv(uploaded_file)
    return _normalize_columns(raw)


def _style_opponent_table(
    display: pd.DataFrame,
    highlight_cols: list[str],
) -> "pd.io.formats.style.Styler":
    """Highlight opponent-critical metric columns in the player table."""

    def _highlight_columns(col: pd.Series) -> list[str]:
        if col.name in highlight_cols:
            return [f"background-color: {HIGHLIGHT_BG}; font-weight: 600"] * len(col)
        return [""] * len(col)

    styler = display.style.apply(_highlight_columns, axis=0)
    styler = styler.set_table_styles(
        [
            {
                "selector": f"th.col_heading.level0.col{display.columns.get_loc(col)}",
                "props": [
                    ("background-color", HIGHLIGHT_HEADER_BG),
                    ("color", "#1a1a1a"),
                    ("font-weight", "700"),
                ],
            }
            for col in highlight_cols
            if col in display.columns
        ],
        overwrite=False,
    )
    return styler


def _format_display(report: pd.DataFrame) -> pd.DataFrame:
    display = report.copy()
    formats = {
        "Sprint Speed (m/s)": "{:.2f}",
        "Reload Latency (s)": "{:.2f}",
        "Post-Contact Meters": "{:.1f}",
        "Scrum Axis": "{:.0f}",
        "Kick Contest Wins (%)": "{:.0f}",
        "Aerial Win Rate (%)": "{:.0f}",
        "Tackle Completion (%)": "{:.0f}",
        "Opponent Fit Score": "{:.1f}",
    }
    for col, fmt in formats.items():
        if col in display.columns:
            display[col] = display[col].map(
                lambda value, f=fmt: f.format(value) if pd.notna(value) else "—"
            )
    return display


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Opponent-Specific Selection Engine",
    page_icon="🏉",
    layout="wide",
)

with st.sidebar:
    st.header("Selection Controls")
    target_opponent = st.selectbox(
        "Target Opponent",
        options=list(OPPONENT_PROFILES.keys()),
        index=0,
        help="Reweights and highlights the metrics that matter most for this opponent.",
    )
    profile = OPPONENT_PROFILES[target_opponent]
    st.caption(profile["tagline"])
    st.markdown(f"**Focus:** {profile['focus']}")

    st.divider()
    st.markdown("**Metric weights for this opponent**")
    weight_rows = sorted(
        profile["weights"].items(),
        key=lambda item: item[1],
        reverse=True,
    )
    for metric, weight in weight_rows:
        marker = "◆" if metric in profile["highlight"] else "◇"
        st.text(f"{marker} {metric}: {weight:.0%}")

st.title("Opponent-Specific Selection Engine")
st.caption(
    "Shift from a flat pass/fail standard to opponent-weighted selection. "
    "Critical metrics for the chosen opponent are highlighted and drive the fit score."
)

uploaded_csv = st.file_uploader(
    "Upload Raw Match Report CSV (optional — demo squad loads by default)",
    type=["csv"],
)

if uploaded_csv is None:
    report = _demo_squad()
    st.info("Using built-in demo squad. Upload a CSV to replace it.")
else:
    try:
        report = _load_match_report(uploaded_csv)
    except (ValueError, pd.errors.ParserError) as exc:
        st.error(str(exc))
        st.stop()

report = report.copy()
report["Opponent Fit Score"] = _selection_scores(report, profile)
report = report.sort_values("Opponent Fit Score", ascending=False).reset_index(drop=True)

highlight_cols = [c for c in profile["highlight"] if c in report.columns]

top_fit = report.iloc[0]
summary_col1, summary_col2, summary_col3 = st.columns(3)
summary_col1.metric("Players Assessed", len(report))
summary_col2.metric("Target Opponent", target_opponent.split(" (")[0])
summary_col3.metric(
    "Top Fit",
    f"{top_fit['Player Name']} ({top_fit['Opponent Fit Score']:.1f})",
)

st.subheader("Player Selection Table")
st.caption(
    "Highlighted columns are weighted most heavily for "
    f"**{target_opponent}**: {', '.join(highlight_cols)}."
)

display = _format_display(report)
# Put fit score after name for readability
ordered = ["Player Name", "Opponent Fit Score"] + [
    c for c in METRIC_COLUMNS if c in display.columns
]
display = display[ordered]

st.dataframe(
    _style_opponent_table(display, highlight_cols + ["Opponent Fit Score"]),
    width="stretch",
    hide_index=True,
)

with st.expander("Expected CSV columns"):
    st.markdown(
        "Provide `player_name` plus any of: "
        "`sprint_speed_m_s`, `reload_latency_s`, `post_contact_meters`, "
        "`scrum_axis`, `kick_contest_wins_pct`, `aerial_win_rate_pct`, "
        "`tackle_completion_pct` (aliases accepted)."
    )
