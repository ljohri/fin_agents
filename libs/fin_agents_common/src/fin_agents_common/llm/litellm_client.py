from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fin_agents_common.common.errors import LLMError
from fin_agents_common.common.logging import get_logger
from fin_agents_common.llm.model_policy import LLMSettings, ModelPolicy
from fin_agents_common.llm.structured_output import parse_json_response

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


class LiteLLMClient:
    """Routes LLM calls through LiteLLM (local library or proxy)."""

    def __init__(
        self,
        policy: ModelPolicy | None = None,
        settings: LLMSettings | None = None,
    ) -> None:
        self.policy = policy or ModelPolicy()
        self.settings = settings or LLMSettings()
        self._apply_env_credentials()

    def _apply_env_credentials(self) -> None:
        if self.settings.openai_api_key:
            os.environ.setdefault("OPENAI_API_KEY", self.settings.openai_api_key)
        if self.settings.anthropic_api_key:
            os.environ.setdefault("ANTHROPIC_API_KEY", self.settings.anthropic_api_key)
        if self.settings.gemini_api_key:
            os.environ.setdefault("GEMINI_API_KEY", self.settings.gemini_api_key)
        creds = self.settings.google_application_credentials or self.policy.vertex_credentials_path
        if creds:
            os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(Path(creds).resolve()))

    def _completion_kwargs(self, model: str | None) -> dict[str, Any]:
        model = model or self.policy.default_model
        kwargs: dict[str, Any] = {
            "model": model,
            "temperature": self.policy.temperature,
            "max_tokens": self.policy.max_tokens,
            "timeout": self.policy.timeout_seconds,
        }
        if self.policy.mode == "proxy" and self.policy.proxy_base_url:
            kwargs["api_base"] = self.policy.proxy_base_url
            key_env = self.policy.proxy_api_key_env
            if os.getenv(key_env):
                kwargs["api_key"] = os.getenv(key_env)
        if model.startswith("vertex_ai/") or model.startswith("gemini/"):
            if self.policy.vertex_project or self.settings.vertex_project:
                kwargs["vertex_project"] = (
                    self.policy.vertex_project or self.settings.vertex_project
                )
            kwargs["vertex_location"] = (
                self.policy.vertex_location or self.settings.vertex_location
            )
            creds = self.policy.vertex_credentials_path or self.settings.google_application_credentials
            if creds:
                kwargs["vertex_credentials"] = str(Path(creds).resolve())
        return kwargs

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        json_mode: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> LLMResponse:
        try:
            import litellm
        except ImportError as exc:
            raise LLMError("litellm is not installed") from exc

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        kwargs = self._completion_kwargs(model)
        if json_mode or self.policy.enforce_json:
            kwargs["response_format"] = {"type": "json_object"}

        logger.info("LLM call model=%s mode=%s", kwargs["model"], self.policy.mode)
        try:
            response = litellm.completion(messages=messages, **kwargs)
        except Exception as exc:
            raise LLMError(f"LiteLLM completion failed: {exc}") from exc

        content = response.choices[0].message.content or ""
        usage = dict(response.usage) if getattr(response, "usage", None) else {}
        return LLMResponse(
            content=content,
            model=kwargs["model"],
            usage=usage,
            raw={"metadata": metadata or {}},
        )

    def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.policy.max_json_retries + 1):
            try:
                resp = self.complete(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=model,
                    json_mode=True,
                    metadata=metadata,
                )
                return parse_json_response(resp.content)
            except Exception as exc:
                last_error = exc
                logger.warning("JSON parse attempt %s failed: %s", attempt + 1, exc)
        raise LLMError(f"Failed to get valid JSON after retries: {last_error}")
