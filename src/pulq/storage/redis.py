"""Redis-backed task repository for multi-process / durable scheduling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from redis.asyncio.lock import Lock

if TYPE_CHECKING:
    from redis.asyncio import Redis

from pulq.errors import TaskNotFoundError
from pulq.models import NoPendingTask, PendingClaimed, PendingDequeExhausted, Task, TaskStatus
from pulq.models.capabilities import DEFAULT_WORKER_CONTEXT, WorkerContext
from pulq.storage._claim import scan_pending_ids_for_claim

__all__ = ["RedisTaskRepository"]

_TASK_HASH_FIELD = "data"


class RedisTaskRepository:
    """FIFO pending lists per priority with atomic claim via per-priority Redis lock.

    Keys (``key_namespace`` defaults to ``pulq``; hash tag for Redis Cluster)::

        {ns}:q:{priority}   — LIST of task ids (RPUSH on schedule)
        {ns}:t:{task_id}   — HASH field ``data`` — JSON task document

    Requires ``decode_responses=True`` on the :class:`~redis.asyncio.Redis` client so that
    string payloads round-trip without manual decoding.
    """

    def __init__(
        self,
        redis: Redis,
        *,
        key_namespace: str = "pulq",
        lock_timeout: float = 10.0,
        lock_blocking_timeout: float | None = 30.0,
    ) -> None:
        self._redis = redis
        self._ns = key_namespace
        self._lock_timeout = lock_timeout
        self._lock_blocking_timeout = lock_blocking_timeout

    def _q_key(self, priority: str) -> str:
        return f"{{{self._ns}}}:q:{priority}"

    def _task_key(self, task_id: str) -> str:
        return f"{{{self._ns}}}:t:{task_id}"

    def _claim_lock(self, priority: str) -> Lock:
        return Lock(
            self._redis,
            name=f"{{{self._ns}}}:claim:{priority}",
            timeout=self._lock_timeout,
            blocking_timeout=self._lock_blocking_timeout,
        )

    @staticmethod
    def _decode_redis_str(value: str | bytes) -> str:
        return value.decode() if isinstance(value, bytes) else value

    async def _lrange_pending_ids(self, q_key: str) -> list[str]:
        """Return task ids in queue order (FIFO), or empty if the list is missing/empty."""
        # redis stubs union Awaitable[T] with T; async client always returns a coroutine.
        raw_ids = await cast("Any", self._redis.lrange(q_key, 0, -1))
        return [self._decode_redis_str(x) for x in raw_ids]

    async def _pending_tasks_in_id_order(
        self,
        ids: list[str],
    ) -> tuple[list[str], dict[str, Task]]:
        """Pipelined HGET of task JSON per id; preserve order; omit ids with missing hash."""
        pipe = self._redis.pipeline()
        for tid in ids:
            pipe.hget(self._task_key(tid), _TASK_HASH_FIELD)
        raws = await pipe.execute()

        tasks: dict[str, Task] = {}
        ordered: list[str] = []
        for tid, raw in zip(ids, raws, strict=True):
            if raw is None:
                continue
            tasks[tid] = Task.model_validate_json(self._decode_redis_str(raw))
            ordered.append(tid)
        return ordered, tasks

    async def _pending_queue_snapshot(
        self,
        q_key: str,
    ) -> tuple[list[str], dict[str, Task]]:
        """Ordered pending ids + task rows for the in-memory claim scan (see memory repo)."""
        ids = await self._lrange_pending_ids(q_key)
        if not ids:
            return [], {}
        return await self._pending_tasks_in_id_order(ids)

    async def _persist_after_claim_scan(
        self,
        q_key: str,
        new_order: list[str],
        outcome: PendingClaimed | PendingDequeExhausted,
    ) -> None:
        """Rewrite the pending list and persist RUNNING state when a task was claimed."""
        pipe = self._redis.pipeline()
        pipe.delete(q_key)
        if new_order:
            pipe.rpush(q_key, *new_order)
        if isinstance(outcome, PendingClaimed):
            t = outcome.task
            pipe.hset(self._task_key(t.id), _TASK_HASH_FIELD, t.model_dump_json())
        await pipe.execute()

    async def schedule(self, task: Task) -> str:
        """Enqueue a pending task under its priority bucket."""
        if task.status != TaskStatus.PENDING:
            msg = "Can only schedule tasks in PENDING status"
            raise ValueError(msg)
        payload = task.model_dump_json()
        q_key = self._q_key(task.priority)
        t_key = self._task_key(task.id)
        pipe = self._redis.pipeline()
        pipe.rpush(q_key, task.id)
        pipe.hset(t_key, _TASK_HASH_FIELD, payload)
        await pipe.execute()
        return task.id

    async def claim_next_pending(
        self,
        priority: str,
        worker_id: str,
        *,
        worker_context: WorkerContext = DEFAULT_WORKER_CONTEXT,
    ) -> Task | NoPendingTask:
        """Pop the next pending task for ``priority`` that matches ``worker_context``.

        Under the per-priority lock, the pending id list and task rows are loaded, the same
        scan as :class:`~pulq.storage.memory.InMemoryTaskRepository` runs in process, then
        the queue and claimed task document are written back atomically in one pipeline.
        """
        async with self._claim_lock(priority):
            q_key = self._q_key(priority)
            ids, tasks = await self._pending_queue_snapshot(q_key)
            new_order, outcome = scan_pending_ids_for_claim(
                ids,
                tasks,
                worker_context,
                worker_id,
            )
            await self._persist_after_claim_scan(q_key, new_order, outcome)

        if isinstance(outcome, PendingClaimed):
            return outcome.task
        return NoPendingTask(
            priority=priority,
            had_capability_mismatch=outcome.had_capability_mismatch,
        )

    async def mark_complete(self, task_id: str, result: dict[str, Any]) -> Task:
        """Mark task completed unless ``result`` contains ``\"ok\": False``."""
        t_key = self._task_key(task_id)
        raw = await cast("Any", self._redis.hget(t_key, _TASK_HASH_FIELD))
        if raw is None:
            raise TaskNotFoundError(task_id)
        task = Task.model_validate_json(self._decode_redis_str(raw))
        ok = result.get("ok", True)
        new_status = TaskStatus.COMPLETED if ok else TaskStatus.FAILED
        updated = task.model_copy(update={"status": new_status}, deep=True)
        await cast("Any", self._redis.hset(t_key, _TASK_HASH_FIELD, updated.model_dump_json()))
        return updated
