from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from app.config import get_config

try:
    from opentelemetry import metrics
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource

    _otel_available = True
except ImportError:
    _otel_available = False

_meter: Any = None
_eval_run_counter: Any = None
_eval_score_gauge: Any = None
_eval_latency_histogram: Any = None
_chaos_injection_counter: Any = None
_eval_failure_counter: Any = None


def init_metrics() -> None:
    global _meter, _eval_run_counter, _eval_score_gauge, _eval_latency_histogram, _chaos_injection_counter, _eval_failure_counter

    if not _otel_available:
        return

    config = get_config()
    resource = Resource.create({SERVICE_NAME: config.otel_service_name})
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=config.otel_exporter_otlp_endpoint),
        export_interval_millis=15_000,
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)
    _meter = metrics.get_meter(config.otel_service_name)

    _eval_run_counter = _meter.create_counter(
        "snt_evaluation_runs_total", description="Total number of evaluation runs",
    )
    _eval_score_gauge = _meter.create_gauge(
        "snt_aggregate_score", description="Evaluation aggregate score",
    )
    _eval_latency_histogram = _meter.create_histogram(
        "snt_evaluation_latency_ms", description="Per-turn latency in ms", unit="ms",
    )
    _chaos_injection_counter = _meter.create_counter(
        "snt_chaos_injections_total", description="Total chaos injection events by type",
    )
    _eval_failure_counter = _meter.create_counter(
        "snt_evaluation_failures_total", description="Total evaluation failures",
    )


def record_eval_run(score: float, total_sessions: int) -> None:
    if _eval_run_counter:
        _eval_run_counter.add(1, {"total_sessions": str(total_sessions)})
    if _eval_score_gauge:
        _eval_score_gauge.set(score)


def record_turn_latency(latency_ms: float, persona: str) -> None:
    if _eval_latency_histogram:
        _eval_latency_histogram.record(latency_ms, {"persona": persona})


def record_chaos_injection(injection_type: str) -> None:
    if _chaos_injection_counter:
        _chaos_injection_counter.add(1, {"type": injection_type})


def record_eval_failure(reason: str) -> None:
    if _eval_failure_counter:
        _eval_failure_counter.add(1, {"reason": reason})


def shutdown_metrics() -> None:
    if _otel_available:
        try:
            provider = metrics.get_meter_provider()
            provider.shutdown()
        except Exception:
            pass
