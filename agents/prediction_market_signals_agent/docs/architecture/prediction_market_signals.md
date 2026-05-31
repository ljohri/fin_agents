# Prediction Market Signals — Architecture

## Purpose

Ingest Kalshi and Polymarket data, score capital-market-relevant signals deterministically, optionally enrich with LLM analysis and user research, and produce `data/reports/pred_market_sights.md`.

## Pipeline

```text
Topic universe → Market discovery → Normalization → Deterministic algorithms
  → Candidate signal listing → LLM analysis (optional) → User research
  → Synthesis → Final report
```

## Reuse of research agent

Connectors wrap [`prediction_market_research_agent`](../../prediction_market_research_agent/) `MarketDataClient` (predmarket + CLOB). Order books use venue-native endpoints.

## Adding an algorithm

1. Subclass `SignalAlgorithm` in `algorithms/`.
2. Register in `deterministic_scoring_agent.build_registry()`.
3. Add weight in `config/prediction_market_signal_scoring.yaml` if combined in `signal_strength`.

## Adding a connector

1. Implement `PredictionMarketConnector` in `connectors/`.
2. Register in `discovery/market_discovery.py`.

## Pass 7 improvements (proposed)

- Promote `MarketDataClient` into `fin_agents_common` to avoid agent-on-agent dependency.
- Unify async entry (CLI currently uses `asyncio.run` wrapper).
- Persist momentum history with scheduled snapshot jobs.
- Standardize OTel attribute names across agents.
- Add integration tests against recorded API fixtures.
