from prediction_market_signals_agent.algorithms.base import AlgorithmResult, SignalAlgorithm


class AlgorithmRegistry:
    def __init__(self) -> None:
        self._algorithms: dict[str, SignalAlgorithm] = {}

    def register(self, algorithm: SignalAlgorithm) -> None:
        self._algorithms[algorithm.name] = algorithm

    def run_all(self, context: dict) -> dict[str, AlgorithmResult]:
        return {name: algo.run(context) for name, algo in self._algorithms.items()}
