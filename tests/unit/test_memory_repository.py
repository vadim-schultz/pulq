"""Tests for :class:`~pulq.storage.memory.InMemoryTaskRepository`."""

from __future__ import annotations

import pytest

from pulq import (
    InMemoryTaskRepository,
    NoPendingTask,
    Task,
    TaskExecutionSetup,
    TaskStatus,
    WorkerContext,
)


@pytest.mark.asyncio
async def test_schedule_and_claim() -> None:
    r = InMemoryTaskRepository()
    t = Task(priority="high", handler_name="x", payload={"x": 1})
    tid = await r.schedule(t)
    claimed = await r.claim_next_pending("high", "worker-1")
    assert isinstance(claimed, Task)
    assert claimed.id == tid
    assert claimed.status is TaskStatus.RUNNING
    assert claimed.assigned_worker_id == "worker-1"


@pytest.mark.asyncio
async def test_claim_empty_returns_no_pending() -> None:
    r = InMemoryTaskRepository()
    out = await r.claim_next_pending("high", "w")
    assert isinstance(out, NoPendingTask)
    assert out.priority == "high"


@pytest.mark.asyncio
async def test_claim_rotates_past_non_matching_execution_target() -> None:
    r = InMemoryTaskRepository()
    await r.schedule(
        Task(
            priority="high",
            handler_name="x",
            payload={"n": 1},
            execution_target=TaskExecutionSetup(setup_name="s2"),
        ),
    )
    await r.schedule(
        Task(
            priority="high",
            handler_name="x",
            payload={"n": 2},
            execution_target=TaskExecutionSetup(setup_name="s1"),
        ),
    )
    ctx = WorkerContext(setup_name="s1")
    claimed = await r.claim_next_pending("high", "w", worker_context=ctx)
    assert isinstance(claimed, Task)
    assert claimed.payload["n"] == 2


@pytest.mark.asyncio
async def test_claim_reports_capability_mismatch_when_none_match() -> None:
    r = InMemoryTaskRepository()
    await r.schedule(
        Task(
            priority="high",
            handler_name="x",
            payload={},
            execution_target=TaskExecutionSetup(setup_name="other"),
        ),
    )
    out = await r.claim_next_pending(
        "high",
        "w",
        worker_context=WorkerContext(setup_name="here"),
    )
    assert isinstance(out, NoPendingTask)
    assert out.had_capability_mismatch is True


@pytest.mark.asyncio
async def test_mark_complete() -> None:
    r = InMemoryTaskRepository()
    t = Task(priority="low", handler_name="x", payload={})
    tid = await r.schedule(t)
    await r.claim_next_pending("low", "w")
    done = await r.mark_complete(tid, {"ok": True})
    assert done.status is TaskStatus.COMPLETED
