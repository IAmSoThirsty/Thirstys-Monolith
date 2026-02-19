from __future__ import annotations
from multiprocessing import Queue

from .config import MonolithConfig, load_config
from .logging import configure_logging, get_logger
from .metrics import METRICS, start_metrics_server
from .scheduler import Scheduler
from . import ipc

log = get_logger(__name__)


def worker_main(
    task_queue: "Queue[ipc.Message]",
    result_queue: "Queue[ipc.Message]",
    config: MonolithConfig | None = None,
) -> None:
    """Entry point for each worker process.

    Spawned by Supervisor via multiprocessing.Process(target=worker_main).
    Runs until a CONTROL/shutdown message is received or an unrecoverable
    error occurs.

    Args:
        task_queue: Incoming task messages from the Supervisor.
        result_queue: Outgoing result messages back to the Supervisor.
        config: Optional pre-built config; loaded from env if None.
    """
    cfg = config or load_config()
    configure_logging(cfg.log_level)

    # Each worker gets its own metrics port offset by worker index.
    # Workers don't know their index; metrics server port=0 disables it.
    # The Supervisor may pass a non-zero port via config if needed.
    start_metrics_server(0)  # per-worker server disabled by default

    scheduler = Scheduler(
        result_queue=result_queue,
        quantum_ms=cfg.quantum_ms,
        memory_pool_bytes=cfg.memory_pool_bytes,
    )

    log.info("worker started")

    while True:
        try:
            msg = ipc.recv(task_queue, timeout=1.0)
        except ipc.IPCError:
            # Timeout — run the scheduler loop even if no new tasks arrived
            scheduler.run_once()
            continue

        if msg.type == ipc.MessageType.TASK_SUBMIT:
            scheduler.enqueue_from_payload(msg.payload)
            scheduler.run_once()

        elif msg.type == ipc.MessageType.CONTROL:
            action = msg.payload.get("action", "")
            log.info("control message received", extra={"action": action})
            if action == "shutdown":
                break
            # Future: reload, pause, etc.

        else:
            log.warning("unknown message type", extra={"type": str(msg.type)})
            scheduler.run_once()

    log.info("worker stopped")
