# Architecture

`fin_agents` is a **multi-agent monorepo**. Each agent is an independently deployable unit with its own code, dependencies, tests, and documentation. Agents share only repository-level conventions—not runtime coupling.

## Directory layout

```text
fin_agents/
├── docs/                          # Repo-wide docs (this directory)
├── libs/
│   └── fin_agents_common/         # Shared LLM + observability
├── config/                        # Shared llm.yaml, observability.yaml
├── docker-compose.yml             # Shared Postgres, LiteLLM, Langfuse, OTel
├── agents/
│   └── <agent_name>/              # One directory per agent
│       ├── README.md
│       ├── pyproject.toml
│       ├── .venv/                 # Agent-local virtualenv
│       ├── docs/
│       ├── src/<agent_name>/
│       ├── tests/
│       └── scripts/
├── pyproject.toml
├── .env.example
└── README.md
```

## Design principles

1. **Independent agents** — Each agent can be installed, tested, and run on its own (`pip install -e agents/<agent_name>`).
2. **Agent-local virtualenvs** — Agents may maintain their own `.venv` (e.g. `agents/prediction_market_research_agent/.venv`) so dependencies—including GitHub-sourced packages—do not collide with the repo root or other agents.
3. **Explicit data contracts** — Use Pydantic models for inputs/outputs; avoid hidden shared global state between agents.
4. **Provider abstraction** — External APIs live behind client/adapter modules inside each agent. Prefer unified SDKs (e.g. [predmarket](https://github.com/ashercn97/predmarket)) where they reduce duplication; keep thin custom layers when SDK coverage is incomplete.
5. **Docs at two levels** — Root `docs/` for cross-cutting concerns; per-agent `docs/` for domain, architecture, and integration details.
6. **Research, not advice** — Agents produce structured analysis for human review, not automated trading or financial advice.

## Adding a new agent

1. Create `agents/<agent_name>/` following the layout above.
2. Add a row to [agents.md](./agents.md).
3. Document API integrations in `agents/<agent_name>/docs/`.
4. Keep secrets in `.env` (never committed); document required variables in `.env.example`.

## Shared infrastructure

- **Library:** [`libs/fin_agents_common`](../libs/fin_agents_common/) — LiteLLM client (API keys + Vertex service-account JSON), OpenTelemetry, Langfuse helpers.
- **Docker:** [`docker-compose.yml`](../docker-compose.yml) — profiles `core`, `litellm_proxy`, `observability`, `langfuse`.
- **Docs:** [observability/shared_observability.md](./observability/shared_observability.md).

## Current agents

See [agents.md](./agents.md) for the live index.
