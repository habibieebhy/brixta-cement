from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


def _clean(value: str, field_name: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} must not be blank")
    return value


def _finite(value: float, field_name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite")
    return value


def _fraction(value: float, field_name: str) -> float:
    value = _finite(value, field_name)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")
    return value


@dataclass(frozen=True)
class OxideComposition:
    CaO: float
    SiO2: float
    Al2O3: float
    Fe2O3: float
    MgO: float = 0.0
    SO3: float = 0.0
    Na2O: float = 0.0
    K2O: float = 0.0

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            object.__setattr__(self, name, _fraction(getattr(self, name), name))

    def as_dict(self) -> dict[str, float]:
        return {
            "CaO": self.CaO,
            "SiO2": self.SiO2,
            "Al2O3": self.Al2O3,
            "Fe2O3": self.Fe2O3,
            "MgO": self.MgO,
            "SO3": self.SO3,
            "Na2O": self.Na2O,
            "K2O": self.K2O,
        }


@dataclass(frozen=True)
class RawMaterial:
    name: str
    composition: OxideComposition
    min_fraction: float = 0.0
    max_fraction: float = 1.0
    cost_per_tonne: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _clean(self.name, "name"))
        object.__setattr__(
            self, "min_fraction", _fraction(self.min_fraction, f"{self.name}.min_fraction")
        )
        object.__setattr__(
            self, "max_fraction", _fraction(self.max_fraction, f"{self.name}.max_fraction")
        )
        if self.min_fraction > self.max_fraction:
            raise ValueError(f"{self.name}: min_fraction must be <= max_fraction")
        if self.cost_per_tonne is not None:
            cost = _finite(self.cost_per_tonne, f"{self.name}.cost_per_tonne")
            if cost < 0:
                raise ValueError(f"{self.name}.cost_per_tonne must be non-negative")
            object.__setattr__(self, "cost_per_tonne", cost)


@dataclass(frozen=True)
class ModulusTarget:
    target: float
    minimum: float
    maximum: float
    weight: float = 1.0

    def __post_init__(self) -> None:
        for name in ("target", "minimum", "maximum", "weight"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.minimum <= 0 or self.target <= 0 or self.maximum <= 0:
            raise ValueError("modulus values must be positive")
        if not self.minimum <= self.target <= self.maximum:
            raise ValueError("minimum <= target <= maximum is required")
        if self.weight < 0:
            raise ValueError("weight must be non-negative")


@dataclass(frozen=True)
class OxideTarget:
    oxide: str
    minimum: float | None = None
    maximum: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "oxide", _clean(self.oxide, "oxide"))
        valid = set(OxideComposition(0, 0, 0, 0).as_dict())
        if self.oxide not in valid:
            raise ValueError(f"unsupported oxide: {self.oxide}")
        if self.minimum is None and self.maximum is None:
            raise ValueError("at least one oxide bound is required")
        if self.minimum is not None:
            object.__setattr__(self, "minimum", _fraction(self.minimum, f"{self.oxide}.minimum"))
        if self.maximum is not None:
            object.__setattr__(self, "maximum", _fraction(self.maximum, f"{self.oxide}.maximum"))
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("oxide minimum must be <= maximum")


@dataclass(frozen=True)
class RawMixProblem:
    materials: tuple[RawMaterial, ...]
    lsf: ModulusTarget
    sm: ModulusTarget
    am: ModulusTarget
    oxide_targets: tuple[OxideTarget, ...] = ()
    cost_weight: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        materials = tuple(self.materials)
        if len(materials) < 2:
            raise ValueError("at least two raw materials are required")
        names = [material.name.casefold() for material in materials]
        if len(names) != len(set(names)):
            raise ValueError("raw-material names must be unique")
        if sum(m.min_fraction for m in materials) > 1.0 + 1e-12:
            raise ValueError("sum of material minimum fractions exceeds 1")
        if sum(m.max_fraction for m in materials) < 1.0 - 1e-12:
            raise ValueError("sum of material maximum fractions is below 1")
        object.__setattr__(self, "materials", materials)
        object.__setattr__(self, "oxide_targets", tuple(self.oxide_targets))
        cost_weight = _finite(self.cost_weight, "cost_weight")
        if cost_weight < 0:
            raise ValueError("cost_weight must be non-negative")
        object.__setattr__(self, "cost_weight", cost_weight)


@dataclass(frozen=True)
class RawMixSolution:
    material_fractions: dict[str, float]
    oxide_composition: dict[str, float]
    lsf: float
    sm: float
    am: float
    objective_value: float
    solver: str
    solver_status: str
    termination_condition: str
    model_name: str = "brixta_raw_mix_lp_v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "material_fractions": dict(self.material_fractions),
            "oxide_composition": dict(self.oxide_composition),
            "lsf": self.lsf,
            "sm": self.sm,
            "am": self.am,
            "objective_value": self.objective_value,
            "solver": self.solver,
            "solver_status": self.solver_status,
            "termination_condition": self.termination_condition,
            "model_name": self.model_name,
        }
