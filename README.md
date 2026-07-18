# Sovereign Case Management Engine

Streamlit executive dashboard for **operational risk governance** — portfolio metrics, hierarchical audit portals, clinical triage intake, and a Preventative Drift Radar with lookback fee basis.

## Surface

| Area | What it does |
| --- | --- |
| Governance sidebar | Role matrix, CapEx mitigation floor, strategic mandate injection |
| Portfolio bar | Assets protected, critical drift, ODG alignment, indemnity exposure |
| Audit Oracle | Operations & asset availability tranche drill-down |
| Clinical Triage Intake | Anonymized subject token, ICF anatomy, age, occupation, ambient NLP notes |
| Preventative Drift Radar | Asymmetrical `[1.6, 1.0]` layout — physical alignment table + TASE / PPD / lookback liability panel with remediate/escalate gate |

## Core math

- Age / occupation / anatomy modulate baseline cost and ODG timeline
- CapEx mitigation floor compresses allowable baseline spend
- Functional drift = `max(0, 100 − ROM%)`
- IVC = spend variance vs modulated baseline
- Projected TASE escalates with drift and IVC; PPD uses a logistic risk curve
- Lookback license fee = `$5,000 + 12% × projected TASE`

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Optional Kinetic Lab page remains under `pages/` for research-node acquisition demos.
