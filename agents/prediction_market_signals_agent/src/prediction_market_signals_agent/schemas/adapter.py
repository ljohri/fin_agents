from datetime import datetime

from prediction_market_signals_agent.market_data.models import PredictionMarket
from prediction_market_signals_agent.schemas.market import NormalizedMarket


def prediction_market_to_normalized(
    pm: PredictionMarket,
    *,
    topic: str | None = None,
    fetched_at: datetime | None = None,
) -> NormalizedMarket:
    fetched = fetched_at or datetime.now()
    spread = None
    if pm.yes_price is not None and pm.no_price is not None:
        spread = abs(1.0 - pm.yes_price - pm.no_price)
    return NormalizedMarket(
        venue=pm.venue.value,  # type: ignore[arg-type]
        market_id=pm.market_id,
        title=pm.title,
        question=pm.title,
        status=pm.status or "unknown",
        close_time=pm.close_time if isinstance(pm.close_time, datetime) else None,
        source_url=pm.url,
        fetched_at=fetched,
        implied_probability=pm.yes_price,
        best_bid_probability=pm.yes_price,
        best_ask_probability=pm.yes_price,
        spread=spread,
        volume=pm.volume,
        liquidity=pm.liquidity,
        topic=topic,
        raw_payload_ref=pm.market_id,
    )
