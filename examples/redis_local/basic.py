"""Minimal example: PullQueue with Redis-backed storage.

Run Redis locally, for example::

    docker run --rm -p 6379:6379 redis:7

Then::

    pip install pulq[redis]
    python examples/redis_local/basic.py
"""

from __future__ import annotations

import asyncio

from redis.asyncio import Redis

from pulq import PullQueue, RedisTaskRepository, Task


async def main() -> None:
    client = Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    repo = RedisTaskRepository(client)
    queue = PullQueue(repo)

    tid = await queue.schedule(
        Task(priority="high", handler_name="demo", payload={"hello": "world"}),
    )
    work = await queue.get_next("worker-1")
    assert work.type == "task"
    assert work.id == tid
    await queue.mark_complete(work.id, {"ok": True})
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
