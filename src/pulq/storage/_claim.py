"""Shared pending-queue scan logic for task repositories (memory, Redis, …)."""

from __future__ import annotations

from collections import deque

from pulq.models import PendingClaimed, PendingDequeExhausted, Task, TaskStatus
from pulq.models.capabilities import WorkerContext

__all__ = [
    "running_claim_copy",
    "scan_pending_deque_for_claim",
    "scan_pending_ids_for_claim",
]


def running_claim_copy(task: Task, worker_id: str) -> Task:
    """Return a deep copy of ``task`` marked RUNNING and assigned to ``worker_id``."""
    return task.model_copy(
        update={
            "status": TaskStatus.RUNNING,
            "assigned_worker_id": worker_id,
        },
        deep=True,
    )


def scan_pending_deque_for_claim(
    q: deque[str],
    tasks: dict[str, Task],
    worker_context: WorkerContext,
    worker_id: str,
) -> PendingClaimed | PendingDequeExhausted:
    """Pop ids from ``q`` until a PENDING task assignable to ``worker_context`` is claimed."""
    initial_len = len(q)
    had_capability_mismatch = False
    for _ in range(initial_len):
        if not q:
            break
        task_id = q.popleft()
        stored = tasks[task_id]
        if stored.status != TaskStatus.PENDING:
            continue
        if not stored.assignable_by(worker_context):
            q.append(task_id)
            had_capability_mismatch = True
            continue
        claimed = running_claim_copy(stored, worker_id)
        tasks[task_id] = claimed
        return PendingClaimed(task=claimed)
    return PendingDequeExhausted(had_capability_mismatch=had_capability_mismatch)


def scan_pending_ids_for_claim(
    ids: list[str],
    tasks: dict[str, Task],
    worker_context: WorkerContext,
    worker_id: str,
) -> tuple[list[str], PendingClaimed | PendingDequeExhausted]:
    """Rotate a FIFO id list like :func:`scan_pending_deque_for_claim`; mutates ``tasks`` on claim.

    Returns the resulting queue order (what should be persisted for the pending list) and
    the scan outcome.
    """
    q = deque(ids)
    outcome = scan_pending_deque_for_claim(q, tasks, worker_context, worker_id)
    return list(q), outcome
