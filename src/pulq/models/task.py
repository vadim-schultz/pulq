"""Task document model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from pulq.models.capabilities import TaskExecutionAny, TaskExecutionRequirement, WorkerContext
from pulq.models.enums import TaskStatus

__all__ = ["Task"]


class Task(BaseModel):
    """A unit of work with a priority bucket for WDRR scheduling."""

    type: Literal["task"] = "task"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    priority: str
    handler_name: str = Field(
        description="Name of the handler on the worker that will execute this task",
    )
    payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_worker_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    execution_target: TaskExecutionRequirement = Field(
        default_factory=TaskExecutionAny,
        description="Capability requirement; default is match-any-worker",
    )

    @field_validator("execution_target", mode="before")
    @classmethod
    def _execution_target_null_is_any(cls, v: object) -> object:
        if v is None:
            return TaskExecutionAny()
        return v

    def assignable_by(self, worker: WorkerContext) -> bool:
        """Return whether ``worker`` satisfies this task's execution target."""
        return self.execution_target.satisfies(worker)
