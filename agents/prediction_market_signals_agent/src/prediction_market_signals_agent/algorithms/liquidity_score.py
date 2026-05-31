from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm


class LiquidityScoreAlgorithm(SignalAlgorithm):
    name = "liquidity_score"

    def run(self, context: dict) -> AlgorithmResult:
        market = context["market"]
        ob = context.get("orderbook")
        score = 0.3
        if market.volume and market.volume > 10000:
            score += 0.2
        if market.liquidity and market.liquidity > 5000:
            score += 0.2
        if ob:
            depth = len(ob.yes_bids) + len(ob.yes_asks)
            score += min(0.3, depth * 0.05)
        spread_result = context.get("algorithm_results", {}).get("spread_quality")
        if spread_result and spread_result.score:
            score = (score + spread_result.score) / 2
        score = max(0.0, min(1.0, score))
        label = "strong" if score >= 0.8 else "usable" if score >= 0.6 else "weak" if score >= 0.4 else "noisy"
        return AlgorithmResult(name=self.name, score=score, label=label)
