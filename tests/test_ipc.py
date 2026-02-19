from __future__ import annotations
import queue
import pytest
from unittest.mock import MagicMock, patch
from monolith.ipc import Message, MessageType, send, recv
from monolith.errors import IPCError


def _make_queue() -> queue.Queue:
    """Use stdlib queue for single-process tests (avoids multiprocessing overhead)."""
    return queue.Queue()


class TestSend:
    def test_send_puts_message(self) -> None:
        q = _make_queue()
        msg = Message(type=MessageType.TASK_SUBMIT, payload={"x": 1})
        send(q, msg)
        assert q.qsize() == 1

    def test_send_raises_on_full_queue(self) -> None:
        q = queue.Queue(maxsize=1)
        send(q, Message(type=MessageType.TASK_SUBMIT, payload={}))
        with pytest.raises(IPCError):
            send(q, Message(type=MessageType.TASK_SUBMIT, payload={}), timeout=0.05)


class TestRecv:
    def test_recv_returns_message(self) -> None:
        q = _make_queue()
        msg = Message(type=MessageType.TASK_RESULT, payload={"id": "abc", "state": "DONE"})
        q.put(msg)
        received = recv(q, timeout=1.0)
        assert received.type == MessageType.TASK_RESULT
        assert received.payload["id"] == "abc"

    def test_recv_timeout_raises_ipc_error(self) -> None:
        q = _make_queue()
        with pytest.raises(IPCError):
            recv(q, timeout=0.05)

    def test_send_recv_roundtrip_all_types(self) -> None:
        q = _make_queue()
        for mtype in MessageType:
            msg = Message(type=mtype, payload={})
            send(q, msg)
        for mtype in MessageType:
            received = recv(q, timeout=0.1)
            assert received.type == mtype
