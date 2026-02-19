"""
Structured logging for the Monolith runtime.

Uses Python's stdlib logging with a JSON formatter so log lines are
machine-parseable by Fluentd / Loki / CloudWatch.

Usage:
    from monolith.logging import get_logger
    log = get_logger(__name__)
    log.info("task submitted", extra={"task_id": task.meta.id})
"""

from __future__ import annotations
import json
import logging
import os
import time
from typing import Any, MutableMapping


class _JSONFormatter(logging.Formatter):
    """Formats log records as newline-delimited JSON (NDJSON)."""

    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "pid": os.getpid(),
        }
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        # Merge any extra fields injected via `extra=`
        for key, val in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                base[key] = val
        return json.dumps(base, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with JSON output to stdout.

    Should be called once at process startup (worker_main or supervisor start).
    """
    handler = logging.StreamHandler()
    handler.setFormatter(_JSONFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """Return a named logger (lazily created by stdlib machinery)."""
    return logging.getLogger(name)
