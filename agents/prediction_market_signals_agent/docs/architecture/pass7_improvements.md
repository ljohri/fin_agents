# Pass 7 — Architecture Improvement Notes

## Boundaries

- **Algorithms** should remain pure functions of `context` dicts; no I/O inside `algorithms/`.
- **Agents** orchestrate stages and write intermediate artifacts.
- **Connectors** own external API I/O only.

## Async

- Pipeline is async internally; CLI uses `run_pipeline_sync`. Consider native async CLI (Typer + asyncio) for long-running live ingestion.

## Persistence

- DuckDB snapshots enable momentum; schedule `collect_prediction_market_snapshots` for history.
- Postgres store is optional until Docker `core` profile is up.

## Observability

- Align span attributes: `fin_agents.agent_name`, `fin_agents.pipeline_stage`, `fin_agents.signal_id`.
- Enable Langfuse only when keys are set; never log prompts by default (`pii.log_prompts: false`).

## Dependencies

- Move shared market clients from `prediction_market_research_agent` into `fin_agents_common` when a third agent needs them.
