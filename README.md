# NZ AAT Sovereign Orchestration Engine

Portrait-ready Streamlit command surface for **NZ ACC predictive operational risk & long-tail claims governance** (NZD), with Kinetic Lab continual-learning feedback.

## Live demo

- **Streamlit Cloud:** https://xeduyt2kf49xgek76.streamlit.app  
- **Executive access key (default):** `NZ-ACC-2026`  
- On iPhone/iPad: open the link in Safari → Share → **Add to Home Screen**

A GitHub Actions keep-alive workflow pings the Streamlit URL every 10 minutes so Community Cloud stays warm for demos.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Optional Node conversational vault UI:

```bash
npm install
npm start
```

## Surfaces

| Surface | Purpose |
| --- | --- |
| **Executive Security Gate** | Passcode lock before command surface unlocks |
| **Executive Command (home)** | Scheme metrics, Structural Mirror Layers 1–3, Interface A/B |
| **Kinetic Lab** (`pages/1_Kinetic_Lab.py`) | Live acquisition console; recalibrates Auto-Learned Sensitivity |
| **AI Assistant** (`pages/02_AI_Assistant.py`) | Audio briefing + NotebookLM / Layer 2–3 synthesis |
| **Global Scheme Portfolio** | Scheme metrics, slim ledger, CapEx velocity |
| **Log New Claimant Profile** | Triage intake → live Comprehensive Scheme Ledger Dossier |
| **Individual claim drill-down** | Dossier (PPD/TASE/reserve) + alignment vector + time-cost axis + Adaptive Drift θ |
| **Department #4** | Finance / Actuarial / Legal isolated channel (role-gated) |
| **Gemini Notebook Manifest** | Embedded intelligence notebook link |

Use the **SURFACES** strip or sidebar **APP SURFACES** links to move between pages.
**COMMAND LEVELS** on Executive Command jumps Layer 1/2/3 and Interface A/B.
Host Streamlit page chrome stays hidden (`showSidebarNavigation = false`) for iPad Board mode.

## Adaptive Drift Learner

Kinetic Lab feeds live Kinetic Load into `AdaptiveDriftLearner`, which recalibrates sensitivity θ(t). Claim dossiers consume the live drift threshold (`base 15% × θ`) instead of a hard-coded band.
