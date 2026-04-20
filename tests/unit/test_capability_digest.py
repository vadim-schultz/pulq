"""Unit tests for JCS-based capability digests."""

from __future__ import annotations

from pulq.core.capability_digest import compute_capability_digest


def test_digest_stable_under_key_reordering() -> None:
    a = compute_capability_digest({"z": 1, "a": 2})
    b = compute_capability_digest({"a": 2, "z": 1})
    assert a == b


def test_digest_differs_for_different_values() -> None:
    x = compute_capability_digest({"cpu": 4})
    y = compute_capability_digest({"cpu": 8})
    assert x != y
