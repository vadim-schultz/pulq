"""Integration-style checks for WDRR ordering."""

from __future__ import annotations

import pytest

from pulq import InMemoryTaskRepository, PullQueue, Task


@pytest.mark.asyncio
async def test_three_two_one_weights_approximate_order() -> None:
    """Pull subset to observe WDRR weight distribution (3:2:1 → ~50%:33%:17%)."""
    repo = InMemoryTaskRepository()
    q = PullQueue(repo)
    # Schedule 100 tasks per priority
    for _ in range(100):
        await q.schedule(Task(priority="high", handler_name="bench", payload={}))
        await q.schedule(Task(priority="medium", handler_name="bench", payload={}))
        await q.schedule(Task(priority="low", handler_name="bench", payload={}))

    # Pull only 100 (leaving 200 unprocessed)
    counts = {"high": 0, "medium": 0, "low": 0}
    for _ in range(100):
        item = await q.get_next("worker")
        assert item.type == "task"
        assert isinstance(item, Task)
        counts[item.priority] += 1
        await repo.mark_complete(item.id, {"ok": True})

    # Verify WDRR fairness: high > medium > low with reasonable margins
    assert counts["high"] > counts["medium"] > counts["low"]
    # With 3:2:1 weights, expect approximately 50:33:17 distribution
    total = sum(counts.values())
    high_pct = counts["high"] / total
    medium_pct = counts["medium"] / total
    low_pct = counts["low"] / total
    assert 0.45 <= high_pct <= 0.55  # ~50% ±5%
    assert 0.28 <= medium_pct <= 0.38  # ~33% ±5%
    assert 0.12 <= low_pct <= 0.22  # ~17% ±5%
