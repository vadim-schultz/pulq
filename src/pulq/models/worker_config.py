"""Pydantic configuration for :class:`~pulq.core.worker.Worker`."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pulq.models.task import Task

__all__ = ["WorkerConfig", "WorkerHooks"]


class WorkerHooks(BaseModel):
    """Lifecycle hooks for worker processing."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    startup: Callable[[], Awaitable[None]] | None = Field(default=None, exclude=True)
    shutdown: Callable[[], Awaitable[None]] | None = Field(default=None, exclude=True)
    before_process: Callable[[Task], Awaitable[None]] | None = Field(
        default=None,
        exclude=True,
    )
    after_process: Callable[[Task, Mapping[str, Any]], Awaitable[None]] | None = Field(
        default=None,
        exclude=True,
    )


class WorkerConfig(BaseModel):
    """Validated parameters for :class:`~pulq.core.worker.Worker`."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    no_work_delay_seconds: float = Field(
        default=0.01,
        ge=0,
        description="Sleep duration after :class:`~pulq.models.NoWork` before polling again",
    )
    hooks: WorkerHooks = Field(default_factory=WorkerHooks)
