from __future__ import annotations
import os
import signal
import time
from multiprocessing import Process, Queue, get_context
from typing import List, Optional

from .config import MonolithConfig, load_config
from .health import HealthServer
from .logging import configure_logging, get_logger
from .metrics import METRICS, start_metrics_server
from .worker import worker_main
from . import ipc

log = get_logger(__name__)


class Supervisor:
    """Multi-process worker pool manager.

    Lifecycle:
      1. Supervisor.start() — spawns num_workers worker processes.
      2. Supervisor.submit_task(payload) — sends a TASK_SUBMIT message.
      3. Supervisor.collect_results(callback) — drains the result queue,
         invoking callback(result_payload) for each completed task.
      4. Supervisor.stop() — sends shutdown to all workers, joins processes.

    Process model:
      - Workers are spawned with the "spawn" start method for clean isolation
        (avoids fork-safety issues with logging, sockets, etc.).
      - IPC via multiprocessing.Queue (backed by OS pipes + pickle).
      - No shared memory between supervisor and workers.

    Health:
      - A HealthServer thread exposes /healthz and /readyz on
        MONOLITH_HEALTH_PORT (default 8080, 0 = disabled).
      - /readyz returns 503 until all workers have started.

    Metrics:
      - Supervisor-level metrics are exposed on MONOLITH_METRICS_PORT.
    """

    def __init__(self, config: Optional[MonolithConfig] = None) -> None:
        self._cfg = config or load_config()
        configure_logging(self._cfg.log_level)

        ctx = get_context("spawn")
        self._task_queue: "Queue[ipc.Message]" = ctx.Queue()
        self._result_queue: "Queue[ipc.Message]" = ctx.Queue()
        self._workers: List[Process] = []
        self._started = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Spawn all worker processes and start health + metrics servers."""
        if self._started:
            raise RuntimeError("Supervisor already started")

        health_port = int(os.getenv("MONOLITH_HEALTH_PORT", "8080"))
        health = HealthServer(
            port=health_port,
            readiness_check=self._all_workers_alive,
        )

        start_metrics_server(self._cfg.metrics_port)

        for i in range(self._cfg.num_workers):
            p = Process(
                target=worker_main,
                args=(self._task_queue, self._result_queue, self._cfg),
                name=f"monolith-worker-{i}",
                daemon=False,
            )
            p.start()
            self._workers.append(p)
            log.info("worker spawned", extra={"worker": p.name, "pid": p.pid})

        health.start()
        self._started = True
        log.info(
            "supervisor started",
            extra={"num_workers": self._cfg.num_workers},
        )

    def stop(self, timeout: float = 10.0) -> None:
        """Gracefully shut down all workers, then join their processes."""
        if not self._started:
            return

        shutdown_msg = ipc.Message(
            type=ipc.MessageType.CONTROL,
            payload={"action": "shutdown"},
        )
        for _ in self._workers:
            try:
                ipc.send(self._task_queue, shutdown_msg, timeout=2.0)
            except ipc.IPCError:
                pass

        deadline = time.time() + timeout
        for p in self._workers:
            remaining = max(0.0, deadline - time.time())
            p.join(timeout=remaining)
            if p.is_alive():
                log.warning("worker did not stop; terminating", extra={"pid": p.pid})
                p.terminate()
                p.join(timeout=2.0)

        self._workers.clear()
        self._started = False
        log.info("supervisor stopped")

    # ------------------------------------------------------------------
    # Task submission & result collection
    # ------------------------------------------------------------------

    def submit_task(self, task_payload: dict) -> None:
        """Send a task to the worker pool.

        Args:
            task_payload: Dict with optional "meta" sub-dict and arbitrary
                payload fields (Thirsty-Lang IR, Waterfall DAG node, etc.).

        Raises:
            RuntimeError: if the supervisor has not been started.
            ipc.IPCError: if the queue send times out.
        """
        if not self._started:
            raise RuntimeError("Supervisor not started; call start() first")
        msg = ipc.Message(
            type=ipc.MessageType.TASK_SUBMIT,
            payload=task_payload,
        )
        ipc.send(self._task_queue, msg, timeout=self._cfg.ipc_send_timeout)
        METRICS.tasks_submitted.inc()

    def collect_results(
        self,
        timeout: float = 0.1,
        max_results: int = 100,
    ) -> List[dict]:
        """Drain up to max_results task results from the result queue.

        Non-blocking if no results are available (returns empty list).

        Args:
            timeout: Per-recv timeout in seconds.
            max_results: Maximum number of results to collect per call.

        Returns:
            List of result payload dicts:
              {"id": str, "owner": str, "state": str, "last_error": str|None}
        """
        results = []
        for _ in range(max_results):
            try:
                msg = ipc.recv(self._result_queue, timeout=timeout)
                if msg.type == ipc.MessageType.TASK_RESULT:
                    results.append(msg.payload)
            except ipc.IPCError:
                break  # queue empty or timeout
        return results

    # ------------------------------------------------------------------
    # Health helpers
    # ------------------------------------------------------------------

    def _all_workers_alive(self) -> bool:
        return self._started and all(p.is_alive() for p in self._workers)

    def __enter__(self) -> "Supervisor":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()
