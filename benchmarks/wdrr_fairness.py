"""Rough fairness check: high:medium:low counts over many pulls."""

from __future__ import annotations

import asyncio

from pulq import InMemoryTaskRepository, PullQueue, Task


async def run(n_tasks_per_priority: int = 100, n_pulls: int = 100) -> None:
    """Pull subset of tasks to observe WDRR weight distribution.

    With weights {high: 3, medium: 2, low: 1}, expect roughly 50% high, 33% medium, 17% low.
    """
    repo = InMemoryTaskRepository()
    q = PullQueue(repo)
    for _ in range(n_tasks_per_priority):
        await q.schedule(Task(priority="high", payload={}))
        await q.schedule(Task(priority="medium", payload={}))
        await q.schedule(Task(priority="low", payload={}))

    counts = {"high": 0, "medium": 0, "low": 0}
    for _ in range(n_pulls):
        w = await q.get_next("bench")
        if w.type != "task":
            break
        assert isinstance(w, Task)
        counts[w.priority] += 1
        await repo.mark_complete(w.id, {"ok": True})

    total = sum(counts.values())
    print(f"Scheduled: {n_tasks_per_priority} per priority ({n_tasks_per_priority * 3} total)")
    print(f"Pulled: {total}/{n_pulls}")
    print(f"Counts: {counts}")
    print("Distribution:")
    for k, v in counts.items():
        print(f"  {k}: {v}/{total} = {v / total:.1%}")
    print("\nExpected (3:2:1 weights): high ~50%, medium ~33%, low ~17%")


if __name__ == "__main__":
    asyncio.run(run())
