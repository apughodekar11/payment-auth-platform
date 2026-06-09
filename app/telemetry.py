from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.config import settings


def setup_telemetry(app) -> None:
    if not settings.otel_enabled:
        return  

    # A Resource labels every span with what service produced it, so traces from
    # this app are identifiable in the backend.
    resource = Resource.create({"service.name": settings.service_name})

    provider = TracerProvider(resource=resource)

    # OTLP/HTTP exporter -> Headers carry the auth token Dynatrace needs.
    exporter = OTLPSpanExporter(
        endpoint=settings.otel_endpoint,
        headers=_parse_headers(settings.otel_headers),
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)


def _parse_headers(raw: str) -> dict:
    # Stored as a single string in config; split into a dict here.
    headers = {}
    for pair in raw.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            headers[key.strip()] = value.strip()
    return headers