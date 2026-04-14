"""Worker lifecycle hooks."""

from __future__ import annotations

import asyncio

import pytest

from pulq import (
    CommandType,
    InMemoryTaskRepository,
    LocalTransport,
    PullQueue,
    Task,
    Worker,
)


@pytest.mark.asyncio
async def test_startup_shutdown_and_after_process() -> None:
    repo = InMemoryTaskRepository()
    q = PullQueue(repo, priority_order=("high",), weights={"high": 1})
    await q.schedule(Task(priority="high", payload={}))
    transport = LocalTransport(q)

    log: list[str] = []

    async def handle(_task: Task) -> dict[str, bool]:
        return {"ok": True}

    async def startup() -> None:
        log.append("start")

    async def shutdown() -> None:
        log.append("stop")

    async def after(task: Task, result: dict[str, bool]) -> None:
        log.append(f"after:{task.id}:{result['ok']}")

    worker = Worker(
        transport,
        "w",
        handle,
        no_work_delay_seconds=0.001,
        startup=startup,
        shutdown=shutdown,
        after_process=after,
    )

    async def fire_stop() -> None:
        await asyncio.sleep(0.02)
        q.send_command("w", CommandType.STOP)

    await asyncio.gather(worker.run(), fire_stop())
    assert "start" in log
    assert "stop" in log
    assert any(x.startswith("after:") for x in log)
