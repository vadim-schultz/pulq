"""PullQueue dependency injection surface."""

from __future__ import annotations

from pulq import InMemoryTaskRepository, PullQueue
from pulq.core.dispatcher import CommandDispatcher
from pulq.core.scheduler import DeficitScheduler, DeficitSchedulerConfig


def test_injected_dispatcher_and_deficits() -> None:
    repo = InMemoryTaskRepository()
    disp = CommandDispatcher()
    cfg = DeficitSchedulerConfig(priority_order=("a",), weights={"a": 1}, quantum=1)
    deficits = DeficitScheduler(cfg)
    q = PullQueue(
        repo,
        priority_order=("a",),
        weights={"a": 1},
        commands=disp,
        deficits=deficits,
    )
    assert q.commands is disp
    assert q.deficits is deficits
