"""Parsing and model validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pulq import (
    CommandType,
    ManagementCommand,
    NoPendingTask,
    NoWork,
    NoWorkReason,
    Task,
)
from pulq.parsing import parse_claim_result, parse_work_response


def test_parse_work_response_task() -> None:
    t = Task(priority="p", handler_name="h", payload={"a": 1})
    parsed = parse_work_response(t.model_dump(mode="json"))
    assert isinstance(parsed, Task)
    assert parsed.priority == "p"


def test_parse_work_response_command() -> None:
    c = ManagementCommand(command=CommandType.STOP, worker_id="w")
    parsed = parse_work_response(c.model_dump(mode="json"))
    assert isinstance(parsed, ManagementCommand)


def test_parse_work_response_no_work() -> None:
    n = NoWork(reason=NoWorkReason.QUEUE_EMPTY)
    parsed = parse_work_response(n.model_dump(mode="json"))
    assert isinstance(parsed, NoWork)


def test_parse_work_response_invalid() -> None:
    with pytest.raises(ValidationError, match="does not match any of the expected tags"):
        parse_work_response({"type": "unknown"})


def test_parse_claim_no_pending() -> None:
    parsed = parse_claim_result(NoPendingTask(priority="x").model_dump(mode="json"))
    assert isinstance(parsed, NoPendingTask)


def test_parse_claim_task() -> None:
    t = Task(priority="p", handler_name="h", payload={})
    parsed = parse_claim_result(t.model_dump(mode="json"))
    assert isinstance(parsed, Task)
