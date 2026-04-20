"""In-memory task repository for tests and single-process workloads."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from typing import Any

from pulq.errors import TaskNotFoundError
from pulq.models import NoPendingTask, PendingClaimed, Task, TaskStatus
from pulq.models.capabilities import DEFAULT_WORKER_CONTEXT, WorkerContext
from pulq.storage._claim import scan_pending_deque_for_claim

# This module is a reference `TaskRepository` for tests and local use, not a production
# backend. It keeps process-local state only (no durability, no multi-process safety), and
# claims walk a FIFO deque per priority—workers may scan past tasks they cannot run, which
# does not scale like indexed or partitioned stores. For production, use (or implement) a
# repository backed by Redis, SQLite, PostgreSQL, MongoDB, or similar.

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

    async def claim_next_pending(
        self,
        priority: str,
        worker_id: str,
        *,
        worker_context: WorkerContext = DEFAULT_WORKER_CONTEXT,
    ) -> Task | NoPendingTask:
        """Pop the next pending task for ``priority`` that matches ``worker_context``.

        Under :attr:`_lock`, deque mutation and ``_tasks`` updates are atomic for this process.

        Pending ids in the deque always have a row in ``_tasks`` (see :meth:`schedule`); a
        :class:`~pulq.models.NoPendingTask` is returned when the queue is starved or no task
        matches ``worker_context``.
        """
        async with self._lock:
            outcome = scan_pending_deque_for_claim(
                self._pending_ids[priority],
                self._tasks,
                worker_context,
                worker_id,
            )
        if isinstance(outcome, PendingClaimed):
            return outcome.task
        return NoPendingTask(
            priority=priority,
            had_capability_mismatch=outcome.had_capability_mismatch,
        )

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
