"""Async worker that pulls tasks via a :class:`~pulq.types.Transport`."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from pulq.core.handler_registry import HandlerRegistry
from pulq.models import CommandType, ManagementCommand, NoWork, Task
from pulq.models.worker_config import WorkerConfig
from pulq.types import TaskHandler, Transport

__all__ = ["Worker"]

logger = logging.getLogger(__name__)


class Worker:
    """Pull loop: commands, tasks, and optional backoff on :class:`~pulq.models.NoWork`.

    Pass ``registry`` as a single :class:`~pulq.types.TaskHandler` or a
    :class:`~pulq.core.handler_registry.HandlerRegistry` with named handlers matching
    :attr:`~pulq.models.task.Task.handler_name`. Lifecycle hooks live on the registry.

    Pass ``config`` for idle delay when the queue returns :class:`~pulq.models.NoWork`.

    :meth:`run` uses ``async with`` the transport (setup before registry startup,
    teardown after registry shutdown) so remote transports keep connections for
    the worker's lifetime.
    """

    def __init__(
        self,
        transport: Transport,
        worker_id: str,
        registry: TaskHandler | HandlerRegistry,
        *,
        config: WorkerConfig | None = None,
    ) -> None:
        cfg = config or WorkerConfig()
        self._transport = transport
        self._worker_id = worker_id
        self._registry = (
            registry if isinstance(registry, HandlerRegistry) else HandlerRegistry(default=registry)
        )
        self._no_work_delay_seconds = cfg.no_work_delay_seconds
        self._worker_context = cfg.worker_context
        self._work_handlers: dict[type[Any], Callable[[Any], Awaitable[bool]]] = {
            NoWork: self._handle_no_work,
            ManagementCommand: self._handle_management_command,
            Task: self._handle_task,
        }

    @property
    def worker_id(self) -> str:
        """Stable worker identity used when pulling work."""
        return self._worker_id

    async def run(self) -> None:
        """Run until a :class:`~pulq.models.CommandType.STOP` command is received."""
        async with self._transport:
            if self._registry.startup is not None:
                await self._registry.startup()
            try:
                await self._loop()
            finally:
                if self._registry.shutdown is not None:
                    await self._registry.shutdown()

    async def _loop(self) -> None:
        while True:
            work = await self._transport.request_work(
                self._worker_id,
                worker_context=self._worker_context,
            )
            if await self._dispatch_work(work):
                return

    async def _dispatch_work(self, work: object) -> bool:
        """Run the handler for this work item's type.

        Returns ``True`` if the worker pull loop should terminate.
        """
        handler = self._work_handlers.get(type(work))
        if handler is None:
            logger.error("Unexpected work type %s", type(work).__name__)
            return False
        return await handler(work)

    async def _handle_no_work(self, _work: NoWork) -> bool:
        if self._no_work_delay_seconds > 0:
            await asyncio.sleep(self._no_work_delay_seconds)
            # TODO: add "terminate when exhausted" parameter / logic
        return False

    async def _handle_management_command(self, work: ManagementCommand) -> bool:
        if work.command is CommandType.STOP:
            logger.info("Worker %s received STOP", self._worker_id)
            return True
        logger.debug("Worker %s ignoring command %s", self._worker_id, work.command)
        return False

    async def _handle_task(self, work: Task) -> bool:
        await self._complete_task(work)
        return False

    async def _complete_task(self, work: Task) -> None:
        result = await self._resolve_task_result(work)
        await self._transport.report_completion(work.id, result)

    async def _resolve_task_result(self, work: Task) -> dict[str, Any]:
        handler = self._registry.get_handler(work.handler_name)
        if handler is not None:
            return await self._run_task_handler(work, handler)
        logger.error(
            "No handler for handler_name=%s on worker %s",
            work.handler_name,
            self._worker_id,
        )
        return {"ok": False, "error": f"No handler for: {work.handler_name}"}

    async def _run_task_handler(self, work: Task, handler: TaskHandler) -> dict[str, Any]:
        if self._registry.before_process is not None:
            await self._registry.before_process(work)
        result: dict[str, Any] = {}
        try:
            out = await handler(work)
            result = dict(out) if out is not None else {}
        except Exception as exc:
            logger.exception("Handler failed for task %s", work.id)
            result = {"ok": False, "error": str(exc)}
        finally:
            if self._registry.after_process is not None:
                await self._registry.after_process(work, result)
        return result
