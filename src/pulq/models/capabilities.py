"""Worker capability advertisement and task execution requirements."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

__all__ = [
    "DEFAULT_WORKER_CONTEXT",
    "AdvertisedComponent",
    "ComponentRequirement",
    "TaskConstraints",
    "TaskExecutionAny",
    "TaskExecutionConstraints",
    "TaskExecutionDigest",
    "TaskExecutionRequirement",
    "TaskExecutionSetup",
    "WorkerContext",
]


class AdvertisedComponent(BaseModel):
    """Worker-advertised state for one component (software, hardware, optional parameter bag)."""

    software_version: str | None = Field(
        default=None,
        description="Reported version string evaluated with PEP 440 when constrained",
    )
    hardware_version: str | None = Field(
        default=None,
        description="Opaque hardware identity string matched with exact string equality",
    )
    parameters: dict[str, Any] | None = Field(
        default=None,
        description="Optional bag included in per-component digest checks",
    )

    @model_validator(mode="after")
    def at_least_one_axis(self) -> Self:
        if (
            self.software_version is None
            and self.hardware_version is None
            and self.parameters is None
        ):
            msg = (
                "AdvertisedComponent requires at least one of: "
                "software_version, hardware_version, parameters"
            )
            raise ValueError(msg)
        return self

    def satisfies(self, required: ComponentRequirement) -> bool:
        """Return whether this advertisement meets ``required``."""
        from pulq.core.component_match import advertised_satisfies  # noqa: PLC0415

        return advertised_satisfies(self, required)


class ComponentRequirement(BaseModel):
    """Minimum requirement for one component (aligned fields with :class:`AdvertisedComponent`).

    ``software_version`` is a **PEP 440 specifier** constraining the worker's reported
    ``software_version``. ``hardware_version`` is an exact token. ``parameter_digest`` pins the
    JCS+SHA256 digest of the worker's ``parameters`` dict for this component (empty object if
    ``parameters`` is omitted on the worker).
    """

    software_version: str | None = Field(
        default=None,
        description=(
            "PEP 440 specifier; worker reported software_version for component must satisfy it"
        ),
    )
    hardware_version: str | None = Field(
        default=None,
        description="Required hardware token; must equal worker's hardware_version for component",
    )
    parameter_digest: str | None = Field(
        default=None,
        description="If set, digest of worker parameters for this component must match exactly",
    )

    @model_validator(mode="after")
    def at_least_one_requirement(self) -> Self:
        if (
            self.software_version is None
            and self.hardware_version is None
            and self.parameter_digest is None
        ):
            msg = (
                "ComponentRequirement requires at least one of: "
                "software_version, hardware_version, parameter_digest"
            )
            raise ValueError(msg)
        return self

    def __matmul__(self, other: AdvertisedComponent) -> bool:
        """``required @ advertised`` is true if ``advertised.satisfies(required)``."""
        return other.satisfies(self)


class WorkerContext(BaseModel):
    """Aggregate advertisement: setup, digest parameters, and per-component advertisements."""

    setup_name: str | None = None
    parameters: dict[str, Any] | None = None
    components: dict[str, AdvertisedComponent] = Field(
        default_factory=dict,
        description="Component id → advertised software/hardware/parameters",
    )


DEFAULT_WORKER_CONTEXT = WorkerContext()
"""Omitted-pull default: empty advertisement (module singleton; do not mutate in place)."""


class TaskConstraints(BaseModel):
    """Per-component requirements (component id → minimum) vs :class:`WorkerContext`."""

    components: dict[str, ComponentRequirement] = Field(default_factory=dict)

    def satisfied_by(self, worker: WorkerContext) -> bool:
        """Return whether ``worker`` meets every per-component requirement."""
        for comp_id, required in self.components.items():
            advertised = worker.components.get(comp_id)
            if advertised is None or not advertised.satisfies(required):
                return False
        return True


class TaskExecutionAny(BaseModel):
    """Explicit match-any-worker requirement."""

    kind: Literal["any"] = "any"

    def satisfies(self, worker: WorkerContext) -> bool:  # noqa: ARG002
        """Always true: any worker may run the task."""
        return True


class TaskExecutionSetup(BaseModel):
    """Require the worker's setup name to match exactly."""

    kind: Literal["setup"] = "setup"
    setup_name: str = Field(min_length=1)

    def satisfies(self, worker: WorkerContext) -> bool:
        return worker.setup_name == self.setup_name


class TaskExecutionDigest(BaseModel):
    """Require the worker parameter digest (JCS + SHA-256) to match exactly."""

    kind: Literal["digest"] = "digest"
    required_digest: str = Field(min_length=1)

    def satisfies(self, worker: WorkerContext) -> bool:
        from pulq.core.capability_digest import compute_capability_digest  # noqa: PLC0415

        params = worker.parameters if worker.parameters is not None else {}
        return compute_capability_digest(params) == self.required_digest


class TaskExecutionConstraints(BaseModel):
    """Structured constraint set evaluated against worker context resources."""

    kind: Literal["constraints"] = "constraints"
    constraints: TaskConstraints

    def satisfies(self, worker: WorkerContext) -> bool:
        return self.constraints.satisfied_by(worker)


TaskExecutionRequirement = Annotated[
    TaskExecutionAny | TaskExecutionSetup | TaskExecutionDigest | TaskExecutionConstraints,
    Field(discriminator="kind"),
]
