import uuid


def new_signal_id(prefix: str = "sig") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
