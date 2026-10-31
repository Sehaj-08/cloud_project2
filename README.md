# AutoScaleLab

AutoScaleLab is an AWS-based self-scaling and self-healing web application infrastructure. The FastAPI workload is intentionally measurable and CPU-intensive so that later phases can demonstrate EC2 Auto Scaling, Application Load Balancing, monitoring, and recovery under controlled traffic.

## Phase 1 scope

This phase builds and validates the application locally. It does not create AWS resources.

- `GET /` — application, build version, environment, and instance ID.
- `GET /health` and `GET /healthz` — lightweight health checks.
- `GET /compute?iterations=250000` — bounded deterministic CPU work.
- `GET /metrics` — Prometheus metrics.
- JSON request logs — request ID, method, route, status, duration, app version, and instance ID.

## Requirements

- Python 3.11 or newer
- pip

## Setup

```bash
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\\Scripts\\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env` and adjust values if required. The application loads `.env` automatically for local development. Keep `.env` out of Git; `.gitignore` already excludes it.

Run the application:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/compute?iterations=250000
- http://127.0.0.1:8000/metrics
- http://127.0.0.1:8000/docs

## Configuration

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `AutoScaleLab` | Application name |
| `APP_ENV` | `development` | Environment label |
| `APP_VERSION` | `0.1.0-dev` | Build version |
| `INSTANCE_ID` | `local` | Instance identifier; later populated per EC2 instance |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PORT` | `8000` | Documented application port |
| `DEFAULT_ITERATIONS` | `250000` | Default CPU workload |
| `MAX_ITERATIONS` | `2000000` | Configurable request limit; hard cap is 10,000,000 |

`DEFAULT_ITERATIONS` must not exceed `MAX_ITERATIONS`. The hard cap prevents configuration from accidentally enabling unbounded CPU work.

## Tests

```bash
pytest
```

## Local baseline benchmark

Start the app in one terminal. In another terminal:

```bash
python scripts/benchmark.py --url http://127.0.0.1:8000 --duration 30 --users 5 --iterations 250000
```

Record actual measurements in `docs/baseline-benchmark.md`. Increase concurrency gradually.

## Locust scenario for later phases

```bash
locust -f loadtest/locustfile.py --host http://127.0.0.1:8000
```

Start with a small user count and ramp gradually. Do not use this against systems you do not own or have permission to test.

## Prometheus local scrape configuration

`monitoring/prometheus.yml` is a starter configuration for running Prometheus in Docker on a machine where `host.docker.internal` resolves to the host. On Linux, configure the host-gateway mapping or use the host's reachable address.

## Notes

- The `/compute` endpoint is intentionally synchronous and CPU-intensive for controlled experiments.
- The workload is bounded by `MAX_ITERATIONS` and a hard cap.
- Prometheus labels use route templates, not arbitrary URL paths, to avoid high-cardinality metrics.
- `/metrics` scrapes are excluded from HTTP request counters to avoid scrape noise.
- No AWS resources are provisioned in Phase 1.
