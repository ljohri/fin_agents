import json
import re
from typing import Any

from fin_agents_common.common.errors import StructuredOutputError


def parse_json_response(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise StructuredOutputError(f"Invalid JSON from LLM: {exc}") from exc
    if not isinstance(data, dict):
        raise StructuredOutputError("Expected JSON object from LLM")
    return data
