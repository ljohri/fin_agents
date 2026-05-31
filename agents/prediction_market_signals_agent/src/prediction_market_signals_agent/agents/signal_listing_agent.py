import json
from pathlib import Path

from fin_agents_common.common.ids import new_signal_id
from fin_agents_common.common.time import utc_now
from fin_agents_common.observability.decorators import trace_agent

from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.discovery.market_discovery import discover_markets
from prediction_market_signals_agent.schemas.market import NormalizedMarket


@trace_agent("prediction_market.signal_listing")
async def run_signal_listing(
    *,
    venues: list[str],
    max_per_topic: int,
    settings: AgentSettings,
    offline_markets: list[NormalizedMarket] | None = None,
) -> list[NormalizedMarket]:
    if offline_markets is not None:
        markets = offline_markets
    else:
        markets = await discover_markets(
            venues=venues, max_per_topic=max_per_topic, settings=settings
        )
    settings.intermediate_dir.mkdir(parents=True, exist_ok=True)
    out = settings.intermediate_dir / "market_discovery_raw.json"
    out.write_text(
        json.dumps([m.model_dump(mode="json") for m in markets], indent=2),
        encoding="utf-8",
    )
    return markets
