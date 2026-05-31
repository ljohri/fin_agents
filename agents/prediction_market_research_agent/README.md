# Prediction Market Research Agent

Researches and compares prediction markets using **Kalshi** and **Polymarket**. Market discovery and metadata go through the [predmarket](https://github.com/ashercn97/predmarket) SDK; Polymarket live prices use a custom CLOB midpoint layer.

> **Disclaimer:** For research and decision-support only. Not financial or trading advice.

## Quick start

This agent uses its **own virtual environment** (not the repo root `.venv`).

```bash
# From repo root — creates .venv inside this agent directory
chmod +x agents/prediction_market_research_agent/scripts/install.sh
./agents/prediction_market_research_agent/scripts/install.sh

source agents/prediction_market_research_agent/.venv/bin/activate

# Optional: copy env template for authenticated Kalshi endpoints
cp .env.example .env

pm-research list --limit 5
```

Manual install (equivalent):

```bash
cd agents/prediction_market_research_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `KALSHI_API_BASE_URL` | No | Reserved for future authenticated Kalshi use |
| `KALSHI_API_KEY_ID` | No* | For authenticated Kalshi requests |
| `KALSHI_PRIVATE_KEY_PATH` | No* | RSA private key for request signing |
| `POLYMARKET_GAMMA_API_URL` | No | Used by predmarket (Gamma API) |
| `POLYMARKET_CLOB_API_URL` | No | Live midpoint prices (CLOB API) |

\* Public market data works without credentials.

## Documentation

- [Architecture & design](./docs/README.md)
- [Kalshi notes](./docs/kalshi.md)
- [Polymarket notes](./docs/polymarket.md)

## Dependencies

| Package | Source | Role |
|---------|--------|------|
| `predmarket` | GitHub (`ashercn97/predmarket`) | Unified Kalshi + Polymarket REST |
| `httpx` | PyPI | Async HTTP (predmarket + CLOB) |

See [docs/README.md](./docs/README.md) for the full architecture rationale.
