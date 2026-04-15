"""Per-worker management command queues."""

from __future__ import annotations

from collections import defaultdict, deque

from pulq.models import CommandType, ManagementCommand

__all__ = ["CommandDispatcher"]


class CommandDispatcher:
    """FIFO of :class:`~pulq.models.ManagementCommand` per ``worker_id``."""

    def __init__(self) -> None:
        self._queues: defaultdict[str, deque[ManagementCommand]] = defaultdict(deque)

    def has_pending_for(self, worker_id: str) -> bool:
        """Whether ``worker_id`` has at least one queued command."""
        return bool(self._queues[worker_id])

    def take_next_for(self, worker_id: str) -> ManagementCommand:
        """Pop the next command for ``worker_id`` (must call :meth:`has_pending_for` first)."""
        return self._queues[worker_id].popleft()

    def enqueue(self, worker_id: str, command: ManagementCommand) -> None:
        """Append a management command for ``worker_id``."""
        self._queues[worker_id].append(command)

    def send(self, worker_id: str, command: CommandType) -> None:
        """Enqueue a command built from ``command`` enum and ``worker_id``."""
        self.enqueue(worker_id, ManagementCommand(command=command, worker_id=worker_id))
