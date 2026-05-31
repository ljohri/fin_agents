from abc import ABC, abstractmethod

from prediction_market_signals_agent.schemas.market import NormalizedMarket, NormalizedOrderBook


class PredictionMarketConnector(ABC):
    venue: str

    @abstractmethod
    async def search_markets(self, query: str, *, limit: int = 50) -> list[NormalizedMarket]:
        pass

    @abstractmethod
    async def get_market(self, market_id: str) -> NormalizedMarket:
        pass

    @abstractmethod
    async def get_orderbook(self, market_id: str) -> NormalizedOrderBook | None:
        pass

    async def get_recent_trades(self, market_id: str) -> list[dict]:
        return []
