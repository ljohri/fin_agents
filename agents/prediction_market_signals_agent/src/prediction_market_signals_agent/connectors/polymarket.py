from datetime import UTC, datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.connectors.base import PredictionMarketConnector
from prediction_market_signals_agent.market_data.adapter import polymarket_yes_token_id
from prediction_market_signals_agent.market_data.client import MarketDataClient
from prediction_market_signals_agent.schemas.adapter import prediction_market_to_normalized
from prediction_market_signals_agent.schemas.market import (
    NormalizedMarket,
    NormalizedOrderBook,
    PriceLevel,
)
from prediction_market_signals_agent.storage.raw_payload_store import RawPayloadStore


class PolymarketConnector(PredictionMarketConnector):
    venue = "polymarket"

    def __init__(self, settings: AgentSettings, raw_store: RawPayloadStore | None = None) -> None:
        self._settings = settings
        self._market_data = MarketDataClient(settings)
        self._raw = raw_store or RawPayloadStore(settings.snapshots_dir / "raw")
        self._clob = settings.polymarket_clob_api_url.rstrip("/")
        self._gamma = settings.polymarket_gamma_api_url.rstrip("/")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def search_markets(self, query: str, *, limit: int = 50) -> list[NormalizedMarket]:
        markets = await self._market_data.list_polymarket_markets(limit=limit)
        q = query.lower()
        results = []
        for market in markets:
            if q in market.title.lower() or q in market.market_id.lower():
                normalized = prediction_market_to_normalized(market, topic=query)
                self._raw.save(self.venue, market.market_id, market.raw)
                results.append(normalized)
        return results

    async def get_market(self, market_id: str) -> NormalizedMarket:
        market = await self._market_data.get_polymarket_market(market_id)
        self._raw.save(self.venue, market_id, market.raw)
        return prediction_market_to_normalized(market)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def get_orderbook(self, market_id: str) -> NormalizedOrderBook | None:
        async with httpx.AsyncClient(timeout=self._settings.http_timeout_seconds) as client:
            gamma = await client.get(f"{self._gamma}/markets", params={"slug": market_id})
            if gamma.status_code != 200 or not gamma.json():
                return None
            raw = gamma.json()[0] if isinstance(gamma.json(), list) else gamma.json()
            token_id = polymarket_yes_token_id(raw)
            if not token_id:
                return None
            response = await client.get(f"{self._clob}/book", params={"token_id": token_id})
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
        self._raw.save(self.venue, f"{market_id}_orderbook", data)
        bids = [PriceLevel(price=float(b["price"]), size=float(b["size"])) for b in data.get("bids", [])]
        asks = [PriceLevel(price=float(a["price"]), size=float(a["size"])) for a in data.get("asks", [])]
        best_bid = bids[0].price if bids else None
        best_ask = asks[0].price if asks else None
        mid = (best_bid + best_ask) / 2 if best_bid and best_ask else best_bid
        spread = (best_ask - best_bid) if best_bid and best_ask else None
        return NormalizedOrderBook(
            venue="polymarket",
            market_id=market_id,
            captured_at=datetime.now(UTC),
            yes_bids=bids,
            yes_asks=asks,
            best_yes_bid=best_bid,
            best_yes_ask=best_ask,
            mid_yes=mid,
            spread_yes=spread,
            raw_payload_ref=market_id,
        )
