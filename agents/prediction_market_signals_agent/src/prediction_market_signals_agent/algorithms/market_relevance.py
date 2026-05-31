from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm

HIGH_RELEVANCE_TERMS = [
    "fed", "interest rate", "inflation", "cpi", "pce", "recession",
    "unemployment", "tariff", "oil", "debt ceiling", "government shutdown",
    "election", "tax", "sanctions", "china", "war", "bank", "gdp", "treasury",
]


class MarketRelevanceAlgorithm(SignalAlgorithm):
    name = "capital_market_relevance"

    def run(self, context: dict) -> AlgorithmResult:
        market = context["market"]
        text = f"{market.title} {market.question} {market.topic or ''}".lower()
        hits = sum(1 for t in HIGH_RELEVANCE_TERMS if t in text)
        score = max(0.0, min(1.0, hits / 4))
        return AlgorithmResult(
            name=self.name,
            score=score,
            label="high" if score >= 0.75 else "medium" if score >= 0.5 else "low",
            details={"term_hits": hits},
        )
