from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol

from .model import MaterialState, MeasurementRecord, Mineralogy, MineralPhase


class XrdEngineInfoLike(Protocol):
    engine: str
    engine_version: str
    adapter_version: str


class XrdPhaseLike(Protocol):
    name: str
    mass_fraction: float
    uncertainty: float


class XrdResultLike(Protocol):
    run_id: str
    sample_id: str
    completed_at: str
    engine: XrdEngineInfoLike
    recipe_name: str
    recipe_version: str
    recipe_sha256: str
    phases: Sequence[XrdPhaseLike]
    residuals: Mapping[str, float]
    inputs: Mapping[str, str]
    input_sha256: Mapping[str, str]
    artifacts: Mapping[str, str]
    warnings: Sequence[str]


def material_state_from_xrd(
    result: XrdResultLike,
    *,
    material_type: str,
) -> MaterialState:
    """Map a normalized BRIXTA XRD result into an engine-neutral MaterialState."""

    mineralogy = Mineralogy(
        phases=tuple(
            MineralPhase(
                name=phase.name,
                mass_fraction=phase.mass_fraction,
                uncertainty=phase.uncertainty,
            )
            for phase in result.phases
        )
    )

    measurement = MeasurementRecord(
        technique="XRD",
        run_id=result.run_id,
        completed_at=result.completed_at,
        engine=result.engine.engine,
        engine_version=result.engine.engine_version,
        adapter_version=result.engine.adapter_version,
        method_name=result.recipe_name,
        method_version=result.recipe_version,
        method_sha256=result.recipe_sha256,
        metrics=result.residuals,
        inputs=result.inputs,
        input_sha256=result.input_sha256,
        artifacts=result.artifacts,
        warnings=tuple(result.warnings),
    )

    return MaterialState(
        sample_id=result.sample_id,
        material_type=material_type,
        observed_at=result.completed_at,
        chemistry=None,
        mineralogy=mineralogy,
        measurements=(measurement,),
    )
