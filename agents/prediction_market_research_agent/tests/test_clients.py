import pytest
from predmarket.model.rest.contract import Contract

from prediction_market_research_agent.clients.adapter import (
    contract_to_prediction_market,
    polymarket_yes_token_id,
    yes_price_from_kalshi_raw,
    yes_price_from_gamma_raw,
)
from prediction_market_research_agent.clients.clob import PolymarketClobClient
from prediction_market_research_agent.config import Settings
from prediction_market_research_agent.models.market import Venue


def test_yes_price_from_kalshi_midpoint():
    raw = {"yes_bid_dollars": "0.40", "yes_ask_dollars": "0.60"}
    assert yes_price_from_kalshi_raw(raw) == 0.5


def test_yes_price_from_gamma():
    raw = {"outcomePrices": '["0.60", "0.40"]'}
    assert yes_price_from_gamma_raw(raw) == pytest.approx(0.6)


def test_polymarket_yes_token_id():
    raw = {"clobTokenIds": '["token-yes", "token-no"]'}
    assert polymarket_yes_token_id(raw) == "token-yes"


def test_contract_to_prediction_market_kalshi():
    contract = Contract.from_kalshi(
        {
            "ticker": "TEST-MARKET",
            "title": "Will it rain?",
            "status": "active",
            "yes_bid_dollars": "0.45",
            "yes_ask_dollars": "0.55",
            "volume_fp": "1000.00",
            "liquidity_dollars": "500.00",
            "close_time": "2026-12-31T00:00:00Z",
        }
    )
    market = contract_to_prediction_market(contract)
    assert market.venue == Venue.KALSHI
    assert market.market_id == "TEST-MARKET"
    assert market.yes_price == pytest.approx(0.5)


def test_contract_to_prediction_market_polymarket_with_clob_price():
    contract = Contract.from_polymarket(
        {
            "id": "1",
            "slug": "test-market",
            "question": "Will X happen?",
            "clobTokenIds": '["token-yes", "token-no"]',
            "outcomePrices": '["0.60", "0.40"]',
            "volume": "10000",
            "liquidity": "5000",
            "active": True,
            "endDate": "2026-12-31T00:00:00Z",
        }
    )
    market = contract_to_prediction_market(contract, yes_price=0.62)
    assert market.venue == Venue.POLYMARKET
    assert market.market_id == "test-market"
    assert market.yes_price == pytest.approx(0.62)
    assert market.url == "https://polymarket.com/event/test-market"


@pytest.mark.asyncio
async def test_clob_midpoint(httpx_mock):
    import httpx

    settings = Settings()
    httpx_mock.add_response(
        url=f"{settings.polymarket_clob_api_url}/midpoint?token_id=token-yes",
        json={"mid": "0.62"},
    )

    async with httpx.AsyncClient() as client:
        clob = PolymarketClobClient(settings, client)
        assert await clob.get_midpoint("token-yes") == pytest.approx(0.62)
