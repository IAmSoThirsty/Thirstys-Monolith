"""
Health check endpoint for the Monolith supervisor.

Provides a simple HTTP server that responds to:
  GET /healthz  — liveness (is the process alive?)
  GET /readyz   — readiness (are workers running?)

Used by Kubernetes liveness/readiness probes and systemd watchdog.

Status codes:
  200 OK      — healthy / ready
  503 Service Unavailable — not ready (workers not yet started)
"""

from __future__ import annotations
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
from typing import Callable


class HealthServer:
    """HTTP health check server, runs in a daemon thread."""

    def __init__(
        self,
        port: int,
        readiness_check: Callable[[], bool],
    ) -> None:
        """
        Args:
            port: Port to listen on (0 = disabled).
            readiness_check: Callable returning True when the process is ready
                to accept work (e.g., all workers started).
        """
        self._port = port
        self._readiness_check = readiness_check
        self._start_time = time.time()

    def start(self) -> None:
        if self._port == 0:
            return
        server = HTTPServer(
            ("0.0.0.0", self._port),
            self._make_handler(),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        start_time = self._start_time
        readiness_check = self._readiness_check

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/healthz":
                    body = json.dumps({
                        "status": "ok",
                        "uptime_seconds": round(time.time() - start_time, 1),
                    }).encode()
                    self._respond(200, body)
                elif self.path == "/readyz":
                    ready = readiness_check()
                    code = 200 if ready else 503
                    body = json.dumps({"ready": ready}).encode()
                    self._respond(code, body)
                else:
                    self.send_response(404)
                    self.end_headers()

            def _respond(self, code: int, body: bytes) -> None:
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, fmt: str, *args: object) -> None:
                pass  # suppress access log spam

        return _Handler
