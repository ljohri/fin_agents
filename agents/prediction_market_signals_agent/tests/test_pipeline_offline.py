from pathlib import Path

from prediction_market_signals_agent.config import get_settings
from prediction_market_signals_agent.pipeline.run_signals_pipeline import run_pipeline_sync
from prediction_market_signals_agent.pipeline.state import PipelineState


def test_offline_demo_pipeline(tmp_path):
    settings = get_settings()
    settings.intermediate_dir = tmp_path / "intermediate"
    settings.reports_dir = tmp_path / "reports"
    settings.snapshots_dir = tmp_path / "snapshots"
    settings.user_research_dir = Path(__file__).resolve().parents[1] / "data" / "user_research"
    output = tmp_path / "reports" / "pred_market_sights.md"

    state = run_pipeline_sync(
        venues=["kalshi", "polymarket"],
        max_markets_per_topic=5,
        settings=settings,
        state=PipelineState(offline_demo=True, skip_llm=True),
        output=output,
    )

    assert output.exists()
    assert len(state.signals) >= 1
    assert (settings.intermediate_dir / "candidate_prediction_market_signals.json").exists()
    content = output.read_text(encoding="utf-8")
    assert "Prediction Market Sights" in content
