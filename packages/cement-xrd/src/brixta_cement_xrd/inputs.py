from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import Gsas2InputError


@dataclass(frozen=True)
class PhaseModel:
    """A candidate crystallographic phase model supplied to GSAS-II."""

    name: str
    cif_path: str | Path
    format_hint: str = "CIF"

    def resolved_path(self) -> Path:
        """Return the validated phase-model path."""

        if not self.name.strip():
            raise Gsas2InputError("Phase names cannot be blank.")
        path = Path(self.cif_path).expanduser().resolve()
        if not path.is_file():
            raise Gsas2InputError(f"Phase model does not exist: {path}")
        return path


@dataclass(frozen=True)
class XrdAnalysisInput:
    """Files and metadata required for one quantitative powder-XRD run."""

    sample_id: str
    pattern_path: str | Path
    instrument_path: str | Path
    phases: tuple[PhaseModel, ...]
    output_dir: str | Path
    pattern_format_hint: str | None = None
    data_bank: int | None = None
    instrument_bank: int | None = None

    def validate(self) -> ValidatedXrdAnalysisInput:
        """Resolve files and reject structurally invalid analysis requests."""

        sample_id = self.sample_id.strip()
        if not sample_id:
            raise Gsas2InputError("sample_id cannot be blank.")
        if not self.phases:
            raise Gsas2InputError("At least one candidate phase model is required.")
        if self.data_bank is not None and self.data_bank < 1:
            raise Gsas2InputError("data_bank must be >= 1 when supplied.")
        if self.instrument_bank is not None and self.instrument_bank < 1:
            raise Gsas2InputError("instrument_bank must be >= 1 when supplied.")

        phase_names = [phase.name.strip() for phase in self.phases]
        if len(set(phase_names)) != len(phase_names):
            raise Gsas2InputError("Candidate phase names must be unique.")

        pattern = Path(self.pattern_path).expanduser().resolve()
        instrument = Path(self.instrument_path).expanduser().resolve()
        if not pattern.is_file():
            raise Gsas2InputError(f"XRD pattern does not exist: {pattern}")
        if not instrument.is_file():
            raise Gsas2InputError(f"Instrument parameter file does not exist: {instrument}")

        output_dir = Path(self.output_dir).expanduser().resolve()
        phases = tuple(
            ValidatedPhaseModel(
                name=phase.name.strip(),
                cif_path=phase.resolved_path(),
                format_hint=phase.format_hint,
            )
            for phase in self.phases
        )

        return ValidatedXrdAnalysisInput(
            sample_id=sample_id,
            pattern_path=pattern,
            instrument_path=instrument,
            phases=phases,
            output_dir=output_dir,
            pattern_format_hint=self.pattern_format_hint,
            data_bank=self.data_bank,
            instrument_bank=self.instrument_bank,
        )


@dataclass(frozen=True)
class ValidatedPhaseModel:
    name: str
    cif_path: Path
    format_hint: str


@dataclass(frozen=True)
class ValidatedXrdAnalysisInput:
    sample_id: str
    pattern_path: Path
    instrument_path: Path
    phases: tuple[ValidatedPhaseModel, ...]
    output_dir: Path
    pattern_format_hint: str | None
    data_bank: int | None
    instrument_bank: int | None


@dataclass(frozen=True)
class RefinementRecipe:
    """A named, versioned sequence of GSAS-II refinement dictionaries."""

    name: str
    version: str
    steps: tuple[dict[str, Any], ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise Gsas2InputError("Refinement recipe name cannot be blank.")
        if not self.version.strip():
            raise Gsas2InputError("Refinement recipe version cannot be blank.")
        if not self.steps:
            raise Gsas2InputError("A quantitative refinement recipe needs at least one step.")

        for index, step in enumerate(self.steps, start=1):
            if not isinstance(step, dict):
                raise Gsas2InputError(f"Refinement step {index} must be a dictionary.")
            forbidden = {"call", "callargs", "output"}.intersection(step)
            if forbidden:
                names = ", ".join(sorted(forbidden))
                raise Gsas2InputError(
                    f"Refinement step {index} uses BRIXTA-forbidden GSAS-II key(s): {names}."
                )

        try:
            json.dumps(self.to_dict(), sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise Gsas2InputError("Refinement recipes must be JSON-serializable.") from exc

        if not self.refines_phase_fractions():
            raise Gsas2InputError(
                "Quantitative phase analysis requires at least one refinement step that sets "
                "PhaseFraction or Scale to True."
            )

    @classmethod
    def from_json(cls, path: str | Path) -> RefinementRecipe:
        """Load a BRIXTA refinement recipe from JSON."""

        recipe_path = Path(path).expanduser().resolve()
        if not recipe_path.is_file():
            raise Gsas2InputError(f"Refinement recipe does not exist: {recipe_path}")
        try:
            payload = json.loads(recipe_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise Gsas2InputError(f"Could not read refinement recipe: {recipe_path}") from exc

        try:
            name = payload["name"]
            recipe_version = payload["version"]
            steps = payload["steps"]
        except (KeyError, TypeError) as exc:
            raise Gsas2InputError(
                "Refinement recipe JSON must contain name, version and steps."
            ) from exc

        if not isinstance(steps, list):
            raise Gsas2InputError("Refinement recipe steps must be a JSON array.")
        return cls(name=str(name), version=str(recipe_version), steps=tuple(steps))

    @classmethod
    def minimal_phase_fraction(cls) -> RefinementRecipe:
        """Return a smoke-test recipe that refines only phase fractions.

        This proves the QPA execution path but is not a validated cement method.
        """

        return cls(
            name="minimal-phase-fraction",
            version="1",
            steps=({"set": {"PhaseFraction": True}},),
        )

    def refines_phase_fractions(self) -> bool:
        """Return whether the final executed refinement includes phase fractions.

        ``ComputeMassFracs()`` derives uncertainties from the covariance matrix of
        the last refinement, so the final executed step must leave the HAP scale
        (``PhaseFraction``/``Scale``) enabled.
        """

        enabled = False
        last_refinement_enabled = False
        for step in self.steps:
            settings = step.get("set", {})
            if settings.get("PhaseFraction") is True or settings.get("Scale") is True:
                enabled = True
            if "PhaseFraction" in step.get("clear", {}) or "Scale" in step.get("clear", {}):
                enabled = False

            once = step.get("once", {})
            once_enabled = (
                once.get("PhaseFraction") is True or once.get("Scale") is True
            )
            if "skip" not in step:
                last_refinement_enabled = enabled or once_enabled

        return last_refinement_enabled

    def gsas_steps(self) -> list[dict[str, Any]]:
        """Return an isolated copy suitable for GSAS-II mutation."""

        return deepcopy(list(self.steps))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "steps": deepcopy(list(self.steps)),
        }
