from __future__ import annotations

import os
from typing import Any

from fin_agents_common.common.logging import get_logger

logger = get_logger(__name__)


class LangfuseClient:
    """Thin wrapper around Langfuse SDK; no-ops when disabled or unavailable."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        host: str | None = None,
        public_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self.enabled = enabled
        self.host = host or os.getenv("LANGFUSE_HOST", "http://localhost:3000")
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self._client: Any = None

        if not self.enabled:
            return
        if not self.public_key or not self.secret_key:
            logger.info("Langfuse disabled: missing keys")
            self.enabled = False
            return
        try:
            from langfuse import Langfuse

            self._client = Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host,
            )
        except ImportError:
            logger.info("Langfuse SDK not installed; tracing disabled")
            self.enabled = False

    def trace_metadata(self, **kwargs: Any) -> dict[str, Any]:
        return {k: v for k, v in kwargs.items() if v is not None}

    def flush(self) -> None:
        if self._client:
            self._client.flush()
