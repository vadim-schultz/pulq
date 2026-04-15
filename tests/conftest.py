"""Pytest fixtures."""

from __future__ import annotations

import pytest

from pulq import InMemoryTaskRepository, PullQueue


@pytest.fixture
def repo() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()


@pytest.fixture
def queue(repo: InMemoryTaskRepository) -> PullQueue:
    return PullQueue(repo)
