import json
from pathlib import Path

from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.schemas.signal import PredictionMarketSignal


def write_candidate_signals(signals: list[PredictionMarketSignal], settings: AgentSettings) -> None:
    settings.intermediate_dir.mkdir(parents=True, exist_ok=True)
    json_path = settings.intermediate_dir / "candidate_prediction_market_signals.json"
    md_path = settings.intermediate_dir / "candidate_prediction_market_signals.md"
    json_path.write_text(
        json.dumps([s.model_dump(mode="json") for s in signals], indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Candidate Prediction Market Signals",
        "",
        f"Generated: {signals[0].generated_at.isoformat() if signals else 'n/a'}",
        "",
        "## Summary",
        "",
        "| Signal | Venue | Probability | Strength | Liquidity | Spread | Relevance | Topic |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for s in signals:
        lines.append(
            f"| {s.market_title[:40]} | {s.venue} | {s.implied_probability or 'n/a'} | "
            f"{s.deterministic_label} ({s.deterministic_signal_strength:.2f}) | "
            f"{s.liquidity_score or 'n/a'} | {s.spread or 'n/a'} | "
            f"{s.capital_market_relevance_score or 'n/a'} | {s.topic} |"
        )
    lines.extend(["", "## Signals", ""])
    for i, s in enumerate(signals, 1):
        lines.extend([
            f"### Signal {i}: {s.market_title[:80]}",
            "",
            f"- Venue: {s.venue}",
            f"- Market: {s.market_id}",
            f"- Topic: {s.topic}",
            f"- Current implied probability: {s.implied_probability}",
            f"- Liquidity score: {s.liquidity_score}",
            f"- Relevance score: {s.capital_market_relevance_score}",
            f"- Deterministic signal strength: {s.deterministic_signal_strength} ({s.deterministic_label})",
            f"- Caveats: {', '.join(s.key_caveats) or 'none'}",
            "",
        ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
