from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from multiprocessing import Queue
from typing import Any, Dict

from .errors import IPCError


class MessageType(Enum):
    TASK_SUBMIT = auto()
    TASK_RESULT = auto()
    WORKER_STATUS = auto()
    CONTROL = auto()   # shutdown, reload, pause


@dataclass
class Message:
    type: MessageType
    payload: Dict[str, Any]


def send(queue: "Queue[Message]", msg: Message, timeout: float = 5.0) -> None:
    """Put a message onto a queue.

    Args:
        queue: Target multiprocessing Queue.
        msg: Message to send.
        timeout: Max seconds to block before raising IPCError.

    Raises:
        IPCError: if the put times out or the queue is closed.
    """
    try:
        queue.put(msg, timeout=timeout)
    except Exception as exc:
        raise IPCError(f"send failed: {exc}") from exc


def recv(queue: "Queue[Message]", timeout: float | None = None) -> Message:
    """Get a message from a queue.

    Args:
        queue: Source multiprocessing Queue.
        timeout: Seconds to block; None = block indefinitely.

    Raises:
        IPCError: on timeout or if the queue is closed.
    """
    try:
        return queue.get(timeout=timeout)
    except Exception as exc:
        raise IPCError(f"recv failed: {exc}") from exc
