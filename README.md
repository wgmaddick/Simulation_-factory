# University Operations Vault — Kinetic Sector

Streamlit multipage app for **University Intercollegiate Athletics** operations research.

## Tenant brief

| Field | Value |
| --- | --- |
| Tenant | University Operations Vault |
| Domain | University Intercollegiate Athletics |
| Sector | `SEC_01_KINETIC` |
| Starting credits | 450 |
| Theme | slate-950 / slate-900 / emerald-500 |

## Pages

- **University Operations Vault** (`app.py`) — credit ledger and research-node unlock tree:
  - Node 1.1 Dynamic Interface Shear Stress Mapping (5 cr)
  - Node 1.2 Pelvic Tilt & Deceleration Chain Asymmetry (8 cr)
  - Node 1.3 Cellular Longevity & Micro-Tear Chronology (12 cr)
- **Kinetic Lab** (`pages/1_Kinetic_Lab.py`) — live athlete acquisition console. Channels activate only for unlocked nodes. Engine: `kinetic_simulation.py`.

Config lives in `config.py` (mirrors the sector brief).

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
