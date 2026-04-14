"""Non-STOP management commands."""

from __future__ import annotations

import asyncio

import pytest

from pulq import (
    CommandType,
    DeficitSchedulerConfig,
    InMemoryTaskRepository,
    LocalTransport,
    PullQueue,
    PullQueueConfig,
    Task,
    Worker,
    WorkerConfig,
)


@pytest.mark.asyncio
async def test_worker_ignores_pause_then_stops() -> None:
    repo = InMemoryTaskRepository()
    q = PullQueue(
        repo,
        config=PullQueueConfig(
            scheduler=DeficitSchedulerConfig(priority_order=("high",), weights={"high": 1}),
        ),
    )
    await q.schedule(Task(priority="high", payload={}))
    transport = LocalTransport(q)

    async def handle(_task: Task) -> dict[str, bool]:
        return {"ok": True}

    worker = Worker(transport, "w", handle, config=WorkerConfig(no_work_delay_seconds=0.001))

    async def sequence() -> None:
        await asyncio.sleep(0.01)
        q.send_command("w", CommandType.PAUSE)
        await asyncio.sleep(0.01)
        q.send_command("w", CommandType.STOP)

    await asyncio.gather(worker.run(), sequence())
