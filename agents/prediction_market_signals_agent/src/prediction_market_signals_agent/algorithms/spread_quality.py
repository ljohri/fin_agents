from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm


class SpreadQualityAlgorithm(SignalAlgorithm):
    name = "spread_quality"

    def run(self, context: dict) -> AlgorithmResult:
        market = context["market"]
        ob = context.get("orderbook")
        spread = market.spread
        if ob and ob.spread_yes is not None:
            spread = ob.spread_yes
        if spread is None:
            return AlgorithmResult(name=self.name, score=0.3, label="noisy", warnings=["No spread data"])
        if spread <= 0.02:
            return AlgorithmResult(name=self.name, score=1.0, label="strong", details={"spread": spread})
        if spread <= 0.05:
            return AlgorithmResult(name=self.name, score=0.75, label="usable", details={"spread": spread})
        if spread <= 0.10:
            return AlgorithmResult(name=self.name, score=0.5, label="weak", details={"spread": spread})
        return AlgorithmResult(name=self.name, score=0.2, label="noisy", details={"spread": spread})
