"""Pytest fixtures."""

from __future__ import annotations

import pytest

from pulq import InMemoryTaskRepository, PullQueue


@pytest.fixture
def repo() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()


@pytest.fixture
def queue(repo: InMemoryTaskRepository) -> PullQueue:
    return PullQueue(
        repo,
        priority_order=("high", "medium", "low"),
        weights={"high": 3, "medium": 2, "low": 1},
        quantum=1,
    )
