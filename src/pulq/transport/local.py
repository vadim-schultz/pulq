"""In-process transport: direct calls into :class:`~pulq.core.pull_queue.PullQueue`."""

from __future__ import annotations

from types import TracebackType
from typing import Any, Self

from pulq.core.pull_queue import PullQueue
from pulq.models import WorkResponse

__all__ = ["LocalTransport"]


class LocalTransport:
    """In-process transport delegating to :class:`~pulq.core.pull_queue.PullQueue`."""

    def __init__(self, queue: PullQueue) -> None:
        self._queue = queue

    async def setup_transport(self) -> None:
        """No-op: work uses the in-process queue only."""

    async def teardown_transport(self) -> None:
        """No-op."""

    async def __aenter__(self) -> Self:
        await self.setup_transport()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.teardown_transport()

    async def request_work(self, worker_id: str) -> WorkResponse:
        """Delegate to :meth:`pulq.core.pull_queue.PullQueue.get_next`."""
        return await self._queue.get_next(worker_id)

    async def report_completion(self, task_id: str, result: dict[str, Any]) -> None:
        """Delegate to :meth:`pulq.core.pull_queue.PullQueue.mark_complete`."""
        await self._queue.mark_complete(task_id, result)
