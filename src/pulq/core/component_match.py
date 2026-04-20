"""Per-component advertised vs required matching (software, hardware, parameter digest)."""

from __future__ import annotations

import importlib

from pulq.core.capability_digest import compute_capability_digest
from pulq.models.capabilities import AdvertisedComponent, ComponentRequirement

__all__ = ["advertised_satisfies", "match_hw_requirement"]


def match_hw_requirement(required: str, reported: str) -> bool:
    """Return whether ``reported`` equals ``required`` (opaque hardware token, exact match)."""
    return required == reported


def _software_report_satisfies_specifier(specifier: str, reported_version: str) -> bool:
    try:
        spec_mod = importlib.import_module("packaging.specifiers")
        ver_mod = importlib.import_module("packaging.version")
    except ImportError as exc:  # pragma: no cover
        msg = "Software constraint matching requires 'packaging' (install pulq[capabilities])"
        raise ImportError(msg) from exc
    spec = spec_mod.SpecifierSet(specifier)
    ver = ver_mod.Version(reported_version)
    return ver in spec


def advertised_satisfies(advertised: AdvertisedComponent, required: ComponentRequirement) -> bool:
    """Whether ``advertised`` meets ``required`` (checks each set field on ``required``)."""
    if required.parameter_digest is not None:
        params = advertised.parameters if advertised.parameters is not None else {}
        if compute_capability_digest(params) != required.parameter_digest:
            return False

    if required.software_version is not None:
        reported = advertised.software_version
        if reported is None or not _software_report_satisfies_specifier(
            required.software_version,
            reported,
        ):
            return False

    if required.hardware_version is not None:
        reported = advertised.hardware_version
        if reported is None or not match_hw_requirement(
            required.hardware_version,
            reported,
        ):
            return False

    return True
