from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Venue = Literal["kalshi", "polymarket"]


class NormalizedMarket(BaseModel):
    venue: Venue
    market_id: str
    event_id: str | None = None
    title: str
    question: str
    description: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: str
    close_time: datetime | None = None
    resolution_time: datetime | None = None
    resolution_rule: str | None = None
    source_url: str | None = None
    raw_payload_ref: str | None = None
    fetched_at: datetime
    implied_probability: float | None = None
    best_bid_probability: float | None = None
    best_ask_probability: float | None = None
    spread: float | None = None
    volume: float | None = None
    liquidity: float | None = None
    topic: str | None = None


class PriceLevel(BaseModel):
    price: float
    size: float


class NormalizedOrderBook(BaseModel):
    venue: Venue
    market_id: str
    captured_at: datetime
    yes_bids: list[PriceLevel] = Field(default_factory=list)
    yes_asks: list[PriceLevel] = Field(default_factory=list)
    no_bids: list[PriceLevel] = Field(default_factory=list)
    no_asks: list[PriceLevel] = Field(default_factory=list)
    best_yes_bid: float | None = None
    best_yes_ask: float | None = None
    mid_yes: float | None = None
    spread_yes: float | None = None
    raw_payload_ref: str | None = None
