from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from .model import CementComponent, CementComponentKind, ComponentChemistry


@runtime_checkable
class ClinkerChemistryLike(Protocol):
    def as_dict(self) -> Mapping[str, float]: ...


@runtime_checkable
class ClinkerStateLike(Protocol):
    chemistry: ClinkerChemistryLike | None
    sample_id: str | None
    method: str


@runtime_checkable
class ChemicalComponentLike(Protocol):
    name: str
    mass_fraction: float


@runtime_checkable
class ChemicalCompositionLike(Protocol):
    components: Sequence[ChemicalComponentLike]


@runtime_checkable
class MaterialStateLike(Protocol):
    sample_id: str
    material_type: str
    chemistry: ChemicalCompositionLike | None


def component_from_clinker_state(
    state: ClinkerStateLike,
    *,
    mass_fraction: float,
    name: str = "clinker",
) -> CementComponent:
    chemistry = None
    if state.chemistry is not None:
        chemistry = ComponentChemistry(
            dict(state.chemistry.as_dict()),
            basis="clinker-state-chemistry",
        )

    return CementComponent(
        name=name,
        kind=CementComponentKind.CLINKER,
        mass_fraction=mass_fraction,
        chemistry=chemistry,
        source_id=state.sample_id,
        metadata={"clinker_method": str(state.method)},
    )


def component_from_material_state(
    state: MaterialStateLike,
    *,
    mass_fraction: float,
    kind: CementComponentKind,
    name: str | None = None,
) -> CementComponent:
    chemistry = None
    if state.chemistry is not None:
        chemistry = ComponentChemistry(
            {
                component.name: float(component.mass_fraction)
                for component in state.chemistry.components
            },
            basis="material-state-chemistry",
        )

    return CementComponent(
        name=state.material_type if name is None else name,
        kind=kind,
        mass_fraction=mass_fraction,
        chemistry=chemistry,
        source_id=state.sample_id,
        metadata={"material_type": str(state.material_type)},
    )
