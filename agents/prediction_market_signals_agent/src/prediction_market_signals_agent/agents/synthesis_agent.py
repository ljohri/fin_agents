from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.schemas.signal import PredictionMarketSignal
from prediction_market_signals_agent.schemas.user_research import UserResearchContext


def build_draft_report(
    signals: list[PredictionMarketSignal],
    user_context: UserResearchContext | None,
    settings: AgentSettings,
) -> str:
    lines = ["# Prediction Market Sights (Draft)", ""]
    strong = [s for s in signals if s.deterministic_label == "strong"]
    moderate = [s for s in signals if s.deterministic_label == "moderate"]
    weak = [s for s in signals if s.deterministic_label in ("weak", "noisy", None)]

    lines.append("## Executive Summary")
    lines.append(
        f"Identified {len(signals)} candidate signals: {len(strong)} strong, "
        f"{len(moderate)} moderate, {len(weak)} weak/noisy."
    )
    lines.append("")
    if user_context and user_context.user_view:
        lines.extend(["## User View vs Prediction Markets", "", user_context.user_view[:2000], ""])
    path = settings.intermediate_dir / "pred_market_sights_draft.md"
    settings.intermediate_dir.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path.read_text(encoding="utf-8")
