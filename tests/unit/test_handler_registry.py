"""HandlerRegistry and worker lifecycle via registry."""

from __future__ import annotations

import asyncio

import pytest

from pulq import (
    CommandType,
    DeficitSchedulerConfig,
    HandlerRegistry,
    InMemoryTaskRepository,
    LocalTransport,
    PullQueue,
    PullQueueConfig,
    Task,
    Worker,
    WorkerConfig,
)


@pytest.mark.asyncio
async def test_startup_shutdown_and_after_process() -> None:
    repo = InMemoryTaskRepository()
    q = PullQueue(
        repo,
        config=PullQueueConfig(
            scheduler=DeficitSchedulerConfig(priority_order=("high",), weights={"high": 1}),
        ),
    )
    await q.schedule(Task(priority="high", handler_name="default", payload={}))
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

    registry = HandlerRegistry(
        default=handle,
        startup=startup,
        shutdown=shutdown,
        after_process=after,
    )
    worker = Worker(transport, "w", registry, config=WorkerConfig(no_work_delay_seconds=0.001))

    async def fire_stop() -> None:
        await asyncio.sleep(0.02)
        q.send_command("w", CommandType.STOP)

    await asyncio.gather(worker.run(), fire_stop())
    assert "start" in log
    assert "stop" in log
    assert any(x.startswith("after:") for x in log)


def test_registry_named_handlers_and_default() -> None:
    async def a(_: Task) -> dict[str, bool | str]:
        return {"ok": True, "which": "a"}

    async def b(_: Task) -> dict[str, bool | str]:
        return {"ok": True, "which": "b"}

    async def d(_: Task) -> dict[str, bool | str]:
        return {"ok": True, "which": "default"}

    reg = HandlerRegistry(foo=a, bar=b, default=d)
    # HandlerRegistry stores callables; sync test only checks resolution
    assert reg.get_handler("foo") is a
    assert reg.get_handler("bar") is b
    assert reg.get_handler("unknown") is d
