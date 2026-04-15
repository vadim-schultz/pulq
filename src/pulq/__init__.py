"""PULQ — fair pull-based task scheduling with WDRR."""

from pulq.core import (
    CommandDispatcher,
    DeficitScheduler,
    HandlerRegistry,
    PullQueue,
    PullQueueConfig,
    Worker,
)
from pulq.errors import TaskNotFoundError, TransportHttpError
from pulq.models import (
    ClaimResult,
    CommandType,
    DeficitSchedulerConfig,
    ManagementCommand,
    NoPendingTask,
    NoWork,
    NoWorkReason,
    ReportCompletionRequest,
    ReportCompletionResponse,
    RequestWorkRequest,
    ScheduleTaskRequest,
    SendCommandRequest,
    Task,
    TaskStatus,
    WorkerConfig,
    WorkResponse,
    WorkResponseBody,
)
from pulq.parsing import parse_claim_result, parse_work_response
from pulq.storage import InMemoryTaskRepository
from pulq.transport import LocalTransport
from pulq.types import HeartbeatCallback, TaskHandler, TaskRepository, Transport

# Ergonomic alias matching common naming
Queue = PullQueue

__all__ = [
    "ClaimResult",
    "CommandDispatcher",
    "CommandType",
    "DeficitScheduler",
    "DeficitSchedulerConfig",
    "HandlerRegistry",
    "HeartbeatCallback",
    "HttpTransport",
    "InMemoryTaskRepository",
    "LocalTransport",
    "ManagementCommand",
    "NoPendingTask",
    "NoWork",
    "NoWorkReason",
    "PullQueue",
    "PullQueueConfig",
    "Queue",
    "ReportCompletionRequest",
    "ReportCompletionResponse",
    "RequestWorkRequest",
    "ScheduleTaskRequest",
    "SendCommandRequest",
    "Task",
    "TaskHandler",
    "TaskNotFoundError",
    "TaskRepository",
    "TaskStatus",
    "Transport",
    "TransportHttpError",
    "WorkResponse",
    "WorkResponseBody",
    "Worker",
    "WorkerConfig",
    "parse_claim_result",
    "parse_work_response",
]

__version__ = "0.2.1"


def __getattr__(name: str) -> object:
    if name == "HttpTransport":
        from pulq.transport.http import HttpTransport as HttpTransport_cls

        return HttpTransport_cls
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
