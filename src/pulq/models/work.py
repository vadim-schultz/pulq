"""Management commands and null-object work responses."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from pulq.models.enums import CommandType, NoWorkReason

__all__ = ["ManagementCommand", "NoPendingTask", "NoWork"]


class ManagementCommand(BaseModel):
    """High-priority instruction for a specific worker."""

    type: Literal["command"] = "command"
    command: CommandType
    worker_id: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NoWork(BaseModel):
    """Null object: pull succeeded but there is nothing to execute."""

    type: Literal["no_work"] = "no_work"
    reason: NoWorkReason = NoWorkReason.QUEUE_EMPTY


class NoPendingTask(BaseModel):
    """Null object: no pending task for this priority given the worker's advertised capabilities."""

    type: Literal["no_pending"] = "no_pending"
    priority: str
    had_capability_mismatch: bool = Field(
        default=False,
        description="True when pending tasks existed but none matched the worker context",
    )
