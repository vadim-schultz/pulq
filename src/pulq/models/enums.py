"""Enumerations shared by task and work-item models."""

from __future__ import annotations

from enum import StrEnum

__all__ = ["CommandType", "NoWorkReason", "TaskStatus"]


class TaskStatus(StrEnum):
    """Lifecycle state of a task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CommandType(StrEnum):
    """Management commands targeted at a worker."""

    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"


class NoWorkReason(StrEnum):
    """Why the queue returned no schedulable work."""

    QUEUE_EMPTY = "queue_empty"
    ALL_PRIORITIES_STARVED = "all_priorities_starved"
    NO_CAPABLE_TASKS = "no_capable_tasks"
