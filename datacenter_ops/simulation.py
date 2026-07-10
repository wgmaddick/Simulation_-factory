"""Cluster request-processing simulation engine for the console display."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum


class NodeState(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    THROTTLED = "throttled"
    DOWN = "down"


@dataclass
class Node:
    name: str
    state: NodeState = NodeState.IDLE
    queue: int = 0
    served: int = 0
    errors: int = 0
    capacity: int = 6


@dataclass
class ClusterState:
    tick: int = 0
    running: bool = False
    speed: float = 1.0
    nodes: list[Node] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    total_served: int = 0
    total_errors: int = 0
    uptime_ticks: int = 0

    def reset(self, node_count: int = 5) -> None:
        self.tick = 0
        self.running = False
        self.total_served = 0
        self.total_errors = 0
        self.uptime_ticks = 0
        self.log = ["[INIT] Cluster simulation reset. Awaiting start command."]
        self.nodes = [
            Node(
                name=f"node-{i + 1:02d}",
                capacity=random.randint(4, 8),
            )
            for i in range(node_count)
        ]


def _append_log(state: ClusterState, message: str, max_lines: int = 80) -> None:
    state.log.append(message)
    if len(state.log) > max_lines:
        state.log = state.log[-max_lines:]


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
                f"[TICK {state.tick:04d}] Load balancer routed {incoming} request(s) to {target.name}",
            )

    for node in state.nodes:
        roll = random.random()

        # Occasional node outage.
        if roll < 0.015 and node.state != NodeState.DOWN:
            node.state = NodeState.DOWN
            _append_log(state, f"[TICK {state.tick:04d}] {node.name} went DOWN")
            continue

        if node.state == NodeState.DOWN:
            if roll < 0.4:
                node.state = NodeState.IDLE
                _append_log(state, f"[TICK {state.tick:04d}] {node.name} recovered")
            continue

        if node.queue <= 0:
            node.state = NodeState.IDLE
            continue

        # Throttle when the queue exceeds capacity.
        if node.queue > node.capacity:
            node.state = NodeState.THROTTLED
            _append_log(state, f"[TICK {state.tick:04d}] {node.name} throttled (queue {node.queue}/{node.capacity})")

        node.state = NodeState.PROCESSING if node.state != NodeState.THROTTLED else node.state

        # Serve up to `capacity` requests this tick.
        to_serve = min(node.queue, node.capacity)
        for _ in range(to_serve):
            node.queue -= 1
            if random.random() < 0.05:
                node.errors += 1
                state.total_errors += 1
                _append_log(state, f"[TICK {state.tick:04d}] {node.name} returned 5xx error")
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
