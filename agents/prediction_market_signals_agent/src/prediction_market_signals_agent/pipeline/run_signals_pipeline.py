import asyncio
import json
from pathlib import Path

from fin_agents_common.common.config import load_yaml_config
from fin_agents_common.observability.otel import init_otel

from prediction_market_signals_agent.agents.candidate_writer import write_candidate_signals
from prediction_market_signals_agent.agents.deterministic_scoring_agent import score_markets
from prediction_market_signals_agent.agents.llm_signal_analysis_agent import analyze_signals_with_llm
from prediction_market_signals_agent.agents.signal_listing_agent import run_signal_listing
from prediction_market_signals_agent.agents.synthesis_agent import build_draft_report
from prediction_market_signals_agent.agents.user_research_agent import load_user_research
from prediction_market_signals_agent.config import AgentSettings, get_settings
from prediction_market_signals_agent.pipeline.state import PipelineState
from prediction_market_signals_agent.reporting.markdown_renderer import render_report
from prediction_market_signals_agent.schemas.market import NormalizedMarket


def load_offline_markets(settings: AgentSettings) -> list[NormalizedMarket]:
    fixture = (
        Path(__file__).resolve().parents[3]
        / "tests"
        / "fixtures"
        / "prediction_markets"
        / "offline_markets.json"
    )
    if not fixture.exists():
        return []
    data = json.loads(fixture.read_text(encoding="utf-8"))
    return [NormalizedMarket.model_validate(m) for m in data]


async def run_pipeline(
    *,
    venues: list[str],
    max_markets_per_topic: int,
    settings: AgentSettings | None = None,
    state: PipelineState | None = None,
    output: Path | None = None,
    observability_enabled: bool = False,
) -> PipelineState:
    s = settings or get_settings()
    st = state or PipelineState()
    s.intermediate_dir.mkdir(parents=True, exist_ok=True)
    s.reports_dir.mkdir(parents=True, exist_ok=True)

    if observability_enabled:
        obs = load_yaml_config(s.observability_config).get("observability", {})
        init_otel(
            service_name=obs.get("otel", {}).get("service_name", "fin_agents.prediction_markets"),
            endpoint=obs.get("otel", {}).get("endpoint"),
            enabled=obs.get("otel", {}).get("enabled", True),
        )

    offline_markets = load_offline_markets(s) if st.offline_demo else None
    st.markets = await run_signal_listing(
        venues=venues,
        max_per_topic=max_markets_per_topic,
        settings=s,
        offline_markets=offline_markets,
    )

    norm_path = s.intermediate_dir / "normalized_markets.json"
    norm_path.write_text(
        json.dumps([m.model_dump(mode="json") for m in st.markets], indent=2),
        encoding="utf-8",
    )

    st.signals = score_markets(st.markets, s)
    write_candidate_signals(st.signals, s)

    if not st.skip_user_research:
        st.user_research = load_user_research(s)

    if not st.skip_llm:
        st.signals = analyze_signals_with_llm(st.signals, s, st.user_research)

    build_draft_report(st.signals, st.user_research, s)
    render_report(st.signals, st.user_research, s, output_path=output)
    st.report_path = str(output or s.reports_dir / "pred_market_sights.md")
    return st


def run_pipeline_sync(**kwargs) -> PipelineState:
    return asyncio.run(run_pipeline(**kwargs))
