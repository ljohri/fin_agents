from pathlib import Path

from prediction_market_signals_agent.schemas.signal import PredictionMarketSignal


class ParquetStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_signals(self, signals: list[PredictionMarketSignal], name: str = "signals") -> Path:
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            path = self.base_dir / f"{name}.json"
            path.write_text(
                "[" + ",".join(s.model_dump_json() for s in signals) + "]",
                encoding="utf-8",
            )
            return path
        rows = [s.model_dump(mode="json") for s in signals]
        table = pa.Table.from_pylist(rows)
        path = self.base_dir / f"{name}.parquet"
        pq.write_table(table, path)
        return path
