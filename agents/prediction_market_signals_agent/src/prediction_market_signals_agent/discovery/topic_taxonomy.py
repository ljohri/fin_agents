from fin_agents_common.common.config import load_yaml_config
from prediction_market_signals_agent.config import AgentSettings


def load_topics(settings: AgentSettings | None = None) -> dict[str, list[str]]:
    s = settings or AgentSettings()
    return load_yaml_config(s.topics_config)
