"""Parse untrusted mappings into typed work and claim results."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from pulq.models import ManagementCommand, NoPendingTask, NoWork, Task
from pulq.models.unions import ClaimResult, WorkResponse

__all__ = ["parse_claim_result", "parse_work_response"]

_work_response_adapter: TypeAdapter[Task | ManagementCommand | NoWork] = TypeAdapter(WorkResponse)
_claim_result_adapter: TypeAdapter[Task | NoPendingTask] = TypeAdapter(ClaimResult)


def parse_work_response(data: dict[str, Any]) -> Task | ManagementCommand | NoWork:
    """Parse a mapping into a ``WorkResponse`` union using Pydantic discriminated union."""
    return _work_response_adapter.validate_python(data)


def parse_claim_result(data: dict[str, Any]) -> Task | NoPendingTask:
    """Parse a mapping into a ``ClaimResult`` union using Pydantic discriminated union."""
    return _claim_result_adapter.validate_python(data)
