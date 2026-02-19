"""
Prometheus-compatible metrics for the Monolith runtime.

Exposes a minimal pull-based HTTP /metrics endpoint (text/plain exposition
format) on MONOLITH_METRICS_PORT (default 9100). If the port is 0, metrics
are tracked in-process only (useful for tests).

Counters and gauges are process-local (per worker). The Supervisor's metrics
port (if enabled) aggregates supervisor-level counters only.

Metric naming convention:  monolith_<subsystem>_<name>[_total]

Usage:
    from monolith.metrics import METRICS
    METRICS.tasks_submitted.inc()
    METRICS.tasks_failed.inc()
    METRICS.memory_used_bytes.set(pool.used_bytes)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from typing import Dict


class Counter:
    """Monotonically increasing counter."""

    def __init__(self, name: str, help_text: str) -> None:
        self.name = name
        self.help_text = help_text
        self._value: float = 0.0
        self._lock = threading.Lock()

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    @property
    def value(self) -> float:
        return self._value

    def exposition(self) -> str:
        return (
            f"# HELP {self.name} {self.help_text}\n"
            f"# TYPE {self.name} counter\n"
            f"{self.name}_total {self._value}\n"
        )


class Gauge:
    """Arbitrarily settable gauge."""

    def __init__(self, name: str, help_text: str) -> None:
        self.name = name
        self.help_text = help_text
        self._value: float = 0.0
        self._lock = threading.Lock()

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    @property
    def value(self) -> float:
        return self._value

    def exposition(self) -> str:
        return (
            f"# HELP {self.name} {self.help_text}\n"
            f"# TYPE {self.name} gauge\n"
            f"{self.name} {self._value}\n"
        )


@dataclass
class _MetricsRegistry:
    """All process-level metrics."""

    tasks_submitted: Counter = field(
        default_factory=lambda: Counter(
            "monolith_tasks_submitted", "Total tasks submitted to this worker"
        )
    )
    tasks_completed: Counter = field(
        default_factory=lambda: Counter(
            "monolith_tasks_completed", "Total tasks completed successfully"
        )
    )
    tasks_failed: Counter = field(
        default_factory=lambda: Counter(
            "monolith_tasks_failed", "Total tasks that ended in FAILED state"
        )
    )
    tasks_cancelled: Counter = field(
        default_factory=lambda: Counter(
            "monolith_tasks_cancelled", "Total tasks cancelled"
        )
    )
    scheduler_quantum_overruns: Counter = field(
        default_factory=lambda: Counter(
            "monolith_scheduler_quantum_overruns",
            "Number of task quanta that exceeded quantum_ms",
        )
    )
    memory_used_bytes: Gauge = field(
        default_factory=lambda: Gauge(
            "monolith_memory_used_bytes",
            "Current logical memory pool usage in bytes",
        )
    )
    memory_region_count: Gauge = field(
        default_factory=lambda: Gauge(
            "monolith_memory_region_count",
            "Number of active logical memory regions",
        )
    )
    worker_queue_depth: Gauge = field(
        default_factory=lambda: Gauge(
            "monolith_worker_queue_depth",
            "Current number of tasks in the worker's run queue",
        )
    )

    def exposition_text(self) -> str:
        parts = [
            self.tasks_submitted.exposition(),
            self.tasks_completed.exposition(),
            self.tasks_failed.exposition(),
            self.tasks_cancelled.exposition(),
            self.scheduler_quantum_overruns.exposition(),
            self.memory_used_bytes.exposition(),
            self.memory_region_count.exposition(),
            self.worker_queue_depth.exposition(),
        ]
        return "\n".join(parts)


# Module-level singleton — one per process
METRICS = _MetricsRegistry()


class _MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/metrics":
            body = METRICS.exposition_text().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:  # suppress access logs
        pass


def start_metrics_server(port: int) -> None:
    """Start the Prometheus /metrics HTTP server in a daemon thread.

    If port == 0, this is a no-op (metrics are still tracked in memory).
    """
    if port == 0:
        return
    server = HTTPServer(("0.0.0.0", port), _MetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
