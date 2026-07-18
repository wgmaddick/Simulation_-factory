# AAT Scheme Performance Engine

Streamlit executive surface for **predictive operational risk & long-tail claims governance** (NZD).

## Views

| View | Purpose |
| --- | --- |
| **Global Scheme Portfolio** | Macro metrics, master claims accountability ledger, aggregate CapEx velocity chart |
| **Log New Claimant Profile** | Unlocked triage intake (age 25 / Sedentary defaults) with live PPD, TASE, and trajectory recalculation |
| **Individual claim drill-down** | Select a `Claim_ID` to hydrate locked clinical fields, Preventative Drift Radar, and individual time-cost axis |

## Master ledger (sample)

`AAT-Claimant-Delta-2026`, `Epsilon`, `Zeta`, `Eta` — cached via `@st.cache_data`.

## Role privacy

| Role | Scheme liability | Ledger (PPD / TASE / Lookback) | Charts |
| --- | --- | --- | --- |
| Scheme Director (GM) | Visible | Large-print PPD + NZD | Visible |
| Claims Officer / Analyst | Restricted | Masked / Restricted / Access Denied | Masked |
| Reviewing Specialist | Restricted | Masked / Restricted / Access Denied | Masked |

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
