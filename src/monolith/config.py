from __future__ import annotations
from dataclasses import dataclass
import os


@dataclass
class MonolithConfig:
    """Runtime configuration for the Monolith supervisor and workers.

    All fields can be overridden via environment variables at process start.
    No hot-reload is performed; restart the supervisor to pick up changes.

    Attributes:
        num_workers: Number of worker processes to spawn.
            Env: MONOLITH_NUM_WORKERS (default: 4)
        quantum_ms: Cooperative scheduling quantum in milliseconds.
            Env: MONOLITH_QUANTUM_MS (default: 10)
        memory_pool_bytes: Logical memory pool size per worker, in bytes.
            Env: MONOLITH_MEMORY_POOL_BYTES (default: 67108864 = 64 MiB)
        log_level: Python logging level name (DEBUG, INFO, WARNING, ERROR).
            Env: MONOLITH_LOG_LEVEL (default: INFO)
        metrics_port: Prometheus /metrics HTTP port (0 = disabled).
            Env: MONOLITH_METRICS_PORT (default: 9100)
        ipc_send_timeout: Seconds before send() raises IPCError.
            Env: MONOLITH_IPC_SEND_TIMEOUT (default: 5.0)
    """

    num_workers: int = int(os.getenv("MONOLITH_NUM_WORKERS", "4"))
    quantum_ms: int = int(os.getenv("MONOLITH_QUANTUM_MS", "10"))
    memory_pool_bytes: int = int(
        os.getenv("MONOLITH_MEMORY_POOL_BYTES", str(64 * 1024 * 1024))
    )
    log_level: str = os.getenv("MONOLITH_LOG_LEVEL", "INFO")
    metrics_port: int = int(os.getenv("MONOLITH_METRICS_PORT", "9100"))
    ipc_send_timeout: float = float(os.getenv("MONOLITH_IPC_SEND_TIMEOUT", "5.0"))


def load_config() -> MonolithConfig:
    """Load configuration from environment variables.

    Returns:
        MonolithConfig populated from the current process environment.
    """
    return MonolithConfig()
