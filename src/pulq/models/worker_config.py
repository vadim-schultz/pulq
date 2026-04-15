"""Pydantic configuration for :class:`~pulq.core.worker.Worker`."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["WorkerConfig"]


class WorkerConfig(BaseModel):
    """Validated parameters for :class:`~pulq.core.worker.Worker`."""

    model_config = ConfigDict(frozen=True)

    no_work_delay_seconds: float = Field(
        default=0.01,
        ge=0,
        description="Sleep duration after :class:`~pulq.models.NoWork` before polling again",
    )
