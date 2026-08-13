from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _finite(value: float, field_name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be finite")
    return number


def _non_negative(value: float, field_name: str) -> float:
    number = _finite(value, field_name)
    if number < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return number


@dataclass(frozen=True)
class ThermoStateInput:
    temperature_k: float | None = None
    pressure_pa: float | None = None
    element_amounts_mol: dict[str, float] = field(default_factory=dict)
    preserve_unspecified_elements: bool = False
    min_phase_amount_mol: float = 1e-12
    min_species_amount_mol: float = 1e-12
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.temperature_k is not None:
            value = _finite(self.temperature_k, "temperature_k")
            if value <= 0:
                raise ValueError("temperature_k must be positive")
            object.__setattr__(self, "temperature_k", value)
        if self.pressure_pa is not None:
            value = _finite(self.pressure_pa, "pressure_pa")
            if value <= 0:
                raise ValueError("pressure_pa must be positive")
            object.__setattr__(self, "pressure_pa", value)

        amounts = {}
        for name, amount in self.element_amounts_mol.items():
            key = str(name).strip()
            if not key:
                raise ValueError("element name must not be blank")
            amounts[key] = _non_negative(amount, f"element_amounts_mol[{key}]")
        object.__setattr__(self, "element_amounts_mol", amounts)
        object.__setattr__(
            self,
            "min_phase_amount_mol",
            _non_negative(self.min_phase_amount_mol, "min_phase_amount_mol"),
        )
        object.__setattr__(
            self,
            "min_species_amount_mol",
            _non_negative(self.min_species_amount_mol, "min_species_amount_mol"),
        )


@dataclass(frozen=True)
class ThermoPhase:
    name: str
    amount_mol: float
    mass_kg: float
    volume_m3: float
    density_kg_m3: float
    saturation_index: float


@dataclass(frozen=True)
class ThermoSpecies:
    name: str
    phase_name: str
    amount_mol: float
    charge: float


@dataclass(frozen=True)
class ThermoResult:
    system_path: str
    system_sha256: str
    engine: dict[str, str | bool | None]
    input: ThermoStateInput
    converged: bool
    status_code: int
    iterations: int
    elapsed_time_s: float
    temperature_k: float
    pressure_pa: float
    element_amounts_mol: dict[str, float]
    phases: tuple[ThermoPhase, ...]
    species: tuple[ThermoSpecies, ...]
    ionic_strength_molal: float
    ph: float
    pe: float
    eh_v: float
    system_mass_kg: float
    system_volume_m3: float
    system_gibbs_energy: float
    system_enthalpy: float
    system_entropy: float
    system_heat_capacity_const_p: float
    warnings: tuple[str, ...] = ()

    def phase(self, name: str) -> ThermoPhase | None:
        key = name.casefold()
        for phase in self.phases:
            if phase.name.casefold() == key:
                return phase
        return None

    def species_by_name(self, name: str) -> tuple[ThermoSpecies, ...]:
        key = name.casefold()
        return tuple(item for item in self.species if item.name.casefold() == key)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, destination: str | Path) -> Path:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path
