"""Tests for :class:`~pulq.core.dispatcher.CommandDispatcher`."""

from __future__ import annotations

from pulq import CommandType, ManagementCommand
from pulq.core.dispatcher import CommandDispatcher


def test_enqueue_and_take() -> None:
    d = CommandDispatcher()
    assert not d.has_pending_for("w1")
    d.send("w1", CommandType.STOP)
    assert d.has_pending_for("w1")
    cmd = d.take_next_for("w1")
    assert isinstance(cmd, ManagementCommand)
    assert cmd.command is CommandType.STOP
    assert cmd.worker_id == "w1"
