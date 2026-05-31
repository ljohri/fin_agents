import asyncio

from prediction_market_research_agent.clients.markets import MarketDataClient
from prediction_market_research_agent.config import Settings, get_settings
from prediction_market_research_agent.models.market import MarketResearchResult


class PredictionMarketResearchAgent:
    """Orchestrates market research across Kalshi and Polymarket."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = MarketDataClient(self._settings)

    def list_open_markets(self, *, limit: int = 20) -> MarketResearchResult:
        return asyncio.run(self._list_open_markets(limit=limit))

    async def _list_open_markets(self, *, limit: int) -> MarketResearchResult:
        kalshi_markets, polymarket_markets = await asyncio.gather(
            self._client.list_kalshi_markets(limit=limit),
            self._client.list_polymarket_markets(limit=limit),
        )
        return MarketResearchResult(
            kalshi_markets=kalshi_markets,
            polymarket_markets=polymarket_markets,
        )

    def get_kalshi_market(self, ticker: str):
        return asyncio.run(self._client.get_kalshi_market(ticker))

    def get_polymarket_market(self, slug: str):
        return asyncio.run(self._client.get_polymarket_market(slug))
