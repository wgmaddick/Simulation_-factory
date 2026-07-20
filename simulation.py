"""Factory simulation engine for the console display.

Events carry when (tick + clock time), where (line / bay / station), and why
(cause codes such as downstream_blocked, planned_maintenance, quality_defect).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class StationState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    BLOCKED = "blocked"
    MAINTENANCE = "maintenance"


MAINTENANCE_CAUSES = ("planned_maintenance", "tooling_failure", "sensor_fault")
DEFECT_CAUSES = ("quality_defect", "misassembly", "material_fault")


@dataclass
class Station:
    name: str
    line: str = "Line-A"
    bay: str = "Bay-01"
    state: StationState = StationState.IDLE
    queue: int = 0
    processed: int = 0
    defects: int = 0
    cycle_time: float = 1.0
    last_cause: str = "—"

    @property
    def where(self) -> str:
        return f"{self.line} / {self.bay} / {self.name}"


@dataclass
class Alert:
    """Structured when / where / why alert emitted by the simulation."""

    when: str
    tick: int
    where: str
    why: str
    detail: str


@dataclass
class SimulationState:
    tick: int = 0
    running: bool = False
    speed: float = 1.0
    stations: list[Station] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)
    total_output: int = 0
    total_defects: int = 0
    uptime_ticks: int = 0
    started_at: datetime | None = None

    def reset(self, station_count: int = 5) -> None:
        names = ["Intake", "Assembly", "QA", "Packaging", "Shipping"]
        lines = ["Line-A", "Line-B"]
        self.tick = 0
        self.running = False
        self.total_output = 0
        self.total_defects = 0
        self.uptime_ticks = 0
        self.started_at = None
        self.log = ["[INIT] Factory simulation reset. Awaiting start command."]
        self.alerts = []
        self.stations = [
            Station(
                name=names[i % len(names)]
                + (f" {i // len(names) + 1}" if i >= len(names) else ""),
                line=lines[i % len(lines)],
                bay=f"Bay-{(i % 5) + 1:02d}",
                cycle_time=round(random.uniform(0.8, 1.6), 2),
            )
            for i in range(station_count)
        ]


def _clock(state: SimulationState) -> str:
    """Wall-clock style timestamp derived from simulation start + tick speed."""
    if state.started_at is None:
        state.started_at = datetime.now(timezone.utc)
    elapsed = state.tick * state.speed
    stamp = state.started_at.timestamp() + elapsed
    return datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _append_log(state: SimulationState, message: str, max_lines: int = 80) -> None:
    state.log.append(message)
    if len(state.log) > max_lines:
        state.log = state.log[-max_lines:]


def _emit_alert(
    state: SimulationState,
    station: Station,
    why: str,
    detail: str,
    max_alerts: int = 100,
) -> None:
    when = _clock(state)
    alert = Alert(
        when=when,
        tick=state.tick,
        where=station.where,
        why=why,
        detail=detail,
    )
    state.alerts.append(alert)
    if len(state.alerts) > max_alerts:
        state.alerts = state.alerts[-max_alerts:]
    _append_log(
        state,
        f"[TICK {state.tick:04d} | {when}] WHERE={station.where} WHY={why} — {detail}",
    )


def step_simulation(state: SimulationState) -> None:
    """Advance the factory simulation by one tick."""
    if not state.running:
        return

    if state.started_at is None:
        state.started_at = datetime.now(timezone.utc)

    state.tick += 1
    state.uptime_ticks += 1

    # Inject new work at the first station
    intake = state.stations[0]
    if random.random() < 0.65:
        intake.queue += 1
        _append_log(
            state,
            f"[TICK {state.tick:04d} | {_clock(state)}] "
            f"WHERE={intake.where} — Intake received batch (+1)",
        )

    for index, station in enumerate(state.stations):
        roll = random.random()

        # Occasional maintenance events with an explicit cause.
        if roll < 0.02 and station.state != StationState.MAINTENANCE:
            cause = random.choice(MAINTENANCE_CAUSES)
            station.state = StationState.MAINTENANCE
            station.last_cause = cause
            _emit_alert(
                state,
                station,
                why=cause,
                detail=f"{station.name} entered maintenance",
            )
            continue

        if station.state == StationState.MAINTENANCE:
            if roll < 0.35:
                station.state = StationState.IDLE
                station.last_cause = "—"
                _append_log(
                    state,
                    f"[TICK {state.tick:04d} | {_clock(state)}] "
                    f"WHERE={station.where} — maintenance complete",
                )
            continue

        if station.queue <= 0:
            station.state = StationState.IDLE
            continue

        # Downstream blocked if next station queue is full — why = downstream_blocked.
        if index < len(state.stations) - 1:
            next_station = state.stations[index + 1]
            if next_station.queue >= 8:
                station.state = StationState.BLOCKED
                station.last_cause = "downstream_blocked"
                _emit_alert(
                    state,
                    station,
                    why="downstream_blocked",
                    detail=(
                        f"{station.name} blocked — "
                        f"{next_station.name} queue full ({next_station.queue})"
                    ),
                )
                continue

        station.state = StationState.RUNNING
        station.queue -= 1

        if roll < 0.04:
            cause = random.choice(DEFECT_CAUSES)
            station.defects += 1
            state.total_defects += 1
            station.last_cause = cause
            _emit_alert(
                state,
                station,
                why=cause,
                detail=f"{station.name} flagged defect",
            )
            continue

        station.processed += 1

        if index < len(state.stations) - 1:
            state.stations[index + 1].queue += 1
        else:
            state.total_output += 1
            _append_log(
                state,
                f"[TICK {state.tick:04d} | {_clock(state)}] "
                f"WHERE={station.where} — Shipment completed "
                f"(total: {state.total_output})",
            )

        station.state = StationState.IDLE if station.queue == 0 else StationState.RUNNING


def efficiency(state: SimulationState) -> float:
    if state.uptime_ticks == 0:
        return 0.0
    active = sum(1 for s in state.stations if s.state == StationState.RUNNING)
    return round((active / max(len(state.stations), 1)) * 100, 1)


def throughput(state: SimulationState) -> float:
    if state.tick == 0:
        return 0.0
    return round(state.total_output / state.tick * 60, 2)
