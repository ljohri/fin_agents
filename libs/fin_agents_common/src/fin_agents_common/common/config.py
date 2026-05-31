from pathlib import Path
from typing import Any

import yaml

from fin_agents_common.common.errors import ConfigurationError


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ConfigurationError(f"Config file not found: {p}")
    with p.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}
