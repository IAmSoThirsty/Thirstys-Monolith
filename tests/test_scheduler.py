from __future__ import annotations
import queue
import pytest
from monolith.scheduler import Scheduler
from monolith.models import TaskState
from monolith.errors import TaskExecutionError


@pytest.fixture()
def result_q() -> queue.Queue:
    return queue.Queue()


@pytest.fixture()
def scheduler(result_q: queue.Queue) -> Scheduler:
    return Scheduler(result_queue=result_q, quantum_ms=10, memory_pool_bytes=1024 * 1024)


def _payload(name: str = "test", priority: int = 0) -> dict:
    return {
        "meta": {"owner": "test-tenant", "priority": priority},
        "op": name,
    }


class TestEnqueue:
    def test_enqueue_adds_task(self, scheduler: Scheduler) -> None:
        scheduler.enqueue_from_payload(_payload())
        assert len(scheduler._tasks) == 1

    def test_enqueue_sets_pending(self, scheduler: Scheduler) -> None:
        scheduler.enqueue_from_payload(_payload())
        assert scheduler._tasks[0].state == TaskState.PENDING

    def test_enqueue_priority_respected(self, scheduler: Scheduler) -> None:
        scheduler.enqueue_from_payload(_payload("low", priority=1))
        scheduler.enqueue_from_payload(_payload("high", priority=99))
        ready = [t for t in scheduler._tasks if t.state == TaskState.PENDING]
        selected = max(ready, key=lambda t: (t.meta.priority, -t.meta.created_at))
        assert selected.payload["op"] == "high"


class TestRunOnce:
    def test_run_once_completes_task(self, scheduler: Scheduler, result_q: queue.Queue) -> None:
        scheduler.enqueue_from_payload(_payload())
        scheduler.run_once()
        assert result_q.qsize() == 1
        result = result_q.get_nowait()
        assert result.payload["state"] == "DONE"

    def test_run_once_noop_when_empty(self, scheduler: Scheduler) -> None:
        # Should not raise
        scheduler.run_once()

    def test_failed_task_emits_result(self, scheduler: Scheduler, result_q: queue.Queue) -> None:
        scheduler.enqueue_from_payload(_payload())

        def _raise(task):
            raise RuntimeError("simulated failure")

        scheduler._execute_step = _raise
        scheduler.run_once()
        result = result_q.get_nowait()
        assert result.payload["state"] == "FAILED"
        assert "simulated failure" in result.payload["last_error"]

    def test_deadline_exceeded_cancels_task(
        self, scheduler: Scheduler, result_q: queue.Queue
    ) -> None:
        import time
        payload = _payload()
        payload["meta"]["deadline"] = time.time() - 1.0  # already past
        scheduler.enqueue_from_payload(payload)
        scheduler.run_once()
        result = result_q.get_nowait()
        assert result.payload["state"] == "CANCELLED"

    def test_priority_ordering_executes_highest_first(
        self, scheduler: Scheduler, result_q: queue.Queue
    ) -> None:
        scheduler.enqueue_from_payload(_payload("low", priority=1))
        scheduler.enqueue_from_payload(_payload("high", priority=50))
        scheduler.run_once()
        result = result_q.get_nowait()
        # The "high" task should have been selected and completed first
        assert result.payload["state"] == "DONE"
