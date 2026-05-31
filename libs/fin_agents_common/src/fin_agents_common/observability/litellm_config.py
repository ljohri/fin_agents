"""LiteLLM proxy / Langfuse callback configuration helpers."""

from __future__ import annotations

import os
from typing import Any


def langfuse_litellm_callbacks() -> list[str]:
    if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
        return ["langfuse"]
    return []


def proxy_database_url() -> str | None:
    return os.getenv(
        "LITELLM_DATABASE_URL",
        "postgresql://fin_agents:fin_agents@localhost:5432/litellm",
    )


def observability_env() -> dict[str, Any]:
    return {
        "LANGFUSE_HOST": os.getenv("LANGFUSE_HOST"),
        "OTEL_EXPORTER_OTLP_ENDPOINT": os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        "LITELLM_MODE": os.getenv("LITELLM_MODE", "local_library"),
    }
