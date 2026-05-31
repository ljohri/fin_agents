from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    kalshi_api_base_url: str = "https://api.elections.kalshi.com/trade-api/v2"
    kalshi_api_key_id: str | None = None
    kalshi_private_key_path: str | None = None

    polymarket_gamma_api_url: str = "https://gamma-api.polymarket.com"
    polymarket_clob_api_url: str = "https://clob.polymarket.com"

    http_timeout_seconds: float = 30.0


def get_settings() -> Settings:
    return Settings()
