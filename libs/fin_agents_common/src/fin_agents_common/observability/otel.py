from __future__ import annotations

import os
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

_tracer: trace.Tracer | None = None
_initialized = False


def init_otel(
    *,
    service_name: str = "fin_agents",
    endpoint: str | None = None,
    enabled: bool = True,
    console_fallback: bool = True,
) -> trace.Tracer:
    global _tracer, _initialized
    if _initialized:
        return get_tracer(service_name)

    if not enabled:
        _tracer = trace.get_tracer(service_name)
        _initialized = True
        return _tracer

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    endpoint = endpoint or os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces"
    )
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    except Exception:
        if console_fallback:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name)
    _initialized = True
    return _tracer


def get_tracer(name: str = "fin_agents") -> trace.Tracer:
    global _tracer
    if _tracer is None:
        return init_otel(service_name=name, enabled=False)
    return trace.get_tracer(name)


def set_span_attributes(span: Any, attributes: dict[str, Any]) -> None:
    for key, value in attributes.items():
        if value is not None:
            span.set_attribute(f"fin_agents.{key}", str(value))
