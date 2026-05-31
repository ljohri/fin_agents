from prediction_market_signals_agent.algorithms.implied_probability import ImpliedProbabilityAlgorithm
from prediction_market_signals_agent.algorithms.market_relevance import MarketRelevanceAlgorithm
from prediction_market_signals_agent.algorithms.spread_quality import SpreadQualityAlgorithm
from prediction_market_signals_agent.schemas.market import NormalizedMarket
from datetime import UTC, datetime


def _market(**kwargs) -> NormalizedMarket:
    base = dict(
        venue="kalshi",
        market_id="TEST",
        title="Fed rate hike in 2026",
        question="Fed rate hike?",
        status="active",
        fetched_at=datetime.now(UTC),
        implied_probability=0.5,
        spread=0.03,
    )
    base.update(kwargs)
    return NormalizedMarket(**base)


def test_implied_probability():
    r = ImpliedProbabilityAlgorithm().run({"market": _market()})
    assert r.score == 0.5


def test_spread_quality_usable():
    r = SpreadQualityAlgorithm().run({"market": _market(spread=0.04)})
    assert r.label == "usable"


def test_market_relevance_high():
    r = MarketRelevanceAlgorithm().run({"market": _market(title="Federal reserve inflation CPI")})
    assert r.score >= 0.5
