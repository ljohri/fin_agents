from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm


class SignalStrengthAlgorithm(SignalAlgorithm):
    name = "signal_strength"

    def __init__(self, weights: dict[str, float], labels: dict[str, float]) -> None:
        self.weights = weights
        self.labels = labels

    def run(self, context: dict) -> AlgorithmResult:
        results = context.get("algorithm_results", {})
        total = 0.0
        weight_sum = 0.0
        mapping = {
            "capital_market_relevance": "capital_market_relevance",
            "liquidity_score": "liquidity_score",
            "probability_momentum": "probability_momentum",
            "spread_quality": "spread_quality",
            "cross_market_consistency": "cross_market_consistency",
        }
        for key, algo_name in mapping.items():
            w = self.weights.get(f"{key}_score", self.weights.get(key, 0))
            r = results.get(algo_name)
            if r and r.score is not None:
                total += w * r.score
                weight_sum += w
        score = total / weight_sum if weight_sum else 0.0
        label = "noisy"
        if score >= self.labels.get("strong", 0.8):
            label = "strong"
        elif score >= self.labels.get("moderate", 0.6):
            label = "moderate"
        elif score >= self.labels.get("weak", 0.4):
            label = "weak"
        return AlgorithmResult(name=self.name, score=score, label=label)
