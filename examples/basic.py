"""Minimal in-process example.

Uses the library defaults: three priorities (high / medium / low) with 3:2:1
weights, quantum 1, and a short idle delay between pulls when the queue is
empty. For custom WDRR settings, pass ``config=PullQueueConfig(...)``; for
worker hooks or a different idle delay, use ``config=WorkerConfig(...)``.
"""

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
    queue = PullQueue(repo)
    await queue.schedule(Task(priority="high", payload={"job": "a"}))
    await queue.schedule(Task(priority="medium", payload={"job": "b"}))
    transport = LocalTransport(queue)
    worker = Worker(transport, "worker-1", handle)

    async def stop_after_short_delay() -> None:
        await asyncio.sleep(0.05)
        queue.send_command("worker-1", CommandType.STOP)

    await asyncio.gather(worker.run(), stop_after_short_delay())


if __name__ == "__main__":
    asyncio.run(main())
