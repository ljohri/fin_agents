import httpx

from prediction_market_research_agent.config import Settings


class PolymarketClobClient:
    """Live Polymarket prices via the CLOB API (not covered by predmarket Gamma REST)."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self._base = settings.polymarket_clob_api_url.rstrip("/")
        self._client = client

    async def get_midpoint(self, token_id: str) -> float | None:
        response = await self._client.get(
            f"{self._base}/midpoint",
            params={"token_id": token_id},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        mid = response.json().get("mid")
        try:
            return float(mid) if mid is not None else None
        except (TypeError, ValueError):
            return None
