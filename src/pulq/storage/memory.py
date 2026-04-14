"""In-memory task repository for tests and single-process workloads."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from typing import Any

from pulq.errors import TaskNotFoundError
from pulq.models import NoPendingTask, Task, TaskStatus

__all__ = ["InMemoryTaskRepository"]


class InMemoryTaskRepository:
    """FIFO pending queues per priority with atomic claim semantics."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._pending_ids: defaultdict[str, deque[str]] = defaultdict(deque)
        self._tasks: dict[str, Task] = {}

    async def schedule(self, task: Task) -> str:
        """Enqueue a pending task under its priority bucket."""
        if task.status != TaskStatus.PENDING:
            msg = "Can only schedule tasks in PENDING status"
            raise ValueError(msg)
        async with self._lock:
            self._tasks[task.id] = task.model_copy(deep=True)
            self._pending_ids[task.priority].append(task.id)
        return task.id

    async def claim_next_pending(self, priority: str, worker_id: str) -> Task | NoPendingTask:
        """Pop oldest pending task for ``priority`` and mark it RUNNING."""
        async with self._lock:
            q = self._pending_ids[priority]
            while q:
                task_id = q.popleft()
                existing = self._tasks.get(task_id)
                if existing is None or existing.status != TaskStatus.PENDING:
                    continue
                claimed = existing.model_copy(
                    update={
                        "status": TaskStatus.RUNNING,
                        "assigned_worker_id": worker_id,
                    },
                    deep=True,
                )
                self._tasks[task_id] = claimed
                return claimed
        return NoPendingTask(priority=priority)

    async def mark_complete(self, task_id: str, result: dict[str, Any]) -> Task:
        """Set task to COMPLETED unless ``result`` contains ``\"ok\": False``."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            ok = result.get("ok", True)
            new_status = TaskStatus.COMPLETED if ok else TaskStatus.FAILED
            updated = task.model_copy(update={"status": new_status}, deep=True)
            self._tasks[task_id] = updated
            return updated
