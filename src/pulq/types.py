"""Protocols and callback types."""

from __future__ import annotations

from typing import Any, Protocol

from pulq.models import ClaimResult, Task, WorkResponse

__all__ = [
    "ClaimResult",
    "HeartbeatCallback",
    "TaskHandler",
    "TaskRepository",
    "Transport",
    "WorkResponse",
]


class TaskRepository(Protocol):
    """Storage backend for pending tasks (implement with DB, Redis, etc.)."""

    async def claim_next_pending(self, priority: str, worker_id: str) -> ClaimResult:
        """Atomically claim the next pending task for ``priority``, if any."""

    async def mark_complete(self, task_id: str, result: dict[str, Any]) -> Task:
        """Mark a task completed and return the updated record."""

    async def schedule(self, task: Task) -> str:
        """Enqueue ``task``; return its id."""


class Transport(Protocol):
    """How a worker obtains work and reports completion (local, HTTP, …)."""

    async def request_work(self, worker_id: str) -> WorkResponse:
        """Pull the next schedulable item for ``worker_id``."""

    async def report_completion(self, task_id: str, result: dict[str, Any]) -> None:
        """Persist completion for ``task_id``."""


class TaskHandler(Protocol):
    """User-defined async handler for :class:`~pulq.models.Task` execution."""

    async def __call__(self, task: Task) -> dict[str, Any]:
        """Execute ``task`` and return a JSON-serializable result dict."""


class HeartbeatCallback(Protocol):
    """Optional hook invoked when a worker requests work."""

    async def __call__(self, worker_id: str) -> None:
        """Record liveness for ``worker_id``."""


# `WorkResponse` / `ClaimResult` are type aliases defined in :mod:`pulq.models`.
