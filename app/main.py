"""AutoScaleLab FastAPI workload."""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Annotated

from fastapi import FastAPI, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel

from app.config import settings
from app.logging_config import configure_logging
from app.metrics import (
    COMPUTE_DURATION_SECONDS,
    COMPUTE_OPERATIONS_TOTAL,
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    render_metrics,
)
from app.workload import run_cpu_workload


logger = configure_logging(settings.log_level)
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class RootResponse(BaseModel):
    application: str
    status: str
    build_version: str
    instance_id: str
    environment: str


class HealthResponse(BaseModel):
    status: str
    build_version: str
    instance_id: str


class ComputeResponse(BaseModel):
    status: str
    iterations: int
    result: int
    processing_time_ms: float
    instance_id: str
    build_version: str


app = FastAPI(
    title=settings.app_name,
    description="A bounded CPU workload for demonstrating cloud auto-scaling.",
    version=settings.app_version,
)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    """Attach a request ID, record metrics, and emit one structured log per request."""
    supplied_request_id = request.headers.get("X-Request-ID", "")
    request_id = (
        supplied_request_id
        if _REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
        else str(uuid.uuid4())
    )
    request.state.request_id = request_id

    started_at = time.perf_counter()
    status_code = 500
    response = None

    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        logger.exception(
            "request_exception",
            extra={
                "event_data": {
                    "request_id": request_id,
                    "method": request.method,
                    "route": "unmatched",
                    "status_code": 500,
                    "app_version": settings.app_version,
                }
            },
        )
        raise
    finally:
        duration_seconds = time.perf_counter() - started_at
        route_object = request.scope.get("route")
        route = getattr(route_object, "path", "unmatched")
        method = request.method

        # Scraping /metrics should not inflate the application's own traffic metrics.
        if route != "/metrics":
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                route=route,
                status_code=str(status_code),
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, route=route).observe(
                duration_seconds
            )

        logger.info(
            "http_request",
            extra={
                "event_data": {
                    "request_id": request_id,
                    "method": method,
                    "route": route,
                    "status_code": status_code,
                    "duration_ms": round(duration_seconds * 1000, 3),
                    "app_version": settings.app_version,
                    "instance_id": settings.instance_id,
                }
            },
        )


@app.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    return RootResponse(
        application=settings.app_name,
        status="running",
        build_version=settings.app_version,
        instance_id=settings.instance_id,
        environment=settings.app_env,
    )


@app.get("/health", response_model=HealthResponse)
@app.get("/healthz", response_model=HealthResponse, include_in_schema=False)
async def health() -> HealthResponse:
    """Lightweight process health endpoint for local checks and the future ALB."""
    return HealthResponse(
        status="healthy",
        build_version=settings.app_version,
        instance_id=settings.instance_id,
    )


@app.get("/compute", response_model=ComputeResponse)
def compute(
    iterations: Annotated[
        int,
        Query(
            ge=1,
            le=settings.max_iterations,
            description=f"Number of CPU iterations (maximum {settings.max_iterations:,}).",
        ),
    ] = settings.default_iterations,
) -> ComputeResponse:
    """Run a bounded CPU workload. This is intentionally a synchronous endpoint."""
    started_at = time.perf_counter()
    result = run_cpu_workload(iterations)
    duration_seconds = time.perf_counter() - started_at

    COMPUTE_OPERATIONS_TOTAL.inc()
    COMPUTE_DURATION_SECONDS.observe(duration_seconds)

    return ComputeResponse(
        status="success",
        iterations=iterations,
        result=result,
        processing_time_ms=round(duration_seconds * 1000, 3),
        instance_id=settings.instance_id,
        build_version=settings.app_version,
    )


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    payload, content_type = render_metrics()
    return Response(content=payload, headers={"Content-Type": content_type})
