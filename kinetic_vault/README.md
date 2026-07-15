# Kinetic Asset Management Vault

Three-column intake console for kinetic/biomechanics media: media canvas, research-node orchestration, and advisory/sentinel output.

## Run

```bash
cd kinetic_vault
../.venv/bin/pip install -r requirements.txt
../.venv/bin/python app.py
```

Open http://127.0.0.1:5050

## API

- `GET /api/config` — domain, tenant, credits, research nodes
- `POST /api/analyze` — body `{ "nodeId": "...", "userSpeech": "..." }` → verdict, credits, optional sentinel override
- `POST /api/reset` — restore credit allocation
