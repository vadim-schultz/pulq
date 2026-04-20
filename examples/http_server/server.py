"""Litestar app exposing :class:`~pulq.core.pull_queue.PullQueue` over HTTP (example only)."""

from __future__ import annotations

import argparse
from typing import Any

import uvicorn
from litestar import Litestar, Router, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND

from pulq import InMemoryTaskRepository, PullQueue
from pulq.errors import TaskNotFoundError
from pulq.models.http import (
    ReportCompletionRequest,
    ReportCompletionResponse,
    RequestWorkRequest,
    ScheduleTaskRequest,
    SendCommandRequest,
)


def create_app(queue: PullQueue) -> Litestar:
    """Build a Litestar app with queue routes under ``/api/queue``."""

    @post("/request_work")
    async def request_work(data: RequestWorkRequest) -> dict[str, Any]:
        work = await queue.get_next(
            data.worker_id,
            worker_context=data.worker_context,
        )
        return work.model_dump(mode="json")

    @post("/complete")
    async def report_completion(data: ReportCompletionRequest) -> ReportCompletionResponse:
        try:
            await queue.mark_complete(data.task_id, data.result)
        except TaskNotFoundError as exc:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        return ReportCompletionResponse(ok=True)

    @post("/schedule")
    async def schedule_task(data: ScheduleTaskRequest) -> dict[str, str]:
        task_id = await queue.schedule(data.task)
        return {"task_id": task_id}

    @get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @post("/send_command")
    async def send_command(data: SendCommandRequest) -> dict[str, bool]:
        queue.send_command(data.worker_id, data.command)
        return {"ok": True}

    queue_router = Router(
        path="/api/queue",
        route_handlers=[
            request_work,
            report_completion,
            schedule_task,
            health,
            send_command,
        ],
    )
    return Litestar(route_handlers=[queue_router])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the pulq HTTP queue example server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    repo = InMemoryTaskRepository()
    queue = PullQueue(repo)
    app = create_app(queue)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
