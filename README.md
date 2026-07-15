# Simulation_-factory

Multipage Streamlit simulation tooling plus the **Kinetic Asset Management Vault**.

## Kinetic Vault (Flask)

```bash
cd kinetic_vault
../.venv/bin/python app.py
```

Serves the three-column vault UI at http://127.0.0.1:5050 (`/api/config`, `/api/analyze`).

## Streamlit apps (legacy)

```bash
.venv/bin/streamlit run app.py
```

Opponent-specific selection engine (`app.py`) and factory floor console (`pages/1_Factory_Floor.py`).
