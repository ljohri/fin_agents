class FinAgentsError(Exception):
    """Base error for fin_agents."""


class ConfigurationError(FinAgentsError):
    """Invalid or missing configuration."""


class LLMError(FinAgentsError):
    """LLM call failed."""


class StructuredOutputError(FinAgentsError):
    """LLM returned invalid structured output."""
