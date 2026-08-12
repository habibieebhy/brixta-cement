from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


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


def _clean(value: str, field_name: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} must not be blank")
    return value


@dataclass(frozen=True)
class ClinkerChemistry:
    """Reported oxide fractions for clinker or a normalized clinker oxide basis."""

    CaO: float
    SiO2: float
    Al2O3: float
    Fe2O3: float
    MgO: float = 0.0
    SO3: float = 0.0
    Na2O: float = 0.0
    K2O: float = 0.0
    basis: str = "reported-oxide"

    def __post_init__(self) -> None:
        for name in ("CaO", "SiO2", "Al2O3", "Fe2O3", "MgO", "SO3", "Na2O", "K2O"):
            object.__setattr__(self, name, _fraction(getattr(self, name), name))
        object.__setattr__(self, "basis", _clean(self.basis, "basis"))
        if self.total <= 0:
            raise ValueError("oxide total must be positive")

    @property
    def total(self) -> float:
        return sum(self.as_dict().values())

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

    def normalized(self, *, basis: str = "normalized-reported-oxide") -> ClinkerChemistry:
        total = self.total
        values = {name: value / total for name, value in self.as_dict().items()}
        return ClinkerChemistry(**values, basis=basis)


@dataclass(frozen=True)
class ClinkerPhase:
    name: str
    mass_fraction: float
    uncertainty: float | None = None
    source: str = "unknown"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _clean(self.name, "name"))
        object.__setattr__(self, "mass_fraction", _fraction(self.mass_fraction, self.name))
        object.__setattr__(self, "source", _clean(self.source, "source"))
        if self.uncertainty is not None:
            uncertainty = _finite(self.uncertainty, f"{self.name}.uncertainty")
            if uncertainty < 0:
                raise ValueError(f"{self.name}.uncertainty must be non-negative")
            object.__setattr__(self, "uncertainty", uncertainty)


@dataclass(frozen=True)
class ClinkerState:
    method: str
    phases: tuple[ClinkerPhase, ...]
    chemistry: ClinkerChemistry | None = None
    sample_id: str | None = None
    lsf: float | None = None
    sm: float | None = None
    am: float | None = None
    free_lime_mass_fraction: float | None = None
    liquid_phase_mass_fraction: float | None = None
    burnability_index: float | None = None
    warnings: tuple[str, ...] = ()
    provenance: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "method", _clean(self.method, "method"))
        object.__setattr__(self, "phases", tuple(self.phases))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        if self.sample_id is not None:
            object.__setattr__(self, "sample_id", _clean(self.sample_id, "sample_id"))
        for name in ("lsf", "sm", "am", "burnability_index"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _finite(value, name))
        for name in ("free_lime_mass_fraction", "liquid_phase_mass_fraction"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _fraction(value, name))

    def phase_fraction(self, name: str) -> float | None:
        key = name.casefold()
        for phase in self.phases:
            if phase.name.casefold() == key:
                return phase.mass_fraction
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "sample_id": self.sample_id,
            "chemistry": self.chemistry.as_dict() if self.chemistry is not None else None,
            "chemistry_basis": self.chemistry.basis if self.chemistry is not None else None,
            "phases": [
                {
                    "name": phase.name,
                    "mass_fraction": phase.mass_fraction,
                    "uncertainty": phase.uncertainty,
                    "source": phase.source,
                }
                for phase in self.phases
            ],
            "lsf": self.lsf,
            "sm": self.sm,
            "am": self.am,
            "free_lime_mass_fraction": self.free_lime_mass_fraction,
            "liquid_phase_mass_fraction": self.liquid_phase_mass_fraction,
            "burnability_index": self.burnability_index,
            "warnings": list(self.warnings),
            "provenance": dict(self.provenance),
        }
