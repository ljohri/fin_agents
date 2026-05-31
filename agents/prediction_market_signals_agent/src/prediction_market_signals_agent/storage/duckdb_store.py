from pathlib import Path

import duckdb

from prediction_market_signals_agent.schemas.market import NormalizedMarket


class DuckDBStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(str(db_path))
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS market_snapshots (
                venue VARCHAR,
                market_id VARCHAR,
                topic VARCHAR,
                implied_probability DOUBLE,
                volume DOUBLE,
                fetched_at TIMESTAMP,
                payload JSON
            )
        """)

    def save_snapshot(self, market: NormalizedMarket) -> None:
        import json

        self._conn.execute(
            "INSERT INTO market_snapshots VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                market.venue,
                market.market_id,
                market.topic,
                market.implied_probability,
                market.volume,
                market.fetched_at,
                json.dumps({"title": market.title}),
            ],
        )

    def get_prior_probability(self, venue: str, market_id: str) -> float | None:
        row = self._conn.execute(
            """
            SELECT implied_probability FROM market_snapshots
            WHERE venue = ? AND market_id = ?
            ORDER BY fetched_at DESC LIMIT 1 OFFSET 1
            """,
            [venue, market_id],
        ).fetchone()
        return float(row[0]) if row and row[0] is not None else None

    def close(self) -> None:
        self._conn.close()
