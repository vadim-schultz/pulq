"""Pydantic configuration for :class:`~pulq.core.pull_queue.PullQueue`."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from pydantic import BaseModel, ConfigDict, Field

from pulq.core.dispatcher import CommandDispatcher
from pulq.models.scheduler_config import DeficitSchedulerConfig

__all__ = ["PullQueueConfig"]


class PullQueueConfig(BaseModel):
    """Validated parameters for :class:`~pulq.core.pull_queue.PullQueue`.

    ``scheduler`` holds WDRR settings; inject ``commands`` for tests or custom
    wiring. ``on_heartbeat`` runs at the start of each
    :meth:`~pulq.core.pull_queue.PullQueue.get_next` call.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    scheduler: DeficitSchedulerConfig = Field(default_factory=DeficitSchedulerConfig)
    commands: CommandDispatcher | None = Field(default=None, exclude=True)
    on_heartbeat: Callable[[str], Awaitable[None]] | None = Field(
        default=None,
        exclude=True,
    )
