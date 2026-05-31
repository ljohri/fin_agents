from dataclasses import dataclass, field

from prediction_market_signals_agent.schemas.market import NormalizedMarket
from prediction_market_signals_agent.schemas.signal import PredictionMarketSignal
from prediction_market_signals_agent.schemas.user_research import UserResearchContext


@dataclass
class PipelineState:
    markets: list[NormalizedMarket] = field(default_factory=list)
    signals: list[PredictionMarketSignal] = field(default_factory=list)
    user_research: UserResearchContext | None = None
    report_path: str | None = None
    offline_demo: bool = False
    skip_llm: bool = False
    skip_user_research: bool = False
