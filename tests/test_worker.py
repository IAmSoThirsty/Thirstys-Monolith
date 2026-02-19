from __future__ import annotations
import pytest
from monolith.models import Task, TaskMetadata, TaskState


class TestTaskMetadata:
    def test_id_auto_generated(self) -> None:
        m1 = TaskMetadata()
        m2 = TaskMetadata()
        assert m1.id != m2.id

    def test_defaults(self) -> None:
        m = TaskMetadata()
        assert m.owner == "system"
        assert m.priority == 0
        assert m.deadline is None
        assert m.labels == {}
        assert m.resource_hints == {}

    def test_custom_values(self) -> None:
        m = TaskMetadata(owner="alice", priority=5, labels={"env": "prod"})
        assert m.owner == "alice"
        assert m.priority == 5
        assert m.labels == {"env": "prod"}


class TestTask:
    def test_default_state_pending(self) -> None:
        meta = TaskMetadata()
        task = Task(meta=meta, payload={"op": "noop"})
        assert task.state == TaskState.PENDING
        assert task.last_error is None

    def test_state_transitions(self) -> None:
        meta = TaskMetadata()
        task = Task(meta=meta, payload={})
        for state in TaskState:
            task.state = state
            assert task.state == state

    def test_payload_preserved(self) -> None:
        meta = TaskMetadata()
        payload = {"op": "run", "data": [1, 2, 3]}
        task = Task(meta=meta, payload=payload)
        assert task.payload == payload


class TestTaskStateSupervisor:
    def test_all_states_defined(self) -> None:
        expected = {"PENDING", "RUNNING", "WAITING", "DONE", "FAILED", "CANCELLED"}
        actual = {s.name for s in TaskState}
        assert actual == expected
