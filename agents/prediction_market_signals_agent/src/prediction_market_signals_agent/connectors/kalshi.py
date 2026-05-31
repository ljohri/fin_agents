from datetime import UTC, datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.connectors.base import PredictionMarketConnector
from prediction_market_signals_agent.market_data.client import MarketDataClient
from prediction_market_signals_agent.schemas.adapter import prediction_market_to_normalized
from prediction_market_signals_agent.schemas.market import (
    NormalizedMarket,
    NormalizedOrderBook,
    PriceLevel,
)
from prediction_market_signals_agent.storage.raw_payload_store import RawPayloadStore


class KalshiConnector(PredictionMarketConnector):
    venue = "kalshi"

    def __init__(self, settings: AgentSettings, raw_store: RawPayloadStore | None = None) -> None:
        self._settings = settings
        self._market_data = MarketDataClient(settings)
        self._raw = raw_store or RawPayloadStore(settings.snapshots_dir / "raw")
        self._base = settings.kalshi_api_base_url.rstrip("/")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def search_markets(self, query: str, *, limit: int = 50) -> list[NormalizedMarket]:
        markets = await self._market_data.list_kalshi_markets(limit=limit)
        q = query.lower()
        results = []
        for market in markets:
            if q in market.title.lower() or q in market.market_id.lower():
                normalized = prediction_market_to_normalized(market, topic=query)
                self._raw.save(self.venue, market.market_id, market.raw)
                results.append(normalized)
        return results

    async def get_market(self, market_id: str) -> NormalizedMarket:
        market = await self._market_data.get_kalshi_market(market_id)
        self._raw.save(self.venue, market_id, market.raw)
        return prediction_market_to_normalized(market)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def get_orderbook(self, market_id: str) -> NormalizedOrderBook | None:
        async with httpx.AsyncClient(timeout=self._settings.http_timeout_seconds) as client:
            response = await client.get(f"{self._base}/markets/{market_id}/orderbook")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
        self._raw.save(self.venue, f"{market_id}_orderbook", data)
        orderbook = data.get("orderbook", data)
        yes_bids = [
            PriceLevel(price=float(price) / 100, size=float(size))
            for price, size in orderbook.get("yes", []) or []
        ]
        no_bids = [
            PriceLevel(price=float(price) / 100, size=float(size))
            for price, size in orderbook.get("no", []) or []
        ]
        best_bid = yes_bids[0].price if yes_bids else None
        best_ask = 1.0 - no_bids[0].price if no_bids else None
        mid = (best_bid + best_ask) / 2 if best_bid and best_ask else best_bid
        spread = (best_ask - best_bid) if best_bid and best_ask else None
        return NormalizedOrderBook(
            venue="kalshi",
            market_id=market_id,
            captured_at=datetime.now(UTC),
            yes_bids=yes_bids,
            no_bids=no_bids,
            best_yes_bid=best_bid,
            best_yes_ask=best_ask,
            mid_yes=mid,
            spread_yes=spread,
            raw_payload_ref=market_id,
        )
