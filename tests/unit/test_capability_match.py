"""Unit tests for capability matching."""

from __future__ import annotations

import pytest

from pulq.core.capability_digest import compute_capability_digest
from pulq.core.capability_match import match_hw_requirement, satisfies
from pulq.models.capabilities import (
    DEFAULT_WORKER_CONTEXT,
    AdvertisedComponent,
    ComponentRequirement,
    TaskConstraints,
    TaskExecutionAny,
    TaskExecutionConstraints,
    TaskExecutionDigest,
    TaskExecutionSetup,
    WorkerContext,
)


def test_match_hw_requirement_exact_only() -> None:
    assert match_hw_requirement("rev-a", "rev-a") is True
    assert match_hw_requirement("rev-a", "rev-b") is False


def test_satisfies_default_any_requirement() -> None:
    assert satisfies() is True
    assert satisfies(WorkerContext()) is True


def test_satisfies_any() -> None:
    assert satisfies(DEFAULT_WORKER_CONTEXT, TaskExecutionAny()) is True
    assert satisfies(WorkerContext(), TaskExecutionAny()) is True


def test_satisfies_setup() -> None:
    req = TaskExecutionSetup(setup_name="lab-1")
    worker_ok = WorkerContext(setup_name="lab-1")
    assert req.satisfies(worker_ok) is True
    assert satisfies(worker_ok, req) is req.satisfies(worker_ok)
    assert satisfies(WorkerContext(setup_name="lab-2"), req) is False
    assert satisfies(requirement=req) is False


def test_satisfies_digest() -> None:
    params = {"threads": 8, "cpu": 4}
    digest = compute_capability_digest(params)
    req = TaskExecutionDigest(required_digest=digest)
    worker = WorkerContext(parameters=params)
    assert satisfies(worker, req) is True
    assert satisfies(WorkerContext(parameters={"cpu": 4}), req) is False


def test_satisfies_constraints_software() -> None:
    worker = WorkerContext(
        components={
            "app": AdvertisedComponent(software_version="2.0.0"),
        },
    )
    constraints = TaskConstraints(
        components={
            "app": ComponentRequirement(software_version=">=2.0"),
        },
    )
    req = TaskExecutionConstraints(constraints=constraints)
    assert satisfies(worker, req) is True


def test_satisfies_constraints_hardware_only() -> None:
    worker = WorkerContext(
        components={
            "board": AdvertisedComponent(hardware_version="sku-9"),
        },
    )
    constraints = TaskConstraints(
        components={
            "board": ComponentRequirement(hardware_version="sku-9"),
        },
    )
    req = TaskExecutionConstraints(constraints=constraints)
    assert satisfies(worker, req) is True
    assert (
        satisfies(
            WorkerContext(
                components={
                    "board": AdvertisedComponent(hardware_version="sku-1"),
                },
            ),
            req,
        )
        is False
    )


def test_advertised_satisfies_and_matmul_equivalent() -> None:
    advertised = AdvertisedComponent(
        software_version="3.1.0",
        hardware_version="pcb-rev-2",
    )
    required = ComponentRequirement(
        software_version=">=3.0",
        hardware_version="pcb-rev-2",
    )
    assert advertised.satisfies(required) is True
    assert required @ advertised is True


def test_satisfies_constraints_software_and_hardware_same_component() -> None:
    worker = WorkerContext(
        components={
            "instrument-a": AdvertisedComponent(
                software_version="3.1.0",
                hardware_version="pcb-rev-2",
            ),
        },
    )
    constraints = TaskConstraints(
        components={
            "instrument-a": ComponentRequirement(
                software_version=">=3.0",
                hardware_version="pcb-rev-2",
            ),
        },
    )
    assert satisfies(worker, TaskExecutionConstraints(constraints=constraints)) is True


@pytest.mark.parametrize(
    ("specifier", "version", "expected"),
    [
        (">=1.0", "1.0.1", True),
        (">=2.0", "1.9.0", False),
    ],
)
def test_satisfies_constraints_software_version_specifier(
    specifier: str,
    version: str,
    expected: bool,
) -> None:
    worker = WorkerContext(
        components={
            "lib": AdvertisedComponent(software_version=version),
        },
    )
    constraints = TaskConstraints(
        components={"lib": ComponentRequirement(software_version=specifier)},
    )
    req = TaskExecutionConstraints(constraints=constraints)
    assert satisfies(worker, req) is expected


def test_component_parameter_digest() -> None:
    params = {"slot": "A"}
    digest = compute_capability_digest(params)
    worker = WorkerContext(
        components={
            "probe": AdvertisedComponent(parameters=params),
        },
    )
    constraints = TaskConstraints(
        components={"probe": ComponentRequirement(parameter_digest=digest)},
    )
    assert satisfies(worker, TaskExecutionConstraints(constraints=constraints)) is True
