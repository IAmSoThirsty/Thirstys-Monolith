from __future__ import annotations
import time
from typing import List

from multiprocessing import Queue

from .errors import TaskExecutionError
from .memory import MemoryPool
from .models import Task, TaskMetadata, TaskState
from .metrics import METRICS
from .logging import get_logger
from . import ipc

log = get_logger(__name__)


class Scheduler:
    """Cooperative priority scheduler for one worker process.

    Scheduling policy:
      - Tasks in PENDING or WAITING state are eligible.
      - Among eligible tasks, the one with the highest `meta.priority` runs.
      - Ties broken by earliest `meta.created_at`.
      - Each call to `run_once()` executes one quantum for one task.

    Deadline enforcement:
      - If a task's `meta.deadline` has passed at the time it is selected,
        it is immediately moved to CANCELLED and its result emitted.

    Memory:
      - Each task that calls `alloc_region()` gets a Region in the shared
        MemoryPool for this worker. Memory is freed automatically on DONE/FAILED.
    """

    def __init__(
        self,
        result_queue: "Queue[ipc.Message]",
        quantum_ms: int = 10,
        memory_pool_bytes: int = 64 * 1024 * 1024,
    ) -> None:
        self._tasks: List[Task] = []
        self._result_queue = result_queue
        self._quantum_ms = quantum_ms
        self._memory = MemoryPool(max_bytes=memory_pool_bytes)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enqueue_from_payload(self, payload: dict) -> None:
        """Deserialise an IPC payload dict into a Task and add it to the queue."""
        meta_dict = payload.get("meta", {})
        meta = TaskMetadata(
            owner=meta_dict.get("owner", "system"),
            priority=meta_dict.get("priority", 0),
            deadline=meta_dict.get("deadline"),
            labels=meta_dict.get("labels", {}),
            resource_hints=meta_dict.get("resource_hints", {}),
        )
        task = Task(meta=meta, payload=payload)
        self._tasks.append(task)
        METRICS.tasks_submitted.inc()
        METRICS.worker_queue_depth.set(len(self._tasks))
        log.debug("task enqueued", extra={"task_id": task.meta.id, "priority": task.meta.priority})

    def run_once(self) -> None:
        """Pick the highest-priority eligible task and execute one quantum."""
        now = time.time()
        ready_tasks = [
            t for t in self._tasks
            if t.state in {TaskState.PENDING, TaskState.WAITING}
        ]
        if not ready_tasks:
            return

        # Select: highest priority, then earliest creation time
        task = max(
            ready_tasks,
            key=lambda t: (t.meta.priority, -t.meta.created_at),
        )

        # Deadline check
        if task.meta.deadline is not None and now > task.meta.deadline:
            task.state = TaskState.CANCELLED
            log.warning("task deadline exceeded", extra={"task_id": task.meta.id})
            METRICS.tasks_cancelled.inc()
            self._emit_result(task)
            self._tasks.remove(task)
            METRICS.worker_queue_depth.set(len(self._tasks))
            return

        self._run_task_quantum(task)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_task_quantum(self, task: Task) -> None:
        start = time.time()
        task.state = TaskState.RUNNING
        try:
            self._execute_step(task)
            if self._is_task_complete(task):
                task.state = TaskState.DONE
                METRICS.tasks_completed.inc()
                self._emit_result(task)
                self._tasks.remove(task)
        except Exception as exc:  # noqa: BLE001
            task.state = TaskState.FAILED
            task.last_error = str(exc)
            METRICS.tasks_failed.inc()
            log.error(
                "task failed",
                extra={"task_id": task.meta.id, "error": str(exc)},
                exc_info=True,
            )
            self._emit_result(task)
            self._tasks.remove(task)
        finally:
            elapsed_ms = (time.time() - start) * 1000
            if elapsed_ms > self._quantum_ms:
                METRICS.scheduler_quantum_overruns.inc()
                log.warning(
                    "quantum overrun",
                    extra={
                        "task_id": task.meta.id,
                        "elapsed_ms": round(elapsed_ms, 2),
                        "quantum_ms": self._quantum_ms,
                    },
                )
            METRICS.worker_queue_depth.set(len(self._tasks))
            METRICS.memory_used_bytes.set(self._memory.used_bytes)
            METRICS.memory_region_count.set(self._memory.region_count)

    def _execute_step(self, task: Task) -> None:
        """Execute one step of the task's payload.

        Extension point: replace this with a Thirsty-Lang VM step or a
        Waterfall DAG node evaluation. The default implementation is a no-op
        (single-step = complete).
        """
        # Hook: custom interpreters register here via subclassing or injection.
        # E.g.: ThirstyLangInterpreter(task).step()
        pass

    @staticmethod
    def _is_task_complete(task: Task) -> bool:
        """By default, one step = complete. Override for multi-step tasks."""
        return task.state not in {TaskState.WAITING}

    def _emit_result(self, task: Task) -> None:
        msg = ipc.Message(
            type=ipc.MessageType.TASK_RESULT,
            payload={
                "id": task.meta.id,
                "owner": task.meta.owner,
                "state": task.state.name,
                "last_error": task.last_error,
            },
        )
        ipc.send(self._result_queue, msg)
