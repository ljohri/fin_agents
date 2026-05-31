from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMMode = Literal["local_library", "proxy"]


class ModelPolicy(BaseModel):
    mode: LLMMode = "local_library"
    default_model: str = "openai/gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 3000
    timeout_seconds: int = 60
    proxy_base_url: str | None = None
    proxy_api_key_env: str = "LITELLM_API_KEY"
    vertex_credentials_path: str | None = None
    vertex_project: str | None = None
    vertex_location: str = "us-central1"
    enforce_json: bool = True
    max_json_retries: int = 2

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "ModelPolicy":
        llm = config.get("llm", config)
        proxy = config.get("proxy", {})
        structured = config.get("structured_output", {})
        return cls(
            mode=llm.get("mode", "local_library"),
            default_model=llm.get("default_model", "openai/gpt-4o-mini"),
            temperature=float(llm.get("temperature", 0.2)),
            max_tokens=int(llm.get("max_tokens", 3000)),
            timeout_seconds=int(llm.get("timeout_seconds", 60)),
            proxy_base_url=proxy.get("base_url"),
            proxy_api_key_env=proxy.get("api_key_env", "LITELLM_API_KEY"),
            vertex_credentials_path=llm.get("vertex_credentials_path"),
            vertex_project=llm.get("vertex_project"),
            vertex_location=llm.get("vertex_location", "us-central1"),
            enforce_json=structured.get("enforce_json", True),
            max_json_retries=int(structured.get("max_retries", 2)),
        )


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    litellm_api_key: str | None = None
    google_application_credentials: str | None = None
    vertex_project: str | None = None
    vertex_location: str = "us-central1"
