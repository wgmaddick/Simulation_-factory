# Data Center Operations Center

A Streamlit multipage app, built on the same architecture as the root `Simulation_-factory` app
(a CSV data-audit page + a live tick-simulation console).

## Pages

- **Server Health Audit** (`app.py`) — upload a raw server telemetry CSV and review each server
  against SLA standards (CPU utilization ≤ 85%, response latency ≤ 200 ms).
  Accepted columns (aliases supported): `server_name`, `cpu_utilization_pct`, `response_latency_ms`.
- **Cluster Console** (`pages/1_Cluster_Console.py`) — a live request-processing simulation across
  cluster nodes. A load balancer routes incoming traffic to the least-loaded node; nodes process,
  throttle, error, and occasionally go down and recover. Backed by `simulation.py`.

## Run

```bash
streamlit run app.py
```

From the repo root you can reuse the shared virtualenv:

```bash
../.venv/bin/streamlit run app.py
```
