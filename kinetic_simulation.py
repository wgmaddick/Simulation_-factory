"""Kinetic lab simulation — athlete force / asymmetry / tissue-debt ticks."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum


class AthleteState(str, Enum):
    IDLE = "idle"
    LOADING = "loading"
    CUTTING = "cutting"
    RECOVERING = "recovering"
    FLAGGED = "flagged"


@dataclass
class AthleteChannel:
    name: str
    state: AthleteState = AthleteState.IDLE
    shear_peak_n: float = 0.0
    asymmetry_pct: float = 0.0
    tissue_debt: float = 0.0
    samples: int = 0


@dataclass
class KineticLabState:
    tick: int = 0
    running: bool = False
    speed: float = 1.0
    athletes: list[AthleteChannel] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    shear_alerts: int = 0
    asymmetry_alerts: int = 0
    recovery_clears: int = 0
    uptime_ticks: int = 0
    unlocked_nodes: set[str] = field(default_factory=set)

    def reset(self, athlete_count: int = 5) -> None:
        roster = [
            "J. Williams",
            "T. Okonkwo",
            "M. Dupont",
            "S. Botha",
            "A. Chen",
            "R. Ndlovu",
            "L. Moreau",
            "K. Singh",
        ]
        self.tick = 0
        self.running = False
        self.shear_alerts = 0
        self.asymmetry_alerts = 0
        self.recovery_clears = 0
        self.uptime_ticks = 0
        self.log = ["[INIT] Kinetic lab reset. Awaiting acquisition start."]
        self.athletes = [
            AthleteChannel(name=roster[i % len(roster)])
            for i in range(athlete_count)
        ]


def _append_log(state: KineticLabState, message: str, max_lines: int = 80) -> None:
    state.log.append(message)
    if len(state.log) > max_lines:
        state.log = state.log[-max_lines:]


def step_simulation(state: KineticLabState) -> None:
    """Advance kinetic acquisition by one tick using unlocked research nodes."""
    if not state.running:
        return

    state.tick += 1
    state.uptime_ticks += 1
    has_shear = "node_1_1" in state.unlocked_nodes
    has_asym = "node_1_2" in state.unlocked_nodes
    has_tissue = "node_1_3" in state.unlocked_nodes

    if not (has_shear or has_asym or has_tissue):
        _append_log(
            state,
            f"[TICK {state.tick:04d}] No research nodes unlocked — sensors idle.",
        )
        return

    for athlete in state.athletes:
        roll = random.random()

        if athlete.state == AthleteState.RECOVERING:
            athlete.tissue_debt = max(0.0, athlete.tissue_debt - random.uniform(0.4, 1.2))
            if athlete.tissue_debt < 2.0:
                athlete.state = AthleteState.IDLE
                state.recovery_clears += 1
                _append_log(
                    state,
                    f"[TICK {state.tick:04d}] {athlete.name} cleared recovery window",
                )
            continue

        if athlete.state == AthleteState.FLAGGED and roll < 0.35:
            athlete.state = AthleteState.RECOVERING
            _append_log(
                state,
                f"[TICK {state.tick:04d}] {athlete.name} entered supervised recovery",
            )
            continue

        # Movement bout
        if roll < 0.55 or athlete.state in (AthleteState.LOADING, AthleteState.CUTTING):
            athlete.samples += 1
            athlete.state = AthleteState.CUTTING if roll < 0.25 else AthleteState.LOADING

            if has_shear:
                athlete.shear_peak_n = round(random.uniform(180, 520), 1)
                if athlete.shear_peak_n > 430:
                    state.shear_alerts += 1
                    athlete.state = AthleteState.FLAGGED
                    _append_log(
                        state,
                        f"[TICK {state.tick:04d}] SHEAR FLAG {athlete.name} "
                        f"peak={athlete.shear_peak_n}N",
                    )

            if has_asym:
                athlete.asymmetry_pct = round(random.uniform(2.0, 18.0), 1)
                if athlete.asymmetry_pct > 12.0:
                    state.asymmetry_alerts += 1
                    _append_log(
                        state,
                        f"[TICK {state.tick:04d}] ASYM FLAG {athlete.name} "
                        f"decel Δ={athlete.asymmetry_pct}%",
                    )

            if has_tissue:
                athlete.tissue_debt = round(
                    athlete.tissue_debt + random.uniform(0.3, 1.8),
                    2,
                )
                if athlete.tissue_debt > 14.0:
                    athlete.state = AthleteState.FLAGGED
                    _append_log(
                        state,
                        f"[TICK {state.tick:04d}] TISSUE DEBT {athlete.name} "
                        f"score={athlete.tissue_debt}",
                    )
        else:
            athlete.state = AthleteState.IDLE
            if has_tissue and athlete.tissue_debt > 0:
                athlete.tissue_debt = max(
                    0.0,
                    round(athlete.tissue_debt - random.uniform(0.1, 0.5), 2),
                )


def readiness(state: KineticLabState) -> float:
    """Percent of athletes not flagged or recovering."""
    if not state.athletes:
        return 0.0
    ready = sum(
        1
        for a in state.athletes
        if a.state not in (AthleteState.FLAGGED, AthleteState.RECOVERING)
    )
    return round(ready / len(state.athletes) * 100, 1)


def mean_shear(state: KineticLabState) -> float:
    values = [a.shear_peak_n for a in state.athletes if a.shear_peak_n > 0]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)


def mean_asymmetry(state: KineticLabState) -> float:
    values = [a.asymmetry_pct for a in state.athletes if a.samples > 0]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)
