# Local baseline benchmark

Run the application locally, then collect a baseline before Docker or AWS deployment.

```bash
python scripts/benchmark.py --url http://127.0.0.1:8000 --duration 30 --users 5 --iterations 250000
```

Repeat with a modest concurrency increase, for example `--users 10`, then `--users 20`. Do not jump directly to thousands of users on a laptop.

Record the actual outputs here:

| Date | Users | Iterations | Requests/sec | P50 ms | P95 ms | P99 ms | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| TODO | 5 | 250000 | TODO | TODO | TODO | TODO | TODO |
| TODO | 10 | 250000 | TODO | TODO | TODO | TODO | TODO |

The benchmark is a lightweight baseline tool. Locust will be used for later controlled stress tests. Results depend on your CPU, Python version, operating system, and concurrency settings.
