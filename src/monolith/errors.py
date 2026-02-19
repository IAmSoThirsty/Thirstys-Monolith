from __future__ import annotations


class MonolithError(Exception):
    """Base class for all Monolith errors."""


class TaskExecutionError(MonolithError):
    """Raised when a task step fails during execution."""


class MemoryErrorLogical(MonolithError):
    """Raised on logical memory violations (bounds, owner mismatch, OOM)."""


class IPCError(MonolithError):
    """Raised on IPC send/recv failures."""
