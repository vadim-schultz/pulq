"""Schedule example tasks on the HTTP queue server."""

from __future__ import annotations

import argparse
import asyncio

import httpx

from pulq import Task
from pulq.models.http import ScheduleTaskRequest


async def main() -> None:
    parser = argparse.ArgumentParser(description="POST tasks to the pulq HTTP example server")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    tasks = [
        Task(priority="high", handler_name="echo", payload={"job": "a"}),
        Task(priority="medium", handler_name="echo", payload={"job": "b"}),
    ]

    async with httpx.AsyncClient(base_url=base, timeout=30.0) as client:
        for t in tasks:
            body = ScheduleTaskRequest(task=t).model_dump(mode="json")
            r = await client.post("/api/queue/schedule", json=body)
            r.raise_for_status()
            print("scheduled:", r.json())


if __name__ == "__main__":
    asyncio.run(main())
