import json
import os
from datetime import datetime
from typing import Sequence

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult, ConsoleSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    _OTEL_AVAILABLE = True
except Exception:
    _OTEL_AVAILABLE = False

    class SpanExporter:  # type: ignore
        pass

    class SpanExportResult:  # type: ignore
        SUCCESS = 0
        FAILURE = 1


class FileSpanExporter(SpanExporter):
    def __init__(self, path: str):
        self.path = path

    def export(self, spans: Sequence) -> SpanExportResult:
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                for span in spans:
                    data = {
                        "name": span.name,
                        "start_time": span.start_time,
                        "end_time": span.end_time,
                        "attributes": dict(span.attributes),
                    }
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        return None


def setup_tracing(app, service_name: str = "nady-bakery") -> None:
    if not _OTEL_AVAILABLE:
        # OpenTelemetry not installed; skip tracing
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    exporter = None
    file_path = os.getenv("OTEL_EXPORTER_FILE", "")
    if file_path:
        exporter = FileSpanExporter(file_path)
    else:
        exporter = ConsoleSpanExporter()

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    FastAPIInstrumentor.instrument_app(app)

    # Write a small marker for observability setup (optional)
    marker = os.getenv("OTEL_MARKER_FILE", "")
    if marker:
        with open(marker, "a", encoding="utf-8") as f:
            f.write(f"tracing_enabled {datetime.utcnow().isoformat()}Z\n")
