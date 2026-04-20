"""Storage backends."""

from __future__ import annotations

from pulq.storage.memory import InMemoryTaskRepository

__all__ = ["InMemoryTaskRepository", "RedisTaskRepository"]


def __getattr__(name: str) -> object:
    if name == "RedisTaskRepository":
        from pulq.storage.redis import RedisTaskRepository as RedisTaskRepository_cls

        return RedisTaskRepository_cls
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
