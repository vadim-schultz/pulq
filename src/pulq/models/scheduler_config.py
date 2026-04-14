"""Pydantic configuration for WDRR deficit scheduling."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

__all__ = ["DeficitSchedulerConfig"]


class DeficitSchedulerConfig(BaseModel):
    """Validated parameters for :class:`~pulq.core.scheduler.DeficitScheduler`.

    With no arguments, defaults match the common three-tier setup: priorities
    ``("high", "medium", "low")`` and weights ``3:2:1`` with ``quantum`` 1.

    ``priority_order`` defines visit order among buckets that share a claimable
    deficit. ``weights`` must contain exactly one positive integer weight per
    priority in ``priority_order``, and no other keys.
    """

    model_config = ConfigDict(frozen=True)

    priority_order: tuple[str, ...] = Field(
        default_factory=lambda: ("high", "medium", "low"),
    )
    weights: dict[str, int] = Field(
        default_factory=lambda: {"high": 3, "medium": 2, "low": 1},
    )
    quantum: int = Field(default=1, ge=1, description="Deficit debited per successful claim")

    @field_validator("weights", mode="after")
    @classmethod
    def weights_include_all_priorities(
        cls,
        weights: dict[str, int],
        info: ValidationInfo,
    ) -> dict[str, int]:
        priority_order = info.data["priority_order"]
        missing = [p for p in priority_order if p not in weights]
        if missing:
            msg = f"weights missing for priorities: {missing}"
            raise ValueError(msg)
        return weights

    @field_validator("weights", mode="after")
    @classmethod
    def weights_have_no_unknown_priorities(
        cls,
        weights: dict[str, int],
        info: ValidationInfo,
    ) -> dict[str, int]:
        priority_order = info.data["priority_order"]
        extra = [p for p in weights if p not in priority_order]
        if extra:
            msg = f"weights contain unknown priorities vs order: {extra}"
            raise ValueError(msg)
        return weights
