# Shared Observability

All `fin_agents` agents share observability via `libs/fin_agents_common`.

## Components

| Component | Purpose |
|-----------|---------|
| OpenTelemetry | Pipeline and agent spans |
| Langfuse | LLM trace metadata |
| LiteLLM | Model routing (local library or proxy) |

## Docker profiles

```bash
# Postgres only
docker compose --profile core up -d

# LiteLLM proxy + Postgres
docker compose --profile core --profile litellm_proxy up -d

# OTel collector + Jaeger
docker compose --profile observability up -d

# Langfuse stack (ClickHouse, Redis, MinIO)
docker compose --profile core --profile langfuse up -d
```

## Configuration

- [`config/observability.yaml`](../../config/observability.yaml)
- [`config/llm.yaml`](../../config/llm.yaml)
- [`.env.example`](../../.env.example)

## Enable in an agent

```bash
python scripts/run_prediction_market_signals.py --observability-enabled
```

When infrastructure is unavailable, tracing helpers degrade gracefully (console/no-op).
