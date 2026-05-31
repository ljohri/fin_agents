from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

AGENT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = AGENT_ROOT.parent.parent


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    agent_root: Path = AGENT_ROOT
    repo_root: Path = REPO_ROOT
    topics_config: Path = AGENT_ROOT / "config" / "prediction_market_topics.yaml"
    scoring_config: Path = AGENT_ROOT / "config" / "prediction_market_signal_scoring.yaml"
    data_sources_config: Path = AGENT_ROOT / "config" / "data_sources.yaml"
    llm_config: Path = REPO_ROOT / "config" / "llm.yaml"
    observability_config: Path = REPO_ROOT / "config" / "observability.yaml"
    user_research_dir: Path = AGENT_ROOT / "data" / "user_research"
    intermediate_dir: Path = AGENT_ROOT / "data" / "intermediate"
    reports_dir: Path = AGENT_ROOT / "data" / "reports"
    snapshots_dir: Path = AGENT_ROOT / "data" / "snapshots"
    kalshi_api_base_url: str = "https://api.elections.kalshi.com/trade-api/v2"
    polymarket_gamma_api_url: str = "https://gamma-api.polymarket.com"
    polymarket_clob_api_url: str = "https://clob.polymarket.com"
    http_timeout_seconds: float = 30.0


def get_settings() -> AgentSettings:
    return AgentSettings()
