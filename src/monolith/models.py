from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional
import uuid
import time


class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    WAITING = auto()
    DONE = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class TaskMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    owner: str = "system"              # tenant / principal
    priority: int = 0                  # higher = sooner
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None   # epoch seconds
    labels: Dict[str, str] = field(default_factory=dict)
    resource_hints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    meta: TaskMetadata
    payload: Dict[str, Any]           # Thirsty-Lang / Waterfall IR fragment
    state: TaskState = TaskState.PENDING
    last_error: Optional[str] = None
