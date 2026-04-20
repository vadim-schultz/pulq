"""JCS (RFC 8785) canonical digest for worker capability parameter bags."""

from __future__ import annotations

import hashlib
import importlib
from typing import Any

__all__ = ["compute_capability_digest"]


def compute_capability_digest(parameters: dict[str, Any]) -> str:
    """Return SHA-256 hex of the RFC 8785 canonical JSON encoding of ``parameters``.

    Install ``pulq[capabilities]`` (includes ``rfc8785``) to use this function.
    """
    try:
        rfc8785 = importlib.import_module("rfc8785")
    except ImportError as exc:  # pragma: no cover - exercised when extra missing
        msg = (
            "compute_capability_digest requires the 'rfc8785' package (install pulq[capabilities])"
        )
        raise ImportError(msg) from exc

    canonical = rfc8785.dumps(parameters)
    return hashlib.sha256(canonical).hexdigest()
