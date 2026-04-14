"""Async worker that pulls tasks via a :class:`~pulq.types.Transport`."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pulq.models import CommandType, ManagementCommand, NoWork, Task
from pulq.models.worker_config import WorkerConfig
from pulq.types import TaskHandler, Transport

__all__ = ["Worker"]

logger = logging.getLogger(__name__)


class Worker:
    """Pull loop: commands, tasks, and optional backoff on :class:`~pulq.models.NoWork`.

    Pass ``config`` for idle delay and lifecycle hooks (``WorkerConfig``).
    Omit ``config`` for a short default backoff when idle and no hooks.
    """

    def __init__(
        self,
        transport: Transport,
        worker_id: str,
        handler: TaskHandler,
        *,
        config: WorkerConfig | None = None,
    ) -> None:
        cfg = config or WorkerConfig()
        self._transport = transport
        self._worker_id = worker_id
        self._handler = handler
        self._no_work_delay_seconds = cfg.no_work_delay_seconds
        self._startup = cfg.hooks.startup
        self._shutdown = cfg.hooks.shutdown
        self._before_process = cfg.hooks.before_process
        self._after_process = cfg.hooks.after_process

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
