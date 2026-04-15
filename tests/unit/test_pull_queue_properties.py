"""PullQueue dependency injection surface."""

from __future__ import annotations

from pulq import InMemoryTaskRepository, PullQueue, PullQueueConfig
from pulq.core.dispatcher import CommandDispatcher
from pulq.models.scheduler_config import DeficitSchedulerConfig


def test_injected_commands_and_scheduler_from_config() -> None:
    repo = InMemoryTaskRepository()
    disp = CommandDispatcher()
    cfg = DeficitSchedulerConfig(priority_order=("a",), weights={"a": 1}, quantum=1)
    q = PullQueue(repo, config=PullQueueConfig(scheduler=cfg, commands=disp))
    assert q.commands is disp
    assert q.deficits.priority_order == ("a",)
    assert q.deficits.weights == {"a": 1}
