"""Worker pull loop."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import TracebackType

from pulq import (
    CommandType,
    DeficitSchedulerConfig,
    InMemoryTaskRepository,
    LocalTransport,
    ManagementCommand,
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
    await q.schedule(Task(priority="high", handler_name="default", payload={"v": 1}))
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


@pytest.mark.asyncio
async def test_worker_calls_transport_setup_and_teardown() -> None:
    """Worker.run uses the transport async context manager (setup / teardown)."""

    class DummyTransport:
        def __init__(self) -> None:
            self.phases: list[str] = []

        async def setup_transport(self) -> None:
            self.phases.append("setup")

        async def teardown_transport(self) -> None:
            self.phases.append("teardown")

        async def __aenter__(self) -> DummyTransport:
            await self.setup_transport()
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            await self.teardown_transport()

        async def request_work(self, worker_id: str) -> ManagementCommand:
            return ManagementCommand(command=CommandType.STOP, worker_id=worker_id)

        async def report_completion(self, task_id: str, result: dict[str, bool]) -> None:
            pass

    transport = DummyTransport()

    async def handle(_task: Task) -> dict[str, bool]:
        return {"ok": True}

    worker = Worker(transport, "w1", handle, config=WorkerConfig(no_work_delay_seconds=0))
    await worker.run()
    assert transport.phases == ["setup", "teardown"]
