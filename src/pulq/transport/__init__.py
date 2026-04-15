"""Transports for worker ↔ queue communication."""

from __future__ import annotations

from pulq.transport.local import LocalTransport

__all__ = ["HttpTransport", "LocalTransport"]


def __getattr__(name: str) -> object:
    if name == "HttpTransport":
        from pulq.transport.http import HttpTransport as HttpTransport_cls

        return HttpTransport_cls
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
