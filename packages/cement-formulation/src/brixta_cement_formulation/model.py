from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

_RECIPE_TOLERANCE = 1e-8


def _clean(value: str, field_name: str) -> str:
    cleaned = str(value).strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be blank")
    return cleaned


def _finite(value: float, field_name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be finite")
    return number


def _fraction(value: float, field_name: str) -> float:
    number = _finite(value, field_name)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")
    return number


def _string_mapping(values: dict[str, str], field_name: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in values.items():
        clean_key = _clean(key, f"{field_name} key")
        result[clean_key] = _clean(value, f"{field_name}[{clean_key}]")
    return result


class CementComponentKind(StrEnum):
    CLINKER = "clinker"
    GYPSUM = "gypsum"
    ANHYDRITE = "anhydrite"
    HEMIHYDRATE = "hemihydrate"
    LIMESTONE = "limestone"
    FLY_ASH = "fly-ash"
    GGBS = "ggbs"
    CALCINED_CLAY = "calcined-clay"
    NATURAL_POZZOLAN = "natural-pozzolan"
    SILICA_FUME = "silica-fume"
    OTHER_SCM = "other-scm"
    ADDITIVE = "additive"
    OTHER = "other"

    @property
    def is_clinker(self) -> bool:
        return self is CementComponentKind.CLINKER

    @property
    def is_sulfate_carrier(self) -> bool:
        return self in {
            CementComponentKind.GYPSUM,
            CementComponentKind.ANHYDRITE,
            CementComponentKind.HEMIHYDRATE,
        }

    @property
    def is_scm(self) -> bool:
        return self in {
            CementComponentKind.FLY_ASH,
            CementComponentKind.GGBS,
            CementComponentKind.CALCINED_CLAY,
            CementComponentKind.NATURAL_POZZOLAN,
            CementComponentKind.SILICA_FUME,
            CementComponentKind.OTHER_SCM,
        }

    @property
    def is_limestone(self) -> bool:
        return self is CementComponentKind.LIMESTONE


@dataclass(frozen=True)
class ComponentChemistry:
    "Chemical component fractions, normally oxides, on the source material basis."

    components: dict[str, float]
    basis: str = "reported-mass-fraction"

    def __post_init__(self) -> None:
        if not self.components:
            raise ValueError("components must not be empty")

        cleaned: dict[str, float] = {}
        seen: set[str] = set()
        for name, value in self.components.items():
            key = _clean(name, "component name")
            folded = key.casefold()
            if folded in seen:
                raise ValueError(f"duplicate chemical component: {key}")
            seen.add(folded)
            cleaned[key] = _fraction(value, key)

        object.__setattr__(self, "components", cleaned)
        object.__setattr__(self, "basis", _clean(self.basis, "basis"))

    @property
    def total_fraction(self) -> float:
        return sum(self.components.values())

    def get(self, name: str, default: float = 0.0) -> float:
        key = name.casefold()
        for component, value in self.components.items():
            if component.casefold() == key:
                return value
        return float(default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "basis": self.basis,
            "components": dict(self.components),
            "total_fraction": self.total_fraction,
        }


@dataclass(frozen=True)
class CementComponent:
    name: str
    kind: CementComponentKind
    mass_fraction: float
    chemistry: ComponentChemistry | None = None
    source_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _clean(self.name, "name"))
        object.__setattr__(self, "kind", CementComponentKind(self.kind))
        object.__setattr__(
            self,
            "mass_fraction",
            _fraction(self.mass_fraction, f"{self.name}.mass_fraction"),
        )
        if self.source_id is not None:
            object.__setattr__(self, "source_id", _clean(self.source_id, "source_id"))
        object.__setattr__(self, "metadata", _string_mapping(self.metadata, "metadata"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "mass_fraction": self.mass_fraction,
            "chemistry": None if self.chemistry is None else self.chemistry.to_dict(),
            "source_id": self.source_id,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class CementRecipe:
    recipe_id: str
    cement_family: str
    components: tuple[CementComponent, ...]
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "recipe_id", _clean(self.recipe_id, "recipe_id"))
        object.__setattr__(
            self,
            "cement_family",
            _clean(self.cement_family, "cement_family"),
        )

        components = tuple(self.components)
        if not components:
            raise ValueError("components must not be empty")

        names = [component.name.casefold() for component in components]
        if len(names) != len(set(names)):
            raise ValueError("component names must be unique")

        total = sum(component.mass_fraction for component in components)
        if abs(total - 1.0) > _RECIPE_TOLERANCE:
            raise ValueError(
                "cement component mass fractions must sum to 1.0; "
                f"got {total:.12f}"
            )

        object.__setattr__(self, "components", components)
        object.__setattr__(self, "metadata", _string_mapping(self.metadata, "metadata"))

    @property
    def total_mass_fraction(self) -> float:
        return sum(component.mass_fraction for component in self.components)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "cement_family": self.cement_family,
            "components": [component.to_dict() for component in self.components],
            "total_mass_fraction": self.total_mass_fraction,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class CementState:
    recipe_id: str
    cement_family: str
    components: tuple[CementComponent, ...]
    clinker_factor: float
    scm_factor: float
    sulfate_carrier_factor: float
    limestone_factor: float
    chemistry_coverage_mass_fraction: float
    bulk_chemistry: ComponentChemistry | None = None
    warnings: tuple[str, ...] = ()
    provenance: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "recipe_id", _clean(self.recipe_id, "recipe_id"))
        object.__setattr__(
            self,
            "cement_family",
            _clean(self.cement_family, "cement_family"),
        )
        object.__setattr__(self, "components", tuple(self.components))

        for name in (
            "clinker_factor",
            "scm_factor",
            "sulfate_carrier_factor",
            "limestone_factor",
            "chemistry_coverage_mass_fraction",
        ):
            object.__setattr__(self, name, _fraction(getattr(self, name), name))

        warnings = tuple(_clean(warning, "warning") for warning in self.warnings)
        object.__setattr__(self, "warnings", warnings)
        object.__setattr__(
            self,
            "provenance",
            _string_mapping(self.provenance, "provenance"),
        )

    def bulk_component_fraction(self, name: str) -> float | None:
        if self.bulk_chemistry is None:
            return None
        return self.bulk_chemistry.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "cement_family": self.cement_family,
            "components": [component.to_dict() for component in self.components],
            "clinker_factor": self.clinker_factor,
            "scm_factor": self.scm_factor,
            "sulfate_carrier_factor": self.sulfate_carrier_factor,
            "limestone_factor": self.limestone_factor,
            "chemistry_coverage_mass_fraction": self.chemistry_coverage_mass_fraction,
            "bulk_chemistry": (
                None if self.bulk_chemistry is None else self.bulk_chemistry.to_dict()
            ),
            "warnings": list(self.warnings),
            "provenance": dict(self.provenance),
        }
