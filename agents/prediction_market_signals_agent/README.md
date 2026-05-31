# Prediction Market Signals Agent

Signal intelligence for capital markets from Kalshi and Polymarket. Deterministic scoring first, optional LLM analysis via shared `fin_agents_common`.

## Quick start

```bash
./scripts/install.sh
source .venv/bin/activate
python scripts/run_prediction_market_signals.py --offline-demo
```

## Live run

```bash
docker compose --profile core --profile litellm_proxy --profile observability --profile langfuse up -d
python scripts/run_prediction_market_signals.py --venues kalshi polymarket --write-intermediate
```

Output: `data/reports/pred_market_sights.md`
