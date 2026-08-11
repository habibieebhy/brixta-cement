from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EngineInfo:
    """Normalized metadata for a usable GSAS-II runtime."""

    engine: str
    engine_version: str
    adapter_version: str
    source_path: str
    binary_path: str
    python_version: str
    numpy_version: str

    def to_dict(self) -> dict[str, str]:
        """Return JSON-friendly engine metadata."""

        return asdict(self)


@dataclass(frozen=True)
class PhaseFraction:
    """One GSAS-II quantitative phase-analysis result."""

    name: str
    mass_fraction: float
    uncertainty: float

    @property
    def percent(self) -> float:
        return self.mass_fraction * 100.0


@dataclass(frozen=True)
class XrdResult:
    """Normalized BRIXTA quantitative XRD result with provenance."""

    run_id: str
    sample_id: str
    started_at: str
    completed_at: str
    engine: EngineInfo
    recipe_name: str
    recipe_version: str
    recipe_sha256: str
    phases: tuple[PhaseFraction, ...]
    residuals: dict[str, float]
    inputs: dict[str, str]
    input_sha256: dict[str, str]
    artifacts: dict[str, str]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly result payload."""

        return asdict(self)

    def write_json(self, destination: str | Path) -> Path:
        """Write the normalized result to JSON."""

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path
