# AAT Scheme Performance Engine

Streamlit executive surface for **predictive operational risk & long-tail claims governance** (NZD).

## Surface

| Module | Purpose |
| --- | --- |
| Scheme governance sidebar | Role matrix, liability mitigation floor, performance mandate |
| Bulk ingestion gate | CSV / XLSX client profile upload with AAT sample fallback |
| Macro metrics bar | Scheme claims, pathway drift, AAT performance index, liability (GM-only, NZD) |
| Triage intake | Participant token, ICF anatomy, age, duty tier, clinical dictation NLP |
| Preventative Drift Radar | Alignment vector + large-print PPD-first Macro Financial Liability Ledger |
| Historical analytics | 120-day expected runway vs actual spend NZD (Scheme Director only) |

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
