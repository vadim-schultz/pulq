"""Match worker context against task execution requirements."""

from __future__ import annotations

from pulq.core.component_match import match_hw_requirement
from pulq.models.capabilities import (
    DEFAULT_WORKER_CONTEXT,
    TaskExecutionAny,
    TaskExecutionRequirement,
    WorkerContext,
)

__all__ = ["match_hw_requirement", "satisfies"]

_DEFAULT_ANY = TaskExecutionAny()


def satisfies(
    worker: WorkerContext = DEFAULT_WORKER_CONTEXT,
    requirement: TaskExecutionRequirement = _DEFAULT_ANY,
) -> bool:
    """Return whether ``worker`` satisfies ``requirement``.

    Delegates to :meth:`~pulq.models.capabilities.TaskExecutionAny.satisfies` and siblings.
    Defaults model a missing pull: :data:`~pulq.models.capabilities.DEFAULT_WORKER_CONTEXT`
    and :class:`~pulq.models.capabilities.TaskExecutionAny`. Non-wildcard requirements
    do not match the empty worker context.
    """
    return requirement.satisfies(worker)
