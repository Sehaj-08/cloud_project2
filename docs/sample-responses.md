# AutoScaleLab Phase 1 — sample API responses

The values below are illustrative. `instance_id` and timing values depend on the environment.

## `GET /`

```json
{
  "application": "AutoScaleLab",
  "status": "running",
  "build_version": "0.1.0-dev",
  "instance_id": "local",
  "environment": "development"
}
```

## `GET /health`

```json
{
  "status": "healthy",
  "build_version": "0.1.0-dev",
  "instance_id": "local"
}
```

`GET /healthz` is also supported as an alias for the future ALB health check.

## `GET /compute?iterations=1000`

```json
{
  "status": "success",
  "iterations": 1000,
  "result": 89080666,
  "processing_time_ms": 1.234,
  "instance_id": "local",
  "build_version": "0.1.0-dev"
}
```

The result and timing above are illustrative; run the endpoint to obtain actual values.

## Invalid input

`GET /compute?iterations=0` and values above `MAX_ITERATIONS` return HTTP 422.

## `GET /metrics`

Returns Prometheus text exposition including:

- `autoscalelab_http_requests_total`
- `autoscalelab_http_request_duration_seconds`
- `autoscalelab_compute_operations_total`
- `autoscalelab_compute_duration_seconds`
- `autoscalelab_build_info`

## Request ID and logs

A valid incoming `X-Request-ID` is returned unchanged. If the header is missing or invalid, the application generates a UUID. Each request produces one structured JSON log containing request ID, method, route template, status code, duration, build version, and instance ID.
