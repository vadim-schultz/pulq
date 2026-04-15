"""Pull queue orchestrating WDRR, management commands, and storage."""

from __future__ import annotations

from typing import Any

from pulq.core.dispatcher import CommandDispatcher
from pulq.core.queue_config import PullQueueConfig
from pulq.core.scheduler import DeficitScheduler
from pulq.models import (
    CommandType,
    NoPendingTask,
    NoWork,
    NoWorkReason,
    Task,
    WorkResponse,
)
from pulq.types import TaskRepository

__all__ = ["PullQueue"]


class PullQueue:
    """Coordinates deficit scheduling, per-worker commands, and task claims.

    Pass ``config`` to customize WDRR (see ``DeficitSchedulerConfig``), inject a
    ``CommandDispatcher``, or set a heartbeat callback.
    Omit ``config`` for the default three-priority (high / medium / low) 3:2:1 setup.
    """

    def __init__(
        self,
        repository: TaskRepository,
        *,
        config: PullQueueConfig | None = None,
    ) -> None:
        cfg = config or PullQueueConfig()
        self._repository = repository
        self._commands = cfg.commands or CommandDispatcher()
        self._deficits = DeficitScheduler(cfg.scheduler)
        self._on_heartbeat = cfg.on_heartbeat

    @property
    def commands(self) -> CommandDispatcher:
        """Management command queues (same instance shared if injected)."""
        return self._commands

    @property
    def deficits(self) -> DeficitScheduler:
        """WDRR deficit ledger."""
        return self._deficits

    async def schedule(self, task: Task) -> str:
        """Enqueue ``task`` for scheduling."""
        return await self._repository.schedule(task)

    def send_command(self, worker_id: str, command: CommandType) -> None:
        """Queue a management command for ``worker_id`` (synchronous enqueue)."""
        self._commands.send(worker_id, command)

    async def mark_complete(self, task_id: str, result: dict[str, Any]) -> None:
        """Mark ``task_id`` complete; ``result`` follows handler conventions."""
        await self._repository.mark_complete(task_id, result)

    async def get_next(self, worker_id: str) -> WorkResponse:
        """Pull the next management command, schedulable task, or :class:`~pulq.models.NoWork`."""
        if self._on_heartbeat is not None:
            await self._on_heartbeat(worker_id)

        if self._commands.has_pending_for(worker_id):
            return self._commands.take_next_for(worker_id)

        return await self._schedule_next_task(worker_id)

    async def _schedule_next_task(self, worker_id: str) -> Task | NoWork:
        """Run the WDRR loop until a task is claimed or scheduling is exhausted."""
        while True:
            was_epoch_start = self._deficits.is_epoch_complete
            if was_epoch_start:
                self._deficits.credit_all()

            made_progress = False
            for priority in self._deficits.claimable_priorities:
                claimed = await self._repository.claim_next_pending(priority, worker_id)
                if isinstance(claimed, Task):
                    self._deficits.debit(priority)
                    return claimed
                if isinstance(claimed, NoPendingTask):
                    self._deficits.zero_out(priority)
                    made_progress = True

            if was_epoch_start or not made_progress:
                return NoWork(reason=NoWorkReason.ALL_PRIORITIES_STARVED)
