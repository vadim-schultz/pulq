"""Protocols and callback types."""

from __future__ import annotations

from types import TracebackType
from typing import Any, Protocol, Self

from pulq.models import ClaimResult, Task, WorkResponse
from pulq.models.capabilities import WorkerContext

__all__ = [
    "ClaimResult",
    "HeartbeatCallback",
    "TaskHandler",
    "TaskRepository",
    "Transport",
    "WorkResponse",
    "WorkerContext",
]


class TaskRepository(Protocol):
    """Storage backend for pending tasks (implement with DB, Redis, etc.)."""

    async def claim_next_pending(
        self,
        priority: str,
        worker_id: str,
        *,
        worker_context: WorkerContext,
    ) -> ClaimResult:
        """Atomically claim the next pending task for ``priority``, if any."""

    async def mark_complete(self, task_id: str, result: dict[str, Any]) -> Task:
        """Mark a task completed and return the updated record."""

    async def schedule(self, task: Task) -> str:
        """Enqueue ``task``; return its id."""


class Transport(Protocol):
    """How a worker obtains work and reports completion (local, HTTP, …).

    :class:`~pulq.core.worker.Worker` runs ``async with transport``, which must
    call :meth:`setup_transport` on enter and :meth:`teardown_transport` on exit.
    In-process transports use no-ops; remote transports open/close connections
    there. Standalone code may use the same ``async with`` pattern.
    """

    async def setup_transport(self) -> None:
        """Prepare wire resources (e.g. open an HTTP client)."""

    async def teardown_transport(self) -> None:
        """Release wire resources (e.g. close connections)."""

    async def __aenter__(self) -> Self:
        """Enter context: typically ``await setup_transport()`` then ``return self``."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit context: typically ``await teardown_transport()``."""

    async def request_work(
        self,
        worker_id: str,
        *,
        worker_context: WorkerContext,
    ) -> WorkResponse:
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
