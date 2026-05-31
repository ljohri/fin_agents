import json
from datetime import datetime

from predmarket.model.rest.contract import Contract

from prediction_market_research_agent.models.market import PredictionMarket, Venue


def _parse_dollar(value: str | float | None) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def yes_price_from_kalshi_raw(raw: dict) -> float | None:
    bid = _parse_dollar(raw.get("yes_bid_dollars"))
    ask = _parse_dollar(raw.get("yes_ask_dollars"))
    if bid is not None and ask is not None:
        return (bid + ask) / 2
    return _parse_dollar(raw.get("last_price_dollars"))


def yes_price_from_gamma_raw(raw: dict) -> float | None:
    prices = raw.get("outcomePrices")
    if isinstance(prices, str):
        prices = json.loads(prices)
    if prices:
        return _parse_dollar(prices[0])
    return None


def polymarket_yes_token_id(raw: dict) -> str | None:
    token_ids = raw.get("clobTokenIds")
    if isinstance(token_ids, str):
        token_ids = json.loads(token_ids)
    if token_ids:
        return str(token_ids[0])
    return None


def contract_to_prediction_market(
    contract: Contract,
    *,
    yes_price: float | None = None,
) -> PredictionMarket:
    raw = contract.raw
    venue = Venue.KALSHI if contract.platform == "kalshi" else Venue.POLYMARKET

    if yes_price is None:
        yes_price = (
            yes_price_from_kalshi_raw(raw)
            if venue == Venue.KALSHI
            else yes_price_from_gamma_raw(raw)
        )

    no_price = (1.0 - yes_price) if yes_price is not None else None
    market_id = contract.id

    volume: float | None = None
    liquidity: float | None = None
    close_time: datetime | str | None = None
    status: str | None = None
    url: str | None = None

    if venue == Venue.KALSHI:
        volume_raw = raw.get("volume_fp") or raw.get("volume")
        volume = float(volume_raw) if volume_raw not in (None, "") else None
        liquidity_raw = raw.get("liquidity_dollars")
        liquidity = float(liquidity_raw) if liquidity_raw not in (None, "") else None
        close_time = raw.get("close_time")
        status = raw.get("status")
        url = f"https://kalshi.com/markets/{market_id}"
    else:
        volume = _parse_dollar(raw.get("volume"))
        liquidity = _parse_dollar(raw.get("liquidity"))
        close_time = raw.get("endDate")
        status = "active" if raw.get("active") else "closed"
        slug = raw.get("slug")
        if slug:
            market_id = slug
            url = f"https://polymarket.com/event/{slug}"

    return PredictionMarket(
        venue=venue,
        market_id=market_id,
        title=contract.question or market_id,
        yes_price=yes_price,
        no_price=no_price,
        volume=volume,
        liquidity=liquidity,
        status=status,
        close_time=close_time,
        url=url,
        raw=raw,
    )
