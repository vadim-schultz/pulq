"""Repository error paths."""

from __future__ import annotations

import pytest

from pulq import InMemoryTaskRepository, Task, TaskStatus
from pulq.errors import TaskNotFoundError


@pytest.mark.asyncio
async def test_schedule_non_pending_rejected() -> None:
    r = InMemoryTaskRepository()
    t = Task(priority="h", handler_name="x", payload={}, status=TaskStatus.RUNNING)
    with pytest.raises(ValueError, match="PENDING"):
        await r.schedule(t)


@pytest.mark.asyncio
async def test_mark_complete_unknown_task() -> None:
    r = InMemoryTaskRepository()
    with pytest.raises(TaskNotFoundError):
        await r.mark_complete("missing", {"ok": True})
