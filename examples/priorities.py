"""Schedule many tasks and observe WDRR priority service."""

from __future__ import annotations

import asyncio

from pulq import InMemoryTaskRepository, PullQueue, Task


async def main() -> None:
    repo = InMemoryTaskRepository()
    queue = PullQueue(
        repo,
        priority_order=("high", "medium", "low"),
        weights={"high": 3, "medium": 2, "low": 1},
    )
    for p in ("low", "medium", "high"):
        for i in range(5):
            await queue.schedule(Task(priority=p, payload={"p": p, "i": i}))

    order: list[str] = []
    for _ in range(15):
        item = await queue.get_next("demo-worker")
        if item.type != "task":
            break
        assert isinstance(item, Task)
        order.append(item.payload["p"])
        await repo.mark_complete(item.id, {"ok": True})

    print("First 15 pulls (priority labels):", order)


if __name__ == "__main__":
    asyncio.run(main())
