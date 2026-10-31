"""Prometheus metrics with bounded label cardinality."""

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

from app.config import settings


REGISTRY = CollectorRegistry(auto_describe=True)

HTTP_REQUESTS_TOTAL = Counter(
    "autoscalelab_http_requests_total",
    "Total HTTP requests handled by the application (excluding /metrics scrapes).",
    labelnames=("method", "route", "status_code"),
    registry=REGISTRY,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "autoscalelab_http_request_duration_seconds",
    "HTTP request duration in seconds, excluding /metrics scrapes.",
    labelnames=("method", "route"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=REGISTRY,
)

COMPUTE_OPERATIONS_TOTAL = Counter(
    "autoscalelab_compute_operations_total",
    "Number of completed CPU workload operations.",
    registry=REGISTRY,
)

COMPUTE_DURATION_SECONDS = Histogram(
    "autoscalelab_compute_duration_seconds",
    "CPU workload execution duration in seconds.",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=REGISTRY,
)

BUILD_INFO = Gauge(
    "autoscalelab_build_info",
    "Build information; the version is exposed as a label and the value is always 1.",
    labelnames=("version", "environment"),
    registry=REGISTRY,
)
BUILD_INFO.labels(version=settings.app_version, environment=settings.app_env).set(1)


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
