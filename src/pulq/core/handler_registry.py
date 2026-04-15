"""Named task handlers and lifecycle hooks for :class:`~pulq.core.worker.Worker`."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from pulq.models.task import Task
from pulq.types import TaskHandler

__all__ = ["HandlerRegistry"]


class HandlerRegistry:
    """Maps ``Task.handler_name`` to callables and optional lifecycle hooks.

    Use :class:`HandlerRegistry` for multiple named handlers, or pass a single
    :class:`~pulq.types.TaskHandler` to :class:`~pulq.core.worker.Worker` (it is
    wrapped as ``HandlerRegistry(default=handler)``).
    """

    def __init__(
        self,
        *,
        default: TaskHandler | None = None,
        startup: Callable[[], Awaitable[None]] | None = None,
        shutdown: Callable[[], Awaitable[None]] | None = None,
        before_process: Callable[[Task], Awaitable[None]] | None = None,
        after_process: Callable[[Task, Mapping[str, Any]], Awaitable[None]] | None = None,
        **handlers: TaskHandler,
    ) -> None:
        self._handlers: dict[str, TaskHandler] = dict(handlers)
        self._default = default
        self._startup = startup
        self._shutdown = shutdown
        self._before_process = before_process
        self._after_process = after_process

    def get_handler(self, name: str) -> TaskHandler | None:
        """Return the handler for ``name``, or the default handler if set."""
        return self._handlers.get(name, self._default)

    @property
    def startup(self) -> Callable[[], Awaitable[None]] | None:
        return self._startup

    @property
    def shutdown(self) -> Callable[[], Awaitable[None]] | None:
        return self._shutdown

    @property
    def before_process(self) -> Callable[[Task], Awaitable[None]] | None:
        return self._before_process

    @property
    def after_process(self) -> Callable[[Task, Mapping[str, Any]], Awaitable[None]] | None:
        return self._after_process
