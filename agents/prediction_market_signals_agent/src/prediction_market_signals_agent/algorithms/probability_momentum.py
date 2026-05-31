from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm


class ProbabilityMomentumAlgorithm(SignalAlgorithm):
    name = "probability_momentum"

    def run(self, context: dict) -> AlgorithmResult:
        market = context["market"]
        prior = context.get("prior_probability")
        current = market.implied_probability
        if current is None or prior is None:
            return AlgorithmResult(
                name=self.name,
                score=0.5,
                label="neutral",
                warnings=["Insufficient history for momentum"],
            )
        delta = current - prior
        score = max(0.0, min(1.0, 0.5 + abs(delta) * 2))
        label = "rising" if delta > 0.05 else "falling" if delta < -0.05 else "stable"
        return AlgorithmResult(
            name=self.name,
            score=score,
            label=label,
            details={"delta": delta, "prior": prior, "current": current},
        )
