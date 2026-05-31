import httpx
from predmarket import KalshiRest, PolymarketRest
from predmarket.model.rest.contract import Contract

from prediction_market_research_agent.clients.adapter import (
    contract_to_prediction_market,
    polymarket_yes_token_id,
)
from prediction_market_research_agent.clients.clob import PolymarketClobClient
from prediction_market_research_agent.config import Settings
from prediction_market_research_agent.models.market import PredictionMarket


class MarketDataClient:
    """Fetches normalized markets via predmarket, with CLOB midpoints for Polymarket."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_kalshi_markets(self, *, limit: int = 20) -> list[PredictionMarket]:
        async with httpx.AsyncClient(timeout=self._settings.http_timeout_seconds) as client:
            kalshi = KalshiRest(client)
            response = await kalshi.fetch_contracts(status="open", limit=limit)
            return [
                contract_to_prediction_market(contract)
                for contract in response.data
            ]

    async def get_kalshi_market(self, ticker: str) -> PredictionMarket:
        async with httpx.AsyncClient(timeout=self._settings.http_timeout_seconds) as client:
            kalshi = KalshiRest(client)
            response = await kalshi.fetch_contract(ticker)
            return contract_to_prediction_market(response.data)

    async def list_polymarket_markets(self, *, limit: int = 20) -> list[PredictionMarket]:
        async with httpx.AsyncClient(timeout=self._settings.http_timeout_seconds) as client:
            polymarket = PolymarketRest(client)
            clob = PolymarketClobClient(self._settings, client)
            response = await polymarket.fetch_contracts(
                active=True,
                closed=False,
                limit=limit,
            )
            return [
                await self._enrich_polymarket_contract(contract, clob)
                for contract in response.data
            ]

    async def get_polymarket_market(self, slug: str) -> PredictionMarket:
        async with httpx.AsyncClient(timeout=self._settings.http_timeout_seconds) as client:
            polymarket = PolymarketRest(client)
            clob = PolymarketClobClient(self._settings, client)
            response = await polymarket.fetch_contracts(slug=slug)
            if not response.data:
                raise LookupError(f"Polymarket market not found: {slug}")
            return await self._enrich_polymarket_contract(response.data[0], clob)

    async def _enrich_polymarket_contract(
        self,
        contract: Contract,
        clob: PolymarketClobClient,
    ) -> PredictionMarket:
        yes_price = None
        token_id = polymarket_yes_token_id(contract.raw)
        if token_id:
            yes_price = await clob.get_midpoint(token_id)
        return contract_to_prediction_market(contract, yes_price=yes_price)
