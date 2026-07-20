# Simulation Factory

A Streamlit multipage app. `app.py` is the "Match Report Audit" page (upload a rugby telemetry CSV and review player standards). `pages/1_Factory_Floor.py` is a live factory-floor tick simulation console backed by `simulation.py`.

Alerts answer **when** / **where** / **why**:
- Match Report Audit: optional CSV columns `observed_at`, `team`, `position`, `venue`; derived why codes `sprint_below_standard`, `reload_above_standard`, `sprint_below+reload_above`.
- Factory Floor: station location is `line / bay / name`; alert why codes include `downstream_blocked`, `planned_maintenance`, `tooling_failure`, `sensor_fault`, `quality_defect`, `misassembly`, `material_fault`.

A sibling app with the same architecture lives in `datacenter_ops/` (Server Health Audit + Cluster Console).

## Cursor Cloud specific instructions

- Python deps are installed into a virtualenv at `.venv` (created during setup because `python3 -m venv` requires the `python3.12-venv` system package). Use `.venv/bin/python` / `.venv/bin/streamlit`, or activate with `source .venv/bin/activate`.
- Run the app in dev mode: `.venv/bin/streamlit run app.py --server.port 8501 --server.headless true --server.address 0.0.0.0`. The Factory Floor page is reached via the left sidebar page navigation, not a separate command.
- There is no lint config or test suite in this repo. "Testing" is manual: upload a CSV (required `player_name`, `sprint_speed_m_s`, `reload_latency_s`; optional when/where columns above) on the main page, and use Start/Pause/Reset in the Factory Floor sidebar — confirm the Retraining Alerts / Alerts tables show When / Where / Why.
- The Factory Floor page auto-reruns while running via `time.sleep(sim.speed)` + `st.rerun()`; this is expected and drives the live metrics.
