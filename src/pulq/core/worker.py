"""Async worker that pulls tasks via a :class:`~pulq.types.Transport`."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from pulq.models import CommandType, ManagementCommand, NoWork, Task
from pulq.types import TaskHandler, Transport

__all__ = ["Worker"]

logger = logging.getLogger(__name__)


class Worker:
    """Pull loop: commands, tasks, and optional backoff on :class:`~pulq.models.NoWork`."""

    def __init__(
        self,
        transport: Transport,
        worker_id: str,
        handler: TaskHandler,
        *,
        no_work_delay_seconds: float = 0.0,
        startup: Callable[[], Awaitable[None]] | None = None,
        shutdown: Callable[[], Awaitable[None]] | None = None,
        before_process: Callable[[Task], Awaitable[None]] | None = None,
        after_process: Callable[[Task, Mapping[str, Any]], Awaitable[None]] | None = None,
    ) -> None:
        self._transport = transport
        self._worker_id = worker_id
        self._handler = handler
        self._no_work_delay_seconds = no_work_delay_seconds
        self._startup = startup
        self._shutdown = shutdown
        self._before_process = before_process
        self._after_process = after_process

    @property
    def worker_id(self) -> str:
        """Stable worker identity used when pulling work."""
        return self._worker_id

    async def run(self) -> None:
        """Run until a :class:`~pulq.models.CommandType.STOP` command is received."""
        if self._startup is not None:
            await self._startup()
        try:
            await self._loop()
        finally:
            if self._shutdown is not None:
                await self._shutdown()

    async def _loop(self) -> None:
        while True:
            work = await self._transport.request_work(self._worker_id)
            if isinstance(work, NoWork):
                if self._no_work_delay_seconds > 0:
                    await asyncio.sleep(self._no_work_delay_seconds)
                    # TODO: add "terminate when exhausted" parameter / logic
                continue
            if isinstance(work, ManagementCommand):
                if work.command is CommandType.STOP:
                    logger.info("Worker %s received STOP", self._worker_id)
                    return
                logger.debug("Worker %s ignoring command %s", self._worker_id, work.command)
                continue
            # TODO: add handler factory for each task type
            assert isinstance(work, Task)
            result: dict[str, Any] = {}
            if self._before_process is not None:
                await self._before_process(work)
            try:
                out = await self._handler(work)
                result = dict(out) if out is not None else {}
            except Exception as exc:
                logger.exception("Handler failed for task %s", work.id)
                result = {"ok": False, "error": str(exc)}
            finally:
                if self._after_process is not None:
                    await self._after_process(work, result)
            await self._transport.report_completion(work.id, result)
