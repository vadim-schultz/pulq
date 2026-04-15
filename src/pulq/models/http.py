"""HTTP API request/response bodies for queue integrations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, RootModel

from pulq.models.enums import CommandType
from pulq.models.task import Task
from pulq.models.work import ManagementCommand, NoWork

__all__ = [
    "ReportCompletionRequest",
    "ReportCompletionResponse",
    "RequestWorkRequest",
    "ScheduleTaskRequest",
    "SendCommandRequest",
    "WorkResponseBody",
]


class RequestWorkRequest(BaseModel):
    """Body for ``POST .../request_work``."""

    worker_id: str = Field(min_length=1)


class WorkResponseBody(RootModel[Task | ManagementCommand | NoWork]):
    """JSON body for a work pull: one of task, command, or no_work."""


class ReportCompletionRequest(BaseModel):
    """Body for ``POST .../complete``."""

    task_id: str = Field(min_length=1)
    result: dict[str, Any] = Field(default_factory=dict)


class ReportCompletionResponse(BaseModel):
    """Acknowledgement after reporting task completion."""

    ok: bool = True


class ScheduleTaskRequest(BaseModel):
    """Body for ``POST .../schedule``."""

    task: Task


class SendCommandRequest(BaseModel):
    """Body for ``POST .../send_command`` (example / dev integration)."""

    worker_id: str = Field(min_length=1)
    command: CommandType
