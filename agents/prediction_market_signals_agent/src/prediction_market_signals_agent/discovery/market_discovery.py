import asyncio

from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.connectors import KalshiConnector, PolymarketConnector
from prediction_market_signals_agent.discovery.query_builder import build_search_queries
from prediction_market_signals_agent.discovery.topic_taxonomy import load_topics
from prediction_market_signals_agent.schemas.market import NormalizedMarket


async def discover_markets(
    *,
    venues: list[str],
    max_per_topic: int = 25,
    settings: AgentSettings | None = None,
) -> list[NormalizedMarket]:
    s = settings or AgentSettings()
    topics = load_topics(s)
    connectors = []
    if "kalshi" in venues:
        connectors.append(KalshiConnector(s))
    if "polymarket" in venues:
        connectors.append(PolymarketConnector(s))

    seen: set[tuple[str, str]] = set()
    markets: list[NormalizedMarket] = []

    for category, topic_list in topics.items():
        for topic in topic_list:
            for query in build_search_queries(topic, category):
                for conn in connectors:
                    found = await conn.search_markets(query, limit=max_per_topic)
                    for m in found:
                        key = (m.venue, m.market_id)
                        if key not in seen:
                            seen.add(key)
                            m.topic = topic
                            markets.append(m)
    return markets
