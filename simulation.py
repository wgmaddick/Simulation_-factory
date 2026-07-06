"""Factory simulation engine for the console display."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum


class StationState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    BLOCKED = "blocked"
    MAINTENANCE = "maintenance"


@dataclass
class Station:
    name: str
    state: StationState = StationState.IDLE
    queue: int = 0
    processed: int = 0
    defects: int = 0
    cycle_time: float = 1.0


@dataclass
class SimulationState:
    tick: int = 0
    running: bool = False
    speed: float = 1.0
    stations: list[Station] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    total_output: int = 0
    total_defects: int = 0
    uptime_ticks: int = 0

    def reset(self, station_count: int = 5) -> None:
        names = ["Intake", "Assembly", "QA", "Packaging", "Shipping"]
        self.tick = 0
        self.running = False
        self.total_output = 0
        self.total_defects = 0
        self.uptime_ticks = 0
        self.log = ["[INIT] Factory simulation reset. Awaiting start command."]
        self.stations = [
            Station(
                name=names[i % len(names)] + (f" {i // len(names) + 1}" if i >= len(names) else ""),
                cycle_time=round(random.uniform(0.8, 1.6), 2),
            )
            for i in range(station_count)
        ]


def _append_log(state: SimulationState, message: str, max_lines: int = 80) -> None:
    state.log.append(message)
    if len(state.log) > max_lines:
        state.log = state.log[-max_lines:]


def step_simulation(state: SimulationState) -> None:
    """Advance the factory simulation by one tick."""
    if not state.running:
        return

    state.tick += 1
    state.uptime_ticks += 1

    # Inject new work at the first station
    intake = state.stations[0]
    if random.random() < 0.65:
        intake.queue += 1
        _append_log(state, f"[TICK {state.tick:04d}] Intake received batch (+1)")

    for index, station in enumerate(state.stations):
        roll = random.random()

        # Occasional maintenance events
        if roll < 0.02 and station.state != StationState.MAINTENANCE:
            station.state = StationState.MAINTENANCE
            _append_log(state, f"[TICK {state.tick:04d}] {station.name} entered maintenance")
            continue

        if station.state == StationState.MAINTENANCE:
            if roll < 0.35:
                station.state = StationState.IDLE
                _append_log(state, f"[TICK {state.tick:04d}] {station.name} maintenance complete")
            continue

        if station.queue <= 0:
            station.state = StationState.IDLE
            continue

        # Downstream blocked if next station queue is full
        if index < len(state.stations) - 1:
            next_station = state.stations[index + 1]
            if next_station.queue >= 8:
                station.state = StationState.BLOCKED
                continue

        station.state = StationState.RUNNING
        station.queue -= 1

        if roll < 0.04:
            station.defects += 1
            state.total_defects += 1
            _append_log(state, f"[TICK {state.tick:04d}] {station.name} flagged defect")
            continue

        station.processed += 1

        if index < len(state.stations) - 1:
            state.stations[index + 1].queue += 1
        else:
            state.total_output += 1
            _append_log(state, f"[TICK {state.tick:04d}] Shipment completed (total: {state.total_output})")

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
