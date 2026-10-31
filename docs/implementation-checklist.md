# AutoScaleLab implementation checklist

## Phase 1 — Local FastAPI workload

- [ ] `GET /` returns application, build version, and instance ID.
- [ ] `GET /health` and `/healthz` return healthy status.
- [ ] `GET /compute` runs bounded configurable CPU work.
- [ ] Invalid and over-limit workload values return HTTP 422.
- [ ] Prometheus metrics are exposed at `/metrics`.
- [ ] Request count, status, and duration histogram are instrumented.
- [ ] Compute duration is instrumented.
- [ ] Structured JSON logs include request ID, route, status, duration, and app version.
- [ ] Unit/API tests pass.
- [ ] Local benchmark is run and actual results are recorded.

## Later phases

- [ ] Phase 2 — Docker containerization.
- [ ] Phase 3 — Terraform AWS infrastructure.
- [ ] Phase 4 — Deploy FastAPI to EC2 behind an ALB.
- [ ] Phase 5 — Configure EC2 Auto Scaling and self-healing.
- [ ] Phase 6 — Prometheus and Grafana dashboards.
- [ ] Phase 7 — GitHub Actions CI/CD.
- [ ] Phase 8 — Locust stress testing.
- [ ] Phase 9 — Instance failure and recovery demonstration.
- [ ] Phase 10 — Performance analysis and final documentation.
