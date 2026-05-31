import hashlib
import json
from pathlib import Path


class RawPayloadStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, venue: str, key: str, payload: dict) -> str:
        ref = hashlib.sha256(f"{venue}:{key}".encode()).hexdigest()[:16]
        path = self.base_dir / venue / f"{ref}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, default=str), encoding="utf-8")
        return str(path)
