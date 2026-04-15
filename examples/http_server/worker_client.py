"""Example worker: pull tasks from the HTTP queue server."""

from __future__ import annotations

import argparse
import asyncio

from pulq import CommandType, HttpTransport, Task, Worker
from pulq.models.worker_config import WorkerConfig


async def echo(task: Task) -> dict[str, object]:
    return {"ok": True, "echo": task.payload}


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run a worker against the HTTP queue example")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Queue server base URL")
    parser.add_argument("--worker-id", default="worker-1")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    transport = HttpTransport(base_url=base)
    worker = Worker(
        transport,
        args.worker_id,
        echo,
        config=WorkerConfig(no_work_delay_seconds=0.05),
    )

    async def stop_after_short_delay() -> None:
        await asyncio.sleep(0.15)
        await transport.send_command(args.worker_id, CommandType.STOP)

    await asyncio.gather(worker.run(), stop_after_short_delay())


if __name__ == "__main__":
    asyncio.run(main())
