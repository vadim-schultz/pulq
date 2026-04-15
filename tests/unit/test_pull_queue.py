"""Tests for :class:`~pulq.core.pull_queue.PullQueue`."""

from __future__ import annotations

import pytest

from pulq import (
    CommandType,
    InMemoryTaskRepository,
    ManagementCommand,
    NoWork,
    NoWorkReason,
    PullQueue,
    PullQueueConfig,
    Task,
)


@pytest.mark.asyncio
async def test_management_command_preempts_tasks(queue: PullQueue) -> None:
    await queue.schedule(Task(priority="high", handler_name="x", payload={}))
    queue.send_command("w1", CommandType.PAUSE)
    work = await queue.get_next("w1")
    assert isinstance(work, ManagementCommand)
    assert work.command is CommandType.PAUSE


@pytest.mark.asyncio
async def test_wdrr_prefers_higher_weight(queue: PullQueue) -> None:
    await queue.schedule(Task(priority="low", handler_name="x", payload={"n": "l"}))
    await queue.schedule(Task(priority="high", handler_name="x", payload={"n": "h"}))
    first = await queue.get_next("w")
    assert isinstance(first, Task)
    assert first.payload["n"] == "h"


@pytest.mark.asyncio
async def test_no_work_when_empty(queue: PullQueue) -> None:
    work = await queue.get_next("w")
    assert isinstance(work, NoWork)
    assert work.reason is NoWorkReason.ALL_PRIORITIES_STARVED


@pytest.mark.asyncio
async def test_heartbeat_callback(repo: InMemoryTaskRepository) -> None:
    calls: list[str] = []

    async def beat(wid: str) -> None:
        calls.append(wid)

    q = PullQueue(repo, config=PullQueueConfig(on_heartbeat=beat))
    await q.get_next("wh")
    assert calls == ["wh"]
