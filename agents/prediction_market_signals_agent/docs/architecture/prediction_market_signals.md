# Prediction Market Signals — Architecture

## Purpose

Ingest Kalshi and Polymarket data, score capital-market-relevant signals deterministically, optionally enrich with LLM analysis and user research, and produce `data/reports/pred_market_sights.md`.

## Pipeline

```text
Topic universe → Market discovery → Normalization → Deterministic algorithms
  → Candidate signal listing → LLM analysis (optional) → User research
  → Synthesis → Final report
```

## Market Data Ingestion

The agent owns its market ingestion code under `market_data/`.

- `MarketDataClient` uses `predmarket` for Kalshi and Polymarket REST data.
- `PolymarketClobClient` enriches Polymarket markets with live CLOB midpoints.
- Connectors wrap this internal client and add venue-native order book calls.

Venue-specific details are documented in:

- [Kalshi integration](../integrations/kalshi.md)
- [Polymarket integration](../integrations/polymarket.md)

## Adding an algorithm

1. Subclass `SignalAlgorithm` in `algorithms/`.
2. Register in `deterministic_scoring_agent.build_registry()`.
3. Add weight in `config/prediction_market_signal_scoring.yaml` if combined in `signal_strength`.

## Adding a connector

1. Implement `PredictionMarketConnector` in `connectors/`.
2. Register in `discovery/market_discovery.py`.

## Pass 7 improvements (proposed)

- Promote `MarketDataClient` into `fin_agents_common` if another agent needs prediction-market ingestion.
- Unify async entry (CLI currently uses `asyncio.run` wrapper).
- Persist momentum history with scheduled snapshot jobs.
- Standardize OTel attribute names across agents.
- Add integration tests against recorded API fixtures.
