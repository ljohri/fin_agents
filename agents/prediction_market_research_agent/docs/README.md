# Prediction Market Research Agent — Documentation

## Overview

This agent ingests prediction market data from Kalshi and Polymarket, normalizes it, and supports comparative research workflows (pricing, liquidity, cross-venue topic discovery).

## Architecture

This agent uses a **middle-ground integration strategy**: [predmarket](https://github.com/ashercn97/predmarket) for unified venue access, plus a small custom layer where predmarket’s Gamma-based REST path is insufficient.

### Why predmarket

Kalshi and Polymarket expose different APIs, field names, and event/market hierarchies. Maintaining bespoke clients for every venue duplicates work across agents. `predmarket` provides:

- A shared vocabulary: **Question** (events), **Contract** (markets), **Price**
- Parallel REST clients: `KalshiRest`, `PolymarketRest` with identical method names
- Pydantic models with `raw` payloads preserved for venue-specific fields

We install `predmarket` **from GitHub at agent install time** (see `pyproject.toml`) so this agent tracks upstream fixes without waiting for PyPI releases.

### Why keep a custom CLOB layer

Polymarket’s Gamma API `outcomePrices` can lag the live order book. For research-quality implied probabilities, this agent enriches Polymarket contracts with **CLOB midpoint** prices via `PolymarketClobClient` (`clients/clob.py`).

Kalshi prices are derived from `yes_bid_dollars` / `yes_ask_dollars` in the contract `raw` payload (see `clients/adapter.py`).

### Data flow

```text
CLI / Agent
    │
    ▼
MarketDataClient (clients/markets.py)
    │
    ├── KalshiRest ──────────────► Kalshi Trade API
    │         │
    │         └── Contract ──► adapter ──► PredictionMarket
    │
    └── PolymarketRest ────────► Polymarket Gamma API
              │
              ├── Contract ──► adapter ──► PredictionMarket
              └── PolymarketClobClient ──► CLOB /midpoint (live yes price)
```

### Agent-local environment

Each agent owns an isolated virtualenv at `agents/prediction_market_research_agent/.venv`. Dependencies—including `predmarket` from GitHub—are installed when you run:

```bash
./agents/prediction_market_research_agent/scripts/install.sh
```

This keeps agent dependencies independent from the repo root `.venv` and from other agents added later.

### Package layout

```text
src/prediction_market_research_agent/
├── agent.py              # Orchestration (async internally, sync CLI surface)
├── config.py
├── clients/
│   ├── markets.py        # predmarket REST orchestration
│   ├── adapter.py        # Contract → PredictionMarket
│   └── clob.py           # Polymarket CLOB midpoints
└── models/
    └── market.py         # Agent output schema (PredictionMarket)
```

The agent’s `PredictionMarket` model is the **output contract** for downstream analysis. predmarket’s `Contract` is the **input contract** from providers.

## Downstream consumers

[`prediction_market_signals_agent`](../../prediction_market_signals_agent/) reuses `MarketDataClient` via thin connectors for signal discovery and scoring.

## API references

| Venue | Docs |
|-------|------|
| predmarket (SDK) | [github.com/ashercn97/predmarket](https://github.com/ashercn97/predmarket) |
| Kalshi | [kalshi.md](./kalshi.md) |
| Polymarket | [polymarket.md](./polymarket.md) |

## Planned capabilities

- [x] Fetch open markets from Kalshi and Polymarket via predmarket
- [x] Normalize to a shared `PredictionMarket` schema
- [x] Live Polymarket prices via CLOB midpoints
- [ ] Cross-venue market matching (similar events)
- [ ] Order book depth analysis
- [ ] Historical price / volume trends
- [ ] LLM-assisted research memos
