from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MATERIAL_STATE_SCHEMA_VERSION = "1.0"


def _clean_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be blank")
    return cleaned


def _fraction(value: float, field_name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be finite")
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")
    return number


def _uncertainty(value: float | None, field_name: str) -> float | None:
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise ValueError(f"{field_name} must be a finite non-negative number")
    return number


def _unique_names(values: tuple[object, ...], field_name: str) -> None:
    names = [value.name.casefold() for value in values]
    if len(names) != len(set(names)):
        raise ValueError(f"{field_name} contains duplicate names")


def _string_mapping(values: Mapping[str, str], field_name: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in values.items():
        cleaned_key = _clean_text(str(key), f"{field_name} key")
        cleaned_value = _clean_text(str(value), f"{field_name}[{cleaned_key}]")
        result[cleaned_key] = cleaned_value
    return result


def _float_mapping(values: Mapping[str, float], field_name: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for key, value in values.items():
        cleaned_key = _clean_text(str(key), f"{field_name} key")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"{field_name}[{cleaned_key}] must be finite")
        result[cleaned_key] = number
    return result


@dataclass(frozen=True)
class MineralPhase:
    """One observed mineralogical phase."""

    name: str
    mass_fraction: float
    uncertainty: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _clean_text(self.name, "name"))
        object.__setattr__(
            self,
            "mass_fraction",
            _fraction(self.mass_fraction, f"{self.name}.mass_fraction"),
        )
        object.__setattr__(
            self,
            "uncertainty",
            _uncertainty(self.uncertainty, f"{self.name}.uncertainty"),
        )

    @property
    def percent(self) -> float:
        return self.mass_fraction * 100.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mass_fraction": self.mass_fraction,
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class ChemicalComponent:
    """One observed chemical component, typically an oxide fraction."""

    name: str
    mass_fraction: float
    uncertainty: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _clean_text(self.name, "name"))
        object.__setattr__(
            self,
            "mass_fraction",
            _fraction(self.mass_fraction, f"{self.name}.mass_fraction"),
        )
        object.__setattr__(
            self,
            "uncertainty",
            _uncertainty(self.uncertainty, f"{self.name}.uncertainty"),
        )

    @property
    def percent(self) -> float:
        return self.mass_fraction * 100.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mass_fraction": self.mass_fraction,
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class Mineralogy:
    """Observed mineralogical composition."""

    phases: tuple[MineralPhase, ...]

    def __post_init__(self) -> None:
        phases = tuple(self.phases)
        if not phases:
            raise ValueError("phases must not be empty")
        _unique_names(phases, "phases")
        object.__setattr__(self, "phases", phases)

    @property
    def total_mass_fraction(self) -> float:
        return sum(phase.mass_fraction for phase in self.phases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phases": [phase.to_dict() for phase in self.phases],
            "total_mass_fraction": self.total_mass_fraction,
        }


@dataclass(frozen=True)
class ChemicalComposition:
    """Observed chemical composition. Optional on MaterialState."""

    components: tuple[ChemicalComponent, ...]

    def __post_init__(self) -> None:
        components = tuple(self.components)
        if not components:
            raise ValueError("components must not be empty")
        _unique_names(components, "components")
        object.__setattr__(self, "components", components)

    @property
    def total_mass_fraction(self) -> float:
        return sum(component.mass_fraction for component in self.components)

    def to_dict(self) -> dict[str, Any]:
        return {
            "components": [component.to_dict() for component in self.components],
            "total_mass_fraction": self.total_mass_fraction,
        }


@dataclass(frozen=True)
class MeasurementRecord:
    """Engine-neutral provenance for one scientific measurement/result."""

    technique: str
    run_id: str
    completed_at: str
    engine: str | None = None
    engine_version: str | None = None
    adapter_version: str | None = None
    method_name: str | None = None
    method_version: str | None = None
    method_sha256: str | None = None
    metrics: Mapping[str, float] = field(default_factory=dict)
    inputs: Mapping[str, str] = field(default_factory=dict)
    input_sha256: Mapping[str, str] = field(default_factory=dict)
    artifacts: Mapping[str, str] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "technique", _clean_text(self.technique, "technique"))
        object.__setattr__(self, "run_id", _clean_text(self.run_id, "run_id"))
        object.__setattr__(self, "completed_at", _clean_text(self.completed_at, "completed_at"))

        for field_name in (
            "engine",
            "engine_version",
            "adapter_version",
            "method_name",
            "method_version",
            "method_sha256",
        ):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(self, field_name, _clean_text(value, field_name))

        object.__setattr__(self, "metrics", _float_mapping(self.metrics, "metrics"))
        object.__setattr__(self, "inputs", _string_mapping(self.inputs, "inputs"))
        object.__setattr__(
            self,
            "input_sha256",
            _string_mapping(self.input_sha256, "input_sha256"),
        )
        object.__setattr__(self, "artifacts", _string_mapping(self.artifacts, "artifacts"))

        warnings = tuple(_clean_text(warning, "warning") for warning in self.warnings)
        object.__setattr__(self, "warnings", warnings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "technique": self.technique,
            "run_id": self.run_id,
            "completed_at": self.completed_at,
            "engine": self.engine,
            "engine_version": self.engine_version,
            "adapter_version": self.adapter_version,
            "method_name": self.method_name,
            "method_version": self.method_version,
            "method_sha256": self.method_sha256,
            "metrics": dict(self.metrics),
            "inputs": dict(self.inputs),
            "input_sha256": dict(self.input_sha256),
            "artifacts": dict(self.artifacts),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class MaterialState:
    """Partially observed state of one cement-industry material sample."""

    sample_id: str
    material_type: str
    observed_at: str
    chemistry: ChemicalComposition | None = None
    mineralogy: Mineralogy | None = None
    measurements: tuple[MeasurementRecord, ...] = ()
    schema_version: str = field(default=MATERIAL_STATE_SCHEMA_VERSION, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sample_id", _clean_text(self.sample_id, "sample_id"))
        object.__setattr__(
            self,
            "material_type",
            _clean_text(self.material_type, "material_type"),
        )
        object.__setattr__(self, "observed_at", _clean_text(self.observed_at, "observed_at"))
        measurements = tuple(self.measurements)
        object.__setattr__(self, "measurements", measurements)

        if self.chemistry is None and self.mineralogy is None and not measurements:
            raise ValueError(
                "MaterialState must contain chemistry, mineralogy, or at least one measurement"
            )

    @property
    def chemistry_status(self) -> str:
        return "available" if self.chemistry is not None else "unavailable"

    @property
    def mineralogy_status(self) -> str:
        return "available" if self.mineralogy is not None else "unavailable"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "sample_id": self.sample_id,
            "material_type": self.material_type,
            "observed_at": self.observed_at,
            "chemistry_status": self.chemistry_status,
            "mineralogy_status": self.mineralogy_status,
            "chemistry": None if self.chemistry is None else self.chemistry.to_dict(),
            "mineralogy": None if self.mineralogy is None else self.mineralogy.to_dict(),
            "measurements": [measurement.to_dict() for measurement in self.measurements],
        }

    def write_json(self, destination: str | Path) -> Path:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return path
