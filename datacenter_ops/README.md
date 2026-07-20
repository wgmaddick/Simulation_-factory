# Data Center Operations Center

A Streamlit multipage app, built on the same architecture as the root `Simulation_-factory` app
(a CSV data-audit page + a live tick-simulation console).

Alerts answer **when** / **where** / **why**.

## Pages

- **Server Health Audit** (`app.py`) — upload a raw server telemetry CSV and review each server
  against SLA standards (CPU utilization ≤ 85%, response latency ≤ 200 ms).
  - Required columns (aliases supported): `server_name`, `cpu_utilization_pct`, `response_latency_ms`
  - Optional when/where columns: `observed_at` (or `timestamp`), `region`, `availability_zone` (or `az`), `rack`
  - Derived why codes: `cpu_hot`, `latency_spike`, `cpu_hot+latency_spike`
- **Cluster Console** (`pages/1_Cluster_Console.py`) — a live request-processing simulation across
  cluster nodes. A load balancer routes incoming traffic to the least-loaded node; nodes process,
  throttle, error, and occasionally go down and recover. Backed by `simulation.py`.
  - Each alert includes when (UTC clock + tick), where (region / AZ / rack / node), and why
    (`queue_overflow`, `disk_failure`, `oom_kill`, `network_partition`, `dependency_timeout`,
    `bad_deploy`, `connection_reset`).

## Run

```bash
streamlit run app.py
```

From the repo root you can reuse the shared virtualenv:

```bash
../.venv/bin/streamlit run app.py
```
