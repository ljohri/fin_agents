from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm


class CrossMarketConsistencyAlgorithm(SignalAlgorithm):
    name = "cross_market_consistency"

    def run(self, context: dict) -> AlgorithmResult:
        peers: list[dict] = context.get("peer_markets", [])
        market = context["market"]
        prob = market.implied_probability
        if prob is None or not peers:
            return AlgorithmResult(name=self.name, score=0.7, label="neutral")
        divergences = []
        for p in peers:
            pp = p.get("implied_probability")
            if pp is not None:
                divergences.append(abs(prob - pp))
        if not divergences:
            return AlgorithmResult(name=self.name, score=0.7)
        max_div = max(divergences)
        score = max(0.0, min(1.0, 1.0 - max_div * 2))
        warnings = ["Cross-venue divergence detected"] if max_div > 0.15 else []
        return AlgorithmResult(
            name=self.name,
            score=score,
            details={"max_divergence": max_div},
            warnings=warnings,
        )
