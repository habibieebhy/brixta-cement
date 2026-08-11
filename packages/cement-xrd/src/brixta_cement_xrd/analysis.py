from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from uuid import uuid4

from .errors import Gsas2AnalysisError
from .inputs import RefinementRecipe, ValidatedXrdAnalysisInput, XrdAnalysisInput
from .result import EngineInfo, PhaseFraction, XrdResult


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return slug or "sample"


def _input_provenance(job: ValidatedXrdAnalysisInput) -> tuple[dict[str, str], dict[str, str]]:
    inputs = {
        "pattern": str(job.pattern_path),
        "instrument": str(job.instrument_path),
    }
    hashes = {
        "pattern": _sha256_file(job.pattern_path),
        "instrument": _sha256_file(job.instrument_path),
    }
    for phase in job.phases:
        key = f"phase:{phase.name}"
        inputs[key] = str(phase.cif_path)
        hashes[key] = _sha256_file(phase.cif_path)
    return inputs, hashes


def _normalize_mass_fractions(raw: object) -> tuple[tuple[PhaseFraction, ...], tuple[str, ...]]:
    if not isinstance(raw, dict) or not raw:
        raise Gsas2AnalysisError("GSAS-II returned no quantitative phase fractions.")

    phases: list[PhaseFraction] = []
    warnings: list[str] = []
    for name, values in raw.items():
        try:
            mass_fraction = float(values[0])
            uncertainty = float(values[1])
        except (TypeError, ValueError, IndexError) as exc:
            raise Gsas2AnalysisError(
                f"GSAS-II returned an invalid mass-fraction record for phase {name!r}: {values!r}"
            ) from exc
        if not math.isfinite(mass_fraction) or not math.isfinite(uncertainty):
            raise Gsas2AnalysisError(
                f"GSAS-II returned a non-finite result for phase {name!r}."
            )
        if mass_fraction < 0:
            warnings.append(
                f"Phase {name} refined to a negative mass fraction; result needs review."
            )
        if mass_fraction > 1:
            warnings.append(f"Phase {name} refined above 100% mass fraction; result needs review.")
        if uncertainty < 0:
            warnings.append(
                f"Phase {name} has a negative reported uncertainty; result needs review."
            )
        phases.append(
            PhaseFraction(
                name=str(name),
                mass_fraction=mass_fraction,
                uncertainty=uncertainty,
            )
        )

    phases.sort(key=lambda phase: phase.mass_fraction, reverse=True)
    total = sum(phase.mass_fraction for phase in phases)
    if not 0.98 <= total <= 1.02:
        warnings.append(
            f"Reported phase mass fractions sum to {total:.6f}, outside the 0.98-1.02 review band."
        )
    return tuple(phases), tuple(warnings)


def _numeric_residuals(histogram: object) -> dict[str, float]:
    raw = getattr(histogram, "residuals", {})
    if not isinstance(raw, dict):
        return {}
    result: dict[str, float] = {}
    for key, value in raw.items():
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(numeric):
            result[str(key)] = numeric
    return result


def run_quantitative_analysis(
    *,
    scriptable: ModuleType,
    engine_info: EngineInfo,
    request: XrdAnalysisInput,
    recipe: RefinementRecipe,
) -> XrdResult:
    """Execute one GSAS-II Rietveld/QPA workflow and normalize the result."""

    job = request.validate()
    run_id = uuid4().hex
    started = datetime.now(UTC).isoformat()
    run_dir = job.output_dir / f"{_slug(job.sample_id)}-{run_id[:12]}"
    project_path = run_dir / "refinement.gpx"
    result_path = run_dir / "result.json"
    run_dir.mkdir(parents=True, exist_ok=False)

    inputs, input_hashes = _input_provenance(job)
    recipe_sha256 = _sha256_json(recipe.to_dict())

    try:
        project = scriptable.G2Project(newgpx=str(project_path))
        histogram = project.add_powder_histogram(
            str(job.pattern_path),
            str(job.instrument_path),
            fmthint=job.pattern_format_hint,
            databank=job.data_bank,
            instbank=job.instrument_bank,
        )
        if isinstance(histogram, (list, tuple)):
            raise Gsas2AnalysisError(
                "BRIXTA quantitative XRD currently supports exactly one powder histogram per run."
            )

        for phase in job.phases:
            project.add_phase(
                str(phase.cif_path),
                phasename=phase.name,
                histograms=[histogram],
                fmthint=phase.format_hint,
            )

        project.save()
        project.do_refinements(recipe.gsas_steps())
        project.save()
        raw_fractions = histogram.ComputeMassFracs()
    except Gsas2AnalysisError:
        raise
    except Exception as exc:
        raise Gsas2AnalysisError(
            f"GSAS-II quantitative analysis failed for sample {job.sample_id!r}: {exc}"
        ) from exc

    phases, warnings = _normalize_mass_fractions(raw_fractions)
    completed = datetime.now(UTC).isoformat()
    result = XrdResult(
        run_id=run_id,
        sample_id=job.sample_id,
        started_at=started,
        completed_at=completed,
        engine=engine_info,
        recipe_name=recipe.name,
        recipe_version=recipe.version,
        recipe_sha256=recipe_sha256,
        phases=phases,
        residuals=_numeric_residuals(histogram),
        inputs=inputs,
        input_sha256=input_hashes,
        artifacts={
            "gpx": str(project_path),
            "result_json": str(result_path),
        },
        warnings=warnings,
    )
    result.write_json(result_path)
    return result
