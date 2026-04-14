"""Worker pull loop."""

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
async def test_worker_processes_task_and_stops() -> None:
    repo = InMemoryTaskRepository()
    q = PullQueue(
        repo,
        config=PullQueueConfig(
            scheduler=DeficitSchedulerConfig(priority_order=("high",), weights={"high": 1}),
        ),
    )
    await q.schedule(Task(priority="high", payload={"v": 1}))
    transport = LocalTransport(q)

    processed: list[str] = []

    async def handle(task: Task) -> dict[str, bool]:
        processed.append(task.id)
        return {"ok": True}

    worker = Worker(transport, "w1", handle, config=WorkerConfig(no_work_delay_seconds=0.001))

    async def stop_soon() -> None:
        await asyncio.sleep(0.05)
        q.send_command("w1", CommandType.STOP)

    await asyncio.gather(worker.run(), stop_soon())
    assert len(processed) == 1
