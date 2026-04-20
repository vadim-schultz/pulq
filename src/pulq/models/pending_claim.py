"""Result of scanning a priority deque for the next claimable pending task."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from pulq.models.task import Task  # noqa: TC001

__all__ = [
    "PendingClaimed",
    "PendingDequeExhausted",
    "PendingPriorityScanResult",
]


class PendingClaimed(BaseModel):
    """A pending task was claimed (RUNNING copy stored by the repository)."""

    kind: Literal["claimed"] = "claimed"
    task: Task


class PendingDequeExhausted(BaseModel):
    """Scan finished without a claim: empty queue, stale ids only, or no capability match."""

    kind: Literal["exhausted"] = "exhausted"
    had_capability_mismatch: bool = False


PendingPriorityScanResult = Annotated[
    PendingClaimed | PendingDequeExhausted,
    Field(discriminator="kind"),
]
