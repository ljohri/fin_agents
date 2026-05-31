from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from fin_agents_common.common.time import utc_now
from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.schemas.signal import PredictionMarketSignal
from prediction_market_signals_agent.schemas.user_research import UserResearchContext


def render_report(
    signals: list[PredictionMarketSignal],
    user_context: UserResearchContext | None,
    settings: AgentSettings,
    output_path: Path | None = None,
) -> str:
    tpl_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(tpl_dir), autoescape=select_autoescape())
    template = env.get_template("pred_market_sights.md.j2")

    strong = [s for s in signals if s.deterministic_label == "strong"]
    moderate = [s for s in signals if s.deterministic_label == "moderate"]
    weak = [s for s in signals if s.deterministic_label not in ("strong", "moderate")]

    content = template.render(
        generated_at=utc_now().isoformat(),
        executive_summary=(
            f"Top signals span {len({s.topic for s in signals})} topics across "
            f"{len({s.venue for s in signals})} venues."
        ),
        signals=signals,
        strong_signals=strong,
        moderate_signals=moderate,
        weak_signals=weak,
        user_view_section=(user_context.user_view[:3000] if user_context else "No user view provided."),
    )
    out = output_path or (settings.reports_dir / "pred_market_sights.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return content
