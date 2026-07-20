"""Cluster request-processing simulation engine for the console display.

Events carry when (tick + clock time), where (region / AZ / rack / node), and why
(cause codes such as queue_overflow, node_down, dependency_timeout).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class NodeState(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    THROTTLED = "throttled"
    DOWN = "down"


DOWN_CAUSES = ("disk_failure", "oom_kill", "network_partition")
ERROR_CAUSES = ("dependency_timeout", "bad_deploy", "connection_reset")


@dataclass
class Node:
    name: str
    region: str = "us-west-2"
    az: str = "us-west-2a"
    rack: str = "R01"
    state: NodeState = NodeState.IDLE
    queue: int = 0
    served: int = 0
    errors: int = 0
    capacity: int = 6
    last_cause: str = "—"

    @property
    def where(self) -> str:
        return f"{self.region} / {self.az} / {self.rack} / {self.name}"


@dataclass
class Alert:
    """Structured when / where / why alert emitted by the simulation."""

    when: str
    tick: int
    where: str
    why: str
    detail: str


@dataclass
class ClusterState:
    tick: int = 0
    running: bool = False
    speed: float = 1.0
    nodes: list[Node] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)
    total_served: int = 0
    total_errors: int = 0
    uptime_ticks: int = 0
    started_at: datetime | None = None

    def reset(self, node_count: int = 5) -> None:
        self.tick = 0
        self.running = False
        self.total_served = 0
        self.total_errors = 0
        self.uptime_ticks = 0
        self.started_at = None
        self.log = ["[INIT] Cluster simulation reset. Awaiting start command."]
        self.alerts = []

        regions = [
            ("us-west-2", "us-west-2a"),
            ("us-west-2", "us-west-2b"),
            ("us-east-1", "us-east-1a"),
            ("eu-west-1", "eu-west-1a"),
        ]
        self.nodes = []
        for i in range(node_count):
            region, az = regions[i % len(regions)]
            self.nodes.append(
                Node(
                    name=f"node-{i + 1:02d}",
                    region=region,
                    az=az,
                    rack=f"R{(i % 4) + 1:02d}",
                    capacity=random.randint(4, 8),
                )
            )


def _clock(state: ClusterState) -> str:
    """Wall-clock style timestamp derived from simulation start + tick speed."""
    if state.started_at is None:
        state.started_at = datetime.now(timezone.utc)
    elapsed = state.tick * state.speed
    stamp = state.started_at.timestamp() + elapsed
    return datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _append_log(state: ClusterState, message: str, max_lines: int = 80) -> None:
    state.log.append(message)
    if len(state.log) > max_lines:
        state.log = state.log[-max_lines:]


def _emit_alert(
    state: ClusterState,
    node: Node,
    why: str,
    detail: str,
    max_alerts: int = 100,
) -> None:
    when = _clock(state)
    alert = Alert(
        when=when,
        tick=state.tick,
        where=node.where,
        why=why,
        detail=detail,
    )
    state.alerts.append(alert)
    if len(state.alerts) > max_alerts:
        state.alerts = state.alerts[-max_alerts:]
    _append_log(
        state,
        f"[TICK {state.tick:04d} | {when}] WHERE={node.where} WHY={why} — {detail}",
    )


def _least_loaded_node(state: ClusterState) -> Node | None:
    """Load balancer: pick the healthy node with the smallest queue."""
    available = [n for n in state.nodes if n.state != NodeState.DOWN]
    if not available:
        return None
    return min(available, key=lambda n: n.queue)


def step_simulation(state: ClusterState) -> None:
    """Advance the cluster simulation by one tick."""
    if not state.running:
        return

    if state.started_at is None:
        state.started_at = datetime.now(timezone.utc)

    state.tick += 1
    state.uptime_ticks += 1

    # Incoming traffic: route a burst of requests to the least-loaded node.
    incoming = random.randint(0, 4)
    if incoming:
        target = _least_loaded_node(state)
        if target is not None:
            target.queue += incoming
            _append_log(
                state,
                f"[TICK {state.tick:04d} | {_clock(state)}] "
                f"Load balancer routed {incoming} request(s) to {target.where}",
            )

    for node in state.nodes:
        roll = random.random()

        # Occasional node outage with an explicit cause.
        if roll < 0.015 and node.state != NodeState.DOWN:
            cause = random.choice(DOWN_CAUSES)
            node.state = NodeState.DOWN
            node.last_cause = cause
            _emit_alert(state, node, why=cause, detail=f"{node.name} went DOWN")
            continue

        if node.state == NodeState.DOWN:
            if roll < 0.4:
                node.state = NodeState.IDLE
                node.last_cause = "—"
                _append_log(
                    state,
                    f"[TICK {state.tick:04d} | {_clock(state)}] "
                    f"WHERE={node.where} — recovered",
                )
            continue

        if node.queue <= 0:
            node.state = NodeState.IDLE
            continue

        # Throttle when the queue exceeds capacity — why = queue_overflow.
        if node.queue > node.capacity:
            node.state = NodeState.THROTTLED
            node.last_cause = "queue_overflow"
            _emit_alert(
                state,
                node,
                why="queue_overflow",
                detail=f"throttled (queue {node.queue}/{node.capacity})",
            )

        node.state = NodeState.PROCESSING if node.state != NodeState.THROTTLED else node.state

        # Serve up to `capacity` requests this tick.
        to_serve = min(node.queue, node.capacity)
        for _ in range(to_serve):
            node.queue -= 1
            if random.random() < 0.05:
                cause = random.choice(ERROR_CAUSES)
                node.errors += 1
                state.total_errors += 1
                node.last_cause = cause
                _emit_alert(
                    state,
                    node,
                    why=cause,
                    detail=f"{node.name} returned 5xx error",
                )
            else:
                node.served += 1
                state.total_served += 1

        node.state = NodeState.IDLE if node.queue == 0 else NodeState.PROCESSING


def utilization(state: ClusterState) -> float:
    """Percentage of nodes actively processing this tick."""
    if not state.nodes:
        return 0.0
    active = sum(1 for n in state.nodes if n.state == NodeState.PROCESSING)
    return round((active / len(state.nodes)) * 100, 1)


def throughput(state: ClusterState) -> float:
    """Requests served per minute, extrapolated from ticks."""
    if state.tick == 0:
        return 0.0
    return round(state.total_served / state.tick * 60, 2)


def error_rate(state: ClusterState) -> float:
    total = state.total_served + state.total_errors
    if total == 0:
        return 0.0
    return round(state.total_errors / total * 100, 2)
