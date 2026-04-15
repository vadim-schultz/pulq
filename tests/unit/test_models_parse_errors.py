"""Negative tests for parsers."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pulq.parsing import parse_claim_result, parse_work_response


def test_parse_claim_invalid() -> None:
    with pytest.raises(ValidationError, match="does not match any of the expected tags"):
        parse_claim_result({"type": "nope"})


def test_parse_work_response_missing_type() -> None:
    with pytest.raises(ValidationError, match="Unable to extract tag"):
        parse_work_response({})
