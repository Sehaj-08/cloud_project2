#!/usr/bin/env python3
"""Small local baseline benchmark using only the Python standard library.

Example:
  python scripts/benchmark.py --url http://127.0.0.1:8000 --duration 30 --users 10 --iterations 250000

This is a lightweight baseline tool, not a replacement for distributed Locust tests.
"""

from __future__ import annotations

import argparse
import json
import math
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Any


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(quantile * len(ordered)) - 1))
    return round(ordered[index], 3)


def fetch(url: str, timeout: float) -> tuple[bool, float, int | None]:
    started = time.perf_counter()
    request = urllib.request.Request(url, headers={"User-Agent": "AutoScaleLab-Benchmark/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
            elapsed_ms = (time.perf_counter() - started) * 1000
            return 200 <= response.status < 400, elapsed_ms, response.status
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return False, elapsed_ms, exc.code
    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return False, elapsed_ms, None


def worker(
    url: str,
    deadline: float,
    timeout: float,
    stop_event: threading.Event,
    results: list[tuple[bool, float, int | None]],
    lock: threading.Lock,
) -> None:
    local_results: list[tuple[bool, float, int | None]] = []
    while time.perf_counter() < deadline and not stop_event.is_set():
        local_results.append(fetch(url, timeout))
    with lock:
        results.extend(local_results)


def main() -> int:
    parser = argparse.ArgumentParser(description="AutoScaleLab local baseline benchmark")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base application URL")
    parser.add_argument("--duration", type=int, default=30, help="Test duration in seconds")
    parser.add_argument("--users", type=int, default=10, help="Concurrent worker threads")
    parser.add_argument("--iterations", type=int, default=250_000, help="/compute iterations")
    parser.add_argument("--timeout", type=float, default=15.0, help="Per-request timeout")
    args = parser.parse_args()

    if args.duration < 1 or args.duration > 600:
        parser.error("--duration must be between 1 and 600 seconds")
    if args.users < 1 or args.users > 100:
        parser.error("--users must be between 1 and 100")
    if args.iterations < 1 or args.iterations > 2_000_000:
        parser.error("--iterations must be between 1 and 2,000,000")

    health_ok, _, health_status = fetch(f"{args.url.rstrip('/')}/health", args.timeout)
    if not health_ok:
        parser.error(f"Health check failed (HTTP status: {health_status}); start the app first")

    target = f"{args.url.rstrip('/')}/compute?iterations={args.iterations}"
    results: list[tuple[bool, float, int | None]] = []
    lock = threading.Lock()
    stop_event = threading.Event()
    started = time.perf_counter()
    deadline = started + args.duration

    with ThreadPoolExecutor(max_workers=args.users) as executor:
        futures = [
            executor.submit(worker, target, deadline, args.timeout, stop_event, results, lock)
            for _ in range(args.users)
        ]
        try:
            for future in futures:
                future.result()
        except KeyboardInterrupt:
            stop_event.set()
            raise

    elapsed = time.perf_counter() - started
    latencies = [item[1] for item in results]
    successes = sum(1 for item in results if item[0])
    failures = len(results) - successes
    report: dict[str, Any] = {
        "target": target,
        "duration_seconds": round(elapsed, 3),
        "concurrency": args.users,
        "iterations_per_request": args.iterations,
        "total_requests": len(results),
        "successful_requests": successes,
        "failed_requests": failures,
        "requests_per_second": round(len(results) / elapsed, 3) if elapsed else 0,
        "latency_ms": {
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
            "p99": percentile(latencies, 0.99),
            "max": round(max(latencies), 3) if latencies else None,
        },
    }
    print(json.dumps(report, indent=2))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
