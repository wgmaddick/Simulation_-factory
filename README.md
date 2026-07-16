# Kinetic Vault — Polymorphic Streamlit Framework

Single-page Streamlit shell that binds one of two retained vault data profiles at a time.

## Vault profiles

| Profile | Credits | Research nodes |
| --- | ---: | --- |
| **University Operations Vault** | 450 | Shear Stress Mapping · Decel Chain Asymmetry · Micro-Tear Chronology |
| **AAT Phoenix / Asset Infrastructure** | 100 | Hamstring Load · Thermal Map · Vibration Signature |

Switching the active vault in the sidebar rebinds credits, nodes, metrics, verdicts, and sentinel data instantly. Each profile keeps its own session ledger (unlocks are not retired when you switch).

## Layout (unified)

`app.py` merges both prior surfaces into one execution loop:

1. Credit ledger + profile-bound metrics container  
2. Research-node unlock tree  
3. Media canvas · Orchestration · Advisory / Sentinel (+ roster self-heal)

All profile payloads live in `config.py` (`VAULT_PROFILES`).

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
