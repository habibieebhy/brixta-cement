from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from .bogue import estimate_bogue
from .model import ClinkerChemistry, ClinkerPhase, ClinkerState


@runtime_checkable
class RawMixSolutionLike(Protocol):
    oxide_composition: Mapping[str, float]
    lsf: float
    sm: float
    am: float
    model_name: str


@runtime_checkable
class XrdPhaseLike(Protocol):
    name: str
    mass_fraction: float
    uncertainty: float


@runtime_checkable
class XrdResultLike(Protocol):
    sample_id: str
    recipe_name: str
    recipe_version: str
    phases: Sequence[XrdPhaseLike]
    warnings: Sequence[str]


def chemistry_from_raw_mix(solution: RawMixSolutionLike) -> ClinkerChemistry:
    """Bridge a RawMixSolution-like object to a normalized represented-oxide basis.

    This is not a calcination or volatilization model. The currently represented
    raw-mix oxides are normalized so downstream clinker chemistry has a stable basis.
    """

    values = dict(solution.oxide_composition)
    required = ("CaO", "SiO2", "Al2O3", "Fe2O3")
    missing = [name for name in required if name not in values]
    if missing:
        raise ValueError(f"raw-mix solution is missing required oxides: {', '.join(missing)}")

    chemistry = ClinkerChemistry(
        CaO=values["CaO"],
        SiO2=values["SiO2"],
        Al2O3=values["Al2O3"],
        Fe2O3=values["Fe2O3"],
        MgO=values.get("MgO", 0.0),
        SO3=values.get("SO3", 0.0),
        Na2O=values.get("Na2O", 0.0),
        K2O=values.get("K2O", 0.0),
        basis="rawmix-represented-oxide",
    )
    return chemistry.normalized(basis="normalized-rawmix-represented-oxide")


def estimate_from_raw_mix(solution: RawMixSolutionLike) -> ClinkerState:
    chemistry = chemistry_from_raw_mix(solution)
    base = estimate_bogue(chemistry, normalize=False)
    warnings = (
        *base.warnings,
        "Raw-mix bridge normalizes represented oxides only; it does not model calcination "
        "mass loss, volatilization, dust cycles or kiln reaction kinetics.",
    )
    provenance = dict(base.provenance)
    provenance["rawmix_model"] = str(solution.model_name)

    return ClinkerState(
        method=base.method,
        chemistry=base.chemistry,
        phases=base.phases,
        lsf=float(solution.lsf),
        sm=float(solution.sm),
        am=float(solution.am),
        warnings=warnings,
        provenance=provenance,
    )


_DEFAULT_ALIASES = {
    "c3s": "C3S",
    "alite": "C3S",
    "c2s": "C2S",
    "belite": "C2S",
    "c3a": "C3A",
    "aluminate": "C3A",
    "c4af": "C4AF",
    "ferrite": "C4AF",
    "free lime": "Free lime",
    "free_lime": "Free lime",
    "lime": "Free lime",
    "periclase": "Periclase",
}


def _normalized_alias(value: str) -> str:
    return " ".join(value.replace("-", " ").replace("_", " ").casefold().split())


def from_xrd_result(
    result: XrdResultLike,
    *,
    aliases: Mapping[str, str] | None = None,
) -> ClinkerState:
    alias_map = {_normalized_alias(key): value for key, value in _DEFAULT_ALIASES.items()}
    if aliases:
        alias_map.update({_normalized_alias(key): value for key, value in aliases.items()})

    phases: list[ClinkerPhase] = []
    free_lime: float | None = None
    for item in result.phases:
        canonical = alias_map.get(_normalized_alias(item.name), item.name.strip())
        phase = ClinkerPhase(
            name=canonical,
            mass_fraction=float(item.mass_fraction),
            uncertainty=float(item.uncertainty),
            source="xrd-rietveld",
        )
        phases.append(phase)
        if canonical.casefold() == "free lime":
            free_lime = phase.mass_fraction

    return ClinkerState(
        method="xrd-rietveld",
        sample_id=result.sample_id,
        phases=tuple(phases),
        free_lime_mass_fraction=free_lime,
        warnings=tuple(result.warnings),
        provenance={
            "recipe_name": result.recipe_name,
            "recipe_version": result.recipe_version,
        },
    )
