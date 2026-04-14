"""Minimal in-process example."""

from __future__ import annotations

import asyncio

from pulq import (
    CommandType,
    InMemoryTaskRepository,
    LocalTransport,
    PullQueue,
    Task,
    Worker,
)


async def handle(task: Task) -> dict[str, bool | str]:
    return {"ok": True, "task": task.id}


async def main() -> None:
    repo = InMemoryTaskRepository()
    queue = PullQueue(
        repo,
        priority_order=("high", "medium", "low"),
        weights={"high": 3, "medium": 2, "low": 1},
    )
    await queue.schedule(Task(priority="high", payload={"job": "a"}))
    transport = LocalTransport(queue)
    worker = Worker(transport, "worker-1", handle, no_work_delay_seconds=0.01)

    async def stop_after_short_delay() -> None:
        await asyncio.sleep(0.05)
        queue.send_command("worker-1", CommandType.STOP)

    await asyncio.gather(worker.run(), stop_after_short_delay())


if __name__ == "__main__":
    asyncio.run(main())
