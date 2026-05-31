from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from fin_agents_common.observability.otel import get_tracer, set_span_attributes

F = TypeVar("F", bound=Callable[..., Any])


def _trace(name: str, extra_attrs: dict[str, str] | None = None) -> Callable[[F], F]:
    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer("fin_agents")
            attrs = {"agent_name": name, **(extra_attrs or {})}
            with tracer.start_as_current_span(name) as span:
                set_span_attributes(span, attrs)
                return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def trace_agent(name: str) -> Callable[[F], F]:
    return _trace(name, {"pipeline_stage": "agent"})


def trace_algorithm(name: str) -> Callable[[F], F]:
    return _trace(f"algorithm.{name}", {"algorithm_name": name, "pipeline_stage": "algorithm"})


def trace_llm_call(name: str) -> Callable[[F], F]:
    return _trace(f"llm.{name}", {"pipeline_stage": "llm"})
