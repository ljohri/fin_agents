from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Venue(str, Enum):
    KALSHI = "kalshi"
    POLYMARKET = "polymarket"


class PredictionMarket(BaseModel):
    """Normalized binary market view used internally by the signals agent."""

    venue: Venue
    market_id: str
    title: str
    yes_price: float | None = Field(None, ge=0.0, le=1.0)
    no_price: float | None = Field(None, ge=0.0, le=1.0)
    volume: float | None = None
    liquidity: float | None = None
    status: str | None = None
    close_time: datetime | None = None
    url: str | None = None
    raw: dict = Field(default_factory=dict, repr=False)
