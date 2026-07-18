# AAT Scheme Performance Engine

Streamlit executive surface for **predictive operational risk & long-tail claims governance** (NZD).

Clinical triage intake is the **single engine driver** — age and occupational tier auto-calibrate drift, spend velocity, PPD, and liability without manual telemetry sliders.

## Surface

| Module | Purpose |
| --- | --- |
| Scheme governance sidebar | Role matrix, liability mitigation floor, performance mandate |
| Triage intake (engine driver) | Participant token, ICF anatomy, age, duty tier, clinical dictation |
| Active Profile Status Summary | Claim profile, drift classification, pathway index, projected NZD liability |
| Preventative Drift Radar | Alignment vector + large-print PPD-first Macro Financial Liability Ledger |
| Historical analytics | Dynamic calibrated runway vs actual spend (Scheme Director only) |

## Role privacy

| Role | Liability metric | Ledger (PPD / TASE / Lookback) | Cost chart |
| --- | --- | --- | --- |
| Scheme Director (GM) | Visible (NZD) | Large-print PPD + NZD dollars | Visible |
| Claims Officer / Analyst | Restricted | Masked / Restricted / Access Denied | Masked |
| Reviewing Specialist | Restricted | Masked / Restricted / Access Denied | Masked |

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
