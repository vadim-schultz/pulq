"""Task document model."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from pulq.models.enums import TaskStatus

__all__ = ["Task"]


class Task(BaseModel):
    """A unit of work with a priority bucket for WDRR scheduling."""

    type: Literal["task"] = "task"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    priority: str
    payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_worker_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
