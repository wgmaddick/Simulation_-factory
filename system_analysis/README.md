# System Analysis API

Express engine for the **Video + Talk + Send** execution loop: research-node selection, compute-credit deduction, Twin-Track output (expert + layman), and a Passive Anomaly Sentinel mock.

## Run

```bash
cd system_analysis
npm install
npm start
```

Open [http://localhost:3000](http://localhost:3000).

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/config` | Current system state (credits + research nodes) |
| `POST` | `/api/analyze` | Body: `{ "nodeId", "userSpeech" }` — deducts credits, returns twin-track + optional sentinel |
| `POST` | `/api/reset-credits` | Restore credits from `config.json` (demo helper) |

## Config

Edit `config.json` for `initial_credits` and `research_nodes` (`id`, `label`, `credit_cost`, `description`).
