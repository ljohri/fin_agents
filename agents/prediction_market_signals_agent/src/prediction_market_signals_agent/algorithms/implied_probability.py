from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm


class ImpliedProbabilityAlgorithm(SignalAlgorithm):
    name = "implied_probability"

    def run(self, context: dict) -> AlgorithmResult:
        market = context["market"]
        ob = context.get("orderbook")
        warnings: list[str] = []
        prob = market.implied_probability
        if ob and ob.mid_yes is not None:
            prob = ob.mid_yes
        elif prob is None:
            warnings.append("No bid/ask or last price available")
            return AlgorithmResult(name=self.name, score=None, warnings=warnings)
        if market.spread and market.spread > 0.10:
            warnings.append("Wide spread; lower confidence")
        return AlgorithmResult(
            name=self.name,
            score=max(0.0, min(1.0, prob)),
            details={"implied_probability": prob},
            warnings=warnings,
        )
