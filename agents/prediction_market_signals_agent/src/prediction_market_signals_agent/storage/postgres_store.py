import os
from typing import Any


class PostgresStore:
    """Optional persistence to shared Docker Postgres."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://fin_agents:fin_agents@localhost:5432/fin_agents",
        )
        self._available = False
        try:
            import psycopg2  # noqa: F401

            self._available = True
        except ImportError:
            pass

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        if not self._available:
            return
        import psycopg2

        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
            conn.commit()
