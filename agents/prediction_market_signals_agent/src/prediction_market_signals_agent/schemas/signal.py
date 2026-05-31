from datetime import datetime

from pydantic import BaseModel, Field

from prediction_market_signals_agent.schemas.market import Venue


class PredictionMarketSignal(BaseModel):
    signal_id: str
    topic: str
    venue: Venue
    market_id: str
    event_id: str | None = None
    market_title: str
    market_question: str
    implied_probability: float | None = None
    best_bid_probability: float | None = None
    best_ask_probability: float | None = None
    spread: float | None = None
    liquidity_score: float | None = None
    spread_quality_score: float | None = None
    probability_momentum_score: float | None = None
    capital_market_relevance_score: float | None = None
    cross_market_consistency_score: float | None = None
    deterministic_signal_strength: float | None = None
    deterministic_label: str | None = None
    llm_signal_strength: str | None = None
    llm_analysis_summary: str | None = None
    key_caveats: list[str] = Field(default_factory=list)
    related_assets_or_markets: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    generated_at: datetime
    algorithm_details: dict = Field(default_factory=dict)
