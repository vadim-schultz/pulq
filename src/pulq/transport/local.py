"""In-process transport: direct calls into :class:`~pulq.core.pull_queue.PullQueue`."""

from __future__ import annotations

from typing import Any

from pulq.core.pull_queue import PullQueue
from pulq.models import WorkResponse

__all__ = ["LocalTransport"]


class LocalTransport:
    """In-process transport delegating to :class:`~pulq.core.pull_queue.PullQueue`."""

    def __init__(self, queue: PullQueue) -> None:
        self._queue = queue

    async def request_work(self, worker_id: str) -> WorkResponse:
        """Delegate to :meth:`pulq.core.pull_queue.PullQueue.get_next`."""
        return await self._queue.get_next(worker_id)

    async def report_completion(self, task_id: str, result: dict[str, Any]) -> None:
        """Delegate to :meth:`pulq.core.pull_queue.PullQueue.mark_complete`."""
        await self._queue.mark_complete(task_id, result)
