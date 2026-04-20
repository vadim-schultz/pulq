"""Tests for :class:`~pulq.storage.redis.RedisTaskRepository`."""

from __future__ import annotations

import asyncio

import pytest
from fakeredis import FakeAsyncRedis

from pulq import (
    NoPendingTask,
    RedisTaskRepository,
    Task,
    TaskExecutionSetup,
    TaskStatus,
    WorkerContext,
)


@pytest.fixture
def redis_repo() -> RedisTaskRepository:
    r = FakeAsyncRedis(decode_responses=True)
    return RedisTaskRepository(r)


@pytest.mark.asyncio
async def test_schedule_and_claim(redis_repo: RedisTaskRepository) -> None:
    t = Task(priority="high", handler_name="x", payload={"x": 1})
    tid = await redis_repo.schedule(t)
    claimed = await redis_repo.claim_next_pending("high", "worker-1")
    assert isinstance(claimed, Task)
    assert claimed.id == tid
    assert claimed.status is TaskStatus.RUNNING
    assert claimed.assigned_worker_id == "worker-1"


@pytest.mark.asyncio
async def test_claim_empty_returns_no_pending(redis_repo: RedisTaskRepository) -> None:
    out = await redis_repo.claim_next_pending("high", "w")
    assert isinstance(out, NoPendingTask)
    assert out.priority == "high"


@pytest.mark.asyncio
async def test_claim_rotates_past_non_matching_execution_target(
    redis_repo: RedisTaskRepository,
) -> None:
    await redis_repo.schedule(
        Task(
            priority="high",
            handler_name="x",
            payload={"n": 1},
            execution_target=TaskExecutionSetup(setup_name="s2"),
        ),
    )
    await redis_repo.schedule(
        Task(
            priority="high",
            handler_name="x",
            payload={"n": 2},
            execution_target=TaskExecutionSetup(setup_name="s1"),
        ),
    )
    ctx = WorkerContext(setup_name="s1")
    claimed = await redis_repo.claim_next_pending("high", "w", worker_context=ctx)
    assert isinstance(claimed, Task)
    assert claimed.payload["n"] == 2


@pytest.mark.asyncio
async def test_claim_reports_capability_mismatch_when_none_match(
    redis_repo: RedisTaskRepository,
) -> None:
    await redis_repo.schedule(
        Task(
            priority="high",
            handler_name="x",
            payload={},
            execution_target=TaskExecutionSetup(setup_name="other"),
        ),
    )
    out = await redis_repo.claim_next_pending(
        "high",
        "w",
        worker_context=WorkerContext(setup_name="here"),
    )
    assert isinstance(out, NoPendingTask)
    assert out.had_capability_mismatch is True


@pytest.mark.asyncio
async def test_mark_complete(redis_repo: RedisTaskRepository) -> None:
    t = Task(priority="low", handler_name="x", payload={})
    tid = await redis_repo.schedule(t)
    await redis_repo.claim_next_pending("low", "w")
    done = await redis_repo.mark_complete(tid, {"ok": True})
    assert done.status is TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_concurrent_claims_serialize(redis_repo: RedisTaskRepository) -> None:
    await redis_repo.schedule(Task(priority="high", handler_name="a", payload={"i": 0}))

    async def claim(worker: str) -> Task | NoPendingTask:
        return await redis_repo.claim_next_pending("high", worker)

    a, b = await asyncio.gather(claim("w1"), claim("w2"))
    winners = [x for x in (a, b) if isinstance(x, Task)]
    assert len(winners) == 1
    assert isinstance(winners[0], Task)
    other = b if winners[0] is a else a
    assert isinstance(other, NoPendingTask)
