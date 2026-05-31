from fin_agents_common.common.config import load_yaml_config
from fin_agents_common.common.ids import new_signal_id
from fin_agents_common.common.time import utc_now
from fin_agents_common.observability.decorators import trace_agent

from prediction_market_signals_agent.algorithms.cross_market_consistency import (
    CrossMarketConsistencyAlgorithm,
)
from prediction_market_signals_agent.algorithms.implied_probability import (
    ImpliedProbabilityAlgorithm,
)
from prediction_market_signals_agent.algorithms.liquidity_score import LiquidityScoreAlgorithm
from prediction_market_signals_agent.algorithms.market_relevance import MarketRelevanceAlgorithm
from prediction_market_signals_agent.algorithms.probability_momentum import (
    ProbabilityMomentumAlgorithm,
)
from prediction_market_signals_agent.algorithms.registry import AlgorithmRegistry
from prediction_market_signals_agent.algorithms.signal_strength import SignalStrengthAlgorithm
from prediction_market_signals_agent.algorithms.spread_quality import SpreadQualityAlgorithm
from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.schemas.market import NormalizedMarket
from prediction_market_signals_agent.schemas.signal import PredictionMarketSignal
from prediction_market_signals_agent.storage.duckdb_store import DuckDBStore


def build_registry(settings: AgentSettings) -> AlgorithmRegistry:
    cfg = load_yaml_config(settings.scoring_config)
    registry = AlgorithmRegistry()
    registry.register(ImpliedProbabilityAlgorithm())
    registry.register(SpreadQualityAlgorithm())
    registry.register(LiquidityScoreAlgorithm())
    registry.register(ProbabilityMomentumAlgorithm())
    registry.register(MarketRelevanceAlgorithm())
    registry.register(CrossMarketConsistencyAlgorithm())
    registry.register(
        SignalStrengthAlgorithm(weights=cfg.get("weights", {}), labels=cfg.get("labels", {}))
    )
    return registry


@trace_agent("prediction_market.deterministic_scoring")
def score_markets(
    markets: list[NormalizedMarket],
    settings: AgentSettings,
    orderbooks: dict[tuple[str, str], object] | None = None,
) -> list[PredictionMarketSignal]:
    registry = build_registry(settings)
    duck = DuckDBStore(settings.snapshots_dir / "markets.duckdb")
    by_topic: dict[str, list[NormalizedMarket]] = {}
    for m in markets:
        by_topic.setdefault(m.topic or "general", []).append(m)

    signals: list[PredictionMarketSignal] = []
    for market in markets:
        ob = (orderbooks or {}).get((market.venue, market.market_id))
        prior = duck.get_prior_probability(market.venue, market.market_id)
        peers = [
            {"implied_probability": p.implied_probability}
            for p in by_topic.get(market.topic or "general", [])
            if p.market_id != market.market_id
        ]
        ctx = {
            "market": market,
            "orderbook": ob,
            "prior_probability": prior,
            "peer_markets": peers,
        }
        results = {}
        for name, algo in [
            ("implied_probability", ImpliedProbabilityAlgorithm()),
            ("spread_quality", SpreadQualityAlgorithm()),
            ("liquidity_score", LiquidityScoreAlgorithm()),
            ("probability_momentum", ProbabilityMomentumAlgorithm()),
            ("capital_market_relevance", MarketRelevanceAlgorithm()),
            ("cross_market_consistency", CrossMarketConsistencyAlgorithm()),
        ]:
            results[name] = algo.run(ctx)
        ctx["algorithm_results"] = results
        cfg = load_yaml_config(settings.scoring_config)
        strength = SignalStrengthAlgorithm(
            weights=cfg.get("weights", {}), labels=cfg.get("labels", {})
        ).run(ctx)
        results["signal_strength"] = strength
        imp = results["implied_probability"]
        prob = imp.score if imp.score is not None else market.implied_probability
        signal = PredictionMarketSignal(
            signal_id=new_signal_id(),
            topic=market.topic or "general",
            venue=market.venue,
            market_id=market.market_id,
            market_title=market.title,
            market_question=market.question,
            implied_probability=prob,
            spread=results["spread_quality"].details.get("spread", market.spread),
            liquidity_score=results["liquidity_score"].score,
            spread_quality_score=results["spread_quality"].score,
            probability_momentum_score=results["probability_momentum"].score,
            capital_market_relevance_score=results["capital_market_relevance"].score,
            cross_market_consistency_score=results["cross_market_consistency"].score,
            deterministic_signal_strength=strength.score,
            deterministic_label=strength.label,
            key_caveats=sum((r.warnings for r in results.values()), []),
            source_refs=[market.source_url] if market.source_url else [],
            generated_at=utc_now(),
            algorithm_details={k: v.model_dump() for k, v in results.items()},
        )
        duck.save_snapshot(market)
        signals.append(signal)
    duck.close()
    return signals
