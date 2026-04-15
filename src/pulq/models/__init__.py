"""Pydantic models for tasks, work items, and scheduler configuration."""

from __future__ import annotations

from pulq.models.enums import CommandType, NoWorkReason, TaskStatus
from pulq.models.http import (
    ReportCompletionRequest,
    ReportCompletionResponse,
    RequestWorkRequest,
    ScheduleTaskRequest,
    SendCommandRequest,
    WorkResponseBody,
)
from pulq.models.scheduler_config import DeficitSchedulerConfig
from pulq.models.task import Task
from pulq.models.unions import ClaimResult, WorkResponse
from pulq.models.work import ManagementCommand, NoPendingTask, NoWork
from pulq.models.worker_config import WorkerConfig

__all__ = [
    "ClaimResult",
    "CommandType",
    "DeficitSchedulerConfig",
    "ManagementCommand",
    "NoPendingTask",
    "NoWork",
    "NoWorkReason",
    "ReportCompletionRequest",
    "ReportCompletionResponse",
    "RequestWorkRequest",
    "ScheduleTaskRequest",
    "SendCommandRequest",
    "Task",
    "TaskStatus",
    "WorkResponse",
    "WorkResponseBody",
    "WorkerConfig",
]
