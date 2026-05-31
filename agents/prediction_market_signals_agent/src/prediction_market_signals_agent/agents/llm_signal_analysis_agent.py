import json

from fin_agents_common.common.config import load_yaml_config
from fin_agents_common.llm.litellm_client import LiteLLMClient
from fin_agents_common.llm.model_policy import ModelPolicy
from fin_agents_common.llm.prompts import load_prompt
from fin_agents_common.observability.decorators import trace_llm_call

from prediction_market_signals_agent.config import AgentSettings
from prediction_market_signals_agent.schemas.signal import PredictionMarketSignal
from prediction_market_signals_agent.schemas.user_research import UserResearchContext


def select_signals_for_llm(
    signals: list[PredictionMarketSignal], settings: AgentSettings
) -> list[PredictionMarketSignal]:
    cfg = load_yaml_config(settings.scoring_config).get("llm_analysis", {})
    min_strength = cfg.get("analyze_if", {}).get("deterministic_signal_strength_min", 0.45)
    min_rel = cfg.get("analyze_if", {}).get("capital_market_relevance_min", 0.50)
    min_liq = cfg.get("skip_if_liquidity_score_below", 0.20)
    top_n = cfg.get("always_analyze_top_n", 20)

    eligible = [
        s
        for s in signals
        if (s.deterministic_signal_strength or 0) >= min_strength
        and (s.capital_market_relevance_score or 0) >= min_rel
        and (s.liquidity_score or 0) >= min_liq
    ]
    eligible.sort(key=lambda s: s.deterministic_signal_strength or 0, reverse=True)
    if len(eligible) < top_n:
        rest = [s for s in signals if s not in eligible]
        rest.sort(key=lambda s: s.deterministic_signal_strength or 0, reverse=True)
        eligible.extend(rest[: top_n - len(eligible)])
    return eligible[:top_n]


@trace_llm_call("prediction_market.signal_analysis")
def analyze_signals_with_llm(
    signals: list[PredictionMarketSignal],
    settings: AgentSettings,
    user_context: UserResearchContext | None = None,
) -> list[PredictionMarketSignal]:
    llm_cfg = load_yaml_config(settings.llm_config)
    policy = ModelPolicy.from_config(llm_cfg)
    client = LiteLLMClient(policy=policy)
    prompt_path = settings.agent_root / "docs/prompts/prediction_market_signal_analysis.md"
    system_prompt = load_prompt(prompt_path)

    selected = select_signals_for_llm(signals, settings)
    selected_ids = {s.signal_id for s in selected}

    for signal in signals:
        if signal.signal_id not in selected_ids:
            continue
        user_prompt = json.dumps(
            {
                "signal": signal.model_dump(mode="json"),
                "user_research": user_context.model_dump() if user_context else {},
            },
            indent=2,
        )
        try:
            result = client.complete_json(system_prompt=system_prompt, user_prompt=user_prompt)
            signal.llm_signal_strength = result.get("llm_signal_strength")
            signal.llm_analysis_summary = result.get("summary", "")
            signal.algorithm_details["llm_analysis"] = result
        except Exception as exc:
            signal.key_caveats.append(f"LLM analysis failed: {exc}")

    settings.intermediate_dir.mkdir(parents=True, exist_ok=True)
    out = settings.intermediate_dir / "llm_signal_analysis.json"
    out.write_text(
        json.dumps(
            [s.model_dump(mode="json") for s in signals if s.signal_id in selected_ids],
            indent=2,
        ),
        encoding="utf-8",
    )
    return signals
