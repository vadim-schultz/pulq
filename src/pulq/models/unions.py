"""Discriminated union type aliases for API boundaries."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from pulq.models.task import Task
from pulq.models.work import ManagementCommand, NoPendingTask, NoWork

__all__ = ["ClaimResult", "WorkResponse"]

WorkResponse = Annotated[
    Task | ManagementCommand | NoWork,
    Field(discriminator="type"),
]

ClaimResult = Annotated[
    Task | NoPendingTask,
    Field(discriminator="type"),
]
