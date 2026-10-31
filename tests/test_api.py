from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.workload import run_cpu_workload
from app.config import settings


client = TestClient(app)


def test_root_returns_build_and_instance_information() -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["application"] == "AutoScaleLab"
    assert body["status"] == "running"
    assert body["build_version"] == settings.app_version
    assert body["instance_id"] == settings.instance_id


def test_health_and_healthz_are_healthy() -> None:
    for path in ("/health", "/healthz"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_compute_returns_deterministic_result_and_timing() -> None:
    response = client.get("/compute", params={"iterations": 1000})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["iterations"] == 1000
    assert body["result"] == run_cpu_workload(1000)
    assert body["processing_time_ms"] >= 0
    assert body["instance_id"] == settings.instance_id
    assert body["build_version"] == settings.app_version


def test_compute_uses_configured_default_iterations() -> None:
    response = client.get("/compute")
    assert response.status_code == 200
    assert response.json()["iterations"] == settings.default_iterations


def test_compute_rejects_zero_iterations() -> None:
    response = client.get("/compute", params={"iterations": 0})
    assert response.status_code == 422


def test_compute_rejects_workload_above_configured_limit() -> None:
    response = client.get(
        "/compute", params={"iterations": settings.max_iterations + 1}
    )
    assert response.status_code == 422


def test_compute_rejects_non_integer_input() -> None:
    response = client.get("/compute", params={"iterations": "not-a-number"})
    assert response.status_code == 422


def test_request_id_is_returned_when_valid() -> None:
    request_id = "test-request-123"
    response = client.get("/health", headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_invalid_request_id_is_replaced() -> None:
    response = client.get("/health", headers={"X-Request-ID": "bad request id"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "bad request id"
    assert len(response.headers["X-Request-ID"]) == 36


def test_metrics_endpoint_exposes_application_metrics() -> None:
    # Generate observations before scraping so histogram and counter series exist.
    client.get("/compute", params={"iterations": 1000})
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "autoscalelab_http_requests_total" in response.text
    assert "autoscalelab_http_request_duration_seconds" in response.text
    assert "autoscalelab_compute_operations_total" in response.text
    assert "autoscalelab_compute_duration_seconds" in response.text
    assert "autoscalelab_build_info" in response.text


def test_unknown_route_returns_404() -> None:
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
