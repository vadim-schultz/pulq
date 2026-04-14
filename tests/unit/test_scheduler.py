"""Tests for :class:`~pulq.core.scheduler.DeficitScheduler` and config."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pulq.core.scheduler import DeficitScheduler, DeficitSchedulerConfig


def test_quantum_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        DeficitSchedulerConfig(priority_order=("a",), weights={"a": 1}, quantum=0)


def test_weights_must_cover_priorities() -> None:
    with pytest.raises(ValidationError, match="weights missing"):
        DeficitSchedulerConfig(priority_order=("a", "b"), weights={"a": 1}, quantum=1)


def test_extra_weights_rejected() -> None:
    with pytest.raises(ValidationError, match="unknown priorities"):
        DeficitSchedulerConfig(priority_order=("a",), weights={"a": 1, "b": 1}, quantum=1)


def test_epoch_credit_and_debit() -> None:
    cfg = DeficitSchedulerConfig(priority_order=("hi", "lo"), weights={"hi": 3, "lo": 1}, quantum=1)
    s = DeficitScheduler(cfg)
    assert s.is_epoch_complete
    s.credit_all()
    assert s.claimable_priorities == ("hi", "lo")
    s.debit("hi")
    s.zero_out("lo")
    assert s.claimable_priorities == ("hi",)


def test_claimable_respects_quantum() -> None:
    cfg = DeficitSchedulerConfig(priority_order=("a",), weights={"a": 4}, quantum=2)
    s = DeficitScheduler(cfg)
    s.credit_all()
    assert s.claimable_priorities == ("a",)
    s.debit("a")
    assert s.claimable_priorities == ("a",)
    s.debit("a")
    assert s.claimable_priorities == ()
