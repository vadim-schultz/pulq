"""Pydantic models for tasks, work items, and scheduler configuration."""

from __future__ import annotations

from pulq.models.capabilities import (
    DEFAULT_WORKER_CONTEXT,
    AdvertisedComponent,
    ComponentRequirement,
    TaskConstraints,
    TaskExecutionAny,
    TaskExecutionConstraints,
    TaskExecutionDigest,
    TaskExecutionRequirement,
    TaskExecutionSetup,
    WorkerContext,
)
from pulq.models.enums import CommandType, NoWorkReason, TaskStatus
from pulq.models.http import (
    ReportCompletionRequest,
    ReportCompletionResponse,
    RequestWorkRequest,
    ScheduleTaskRequest,
    SendCommandRequest,
    WorkResponseBody,
)
from pulq.models.pending_claim import (
    PendingClaimed,
    PendingDequeExhausted,
    PendingPriorityScanResult,
)
from pulq.models.scheduler_config import DeficitSchedulerConfig
from pulq.models.task import Task
from pulq.models.unions import ClaimResult, WorkResponse
from pulq.models.work import ManagementCommand, NoPendingTask, NoWork
from pulq.models.worker_config import WorkerConfig

__all__ = [
    "DEFAULT_WORKER_CONTEXT",
    "AdvertisedComponent",
    "ClaimResult",
    "CommandType",
    "ComponentRequirement",
    "DeficitSchedulerConfig",
    "ManagementCommand",
    "NoPendingTask",
    "NoWork",
    "NoWorkReason",
    "PendingClaimed",
    "PendingDequeExhausted",
    "PendingPriorityScanResult",
    "ReportCompletionRequest",
    "ReportCompletionResponse",
    "RequestWorkRequest",
    "ScheduleTaskRequest",
    "SendCommandRequest",
    "Task",
    "TaskConstraints",
    "TaskExecutionAny",
    "TaskExecutionConstraints",
    "TaskExecutionDigest",
    "TaskExecutionRequirement",
    "TaskExecutionSetup",
    "TaskStatus",
    "WorkResponse",
    "WorkResponseBody",
    "WorkerConfig",
    "WorkerContext",
]
