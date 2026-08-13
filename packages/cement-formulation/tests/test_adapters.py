from dataclasses import dataclass

import pytest

from brixta_cement_formulation import (
    CementComponentKind,
    CementRecipe,
    component_from_clinker_state,
    component_from_material_state,
    formulate_cement,
)


@dataclass
class FakeClinkerChemistry:
    values: dict[str, float]

    def as_dict(self) -> dict[str, float]:
        return dict(self.values)


@dataclass
class FakeClinkerState:
    chemistry: FakeClinkerChemistry | None
    sample_id: str | None
    method: str


@dataclass
class FakeChemicalComponent:
    name: str
    mass_fraction: float


@dataclass
class FakeChemicalComposition:
    components: tuple[FakeChemicalComponent, ...]


@dataclass
class FakeMaterialState:
    sample_id: str
    material_type: str
    chemistry: FakeChemicalComposition | None


def test_clinker_state_adapter_preserves_source_and_chemistry() -> None:
    state = FakeClinkerState(
        chemistry=FakeClinkerChemistry({"CaO": 0.65, "SiO2": 0.215}),
        sample_id="clinker-001",
        method="xrd-rietveld",
    )

    component = component_from_clinker_state(state, mass_fraction=0.70)

    assert component.kind is CementComponentKind.CLINKER
    assert component.source_id == "clinker-001"
    assert component.chemistry is not None
    assert component.chemistry.get("CaO") == pytest.approx(0.65)
    assert component.metadata["clinker_method"] == "xrd-rietveld"


def test_xrd_only_clinker_state_remains_valid_with_partial_chemistry_coverage() -> None:
    clinker = component_from_clinker_state(
        FakeClinkerState(
            chemistry=None,
            sample_id="clinker-xrd-only",
            method="xrd-rietveld",
        ),
        mass_fraction=0.95,
    )
    gypsum = component_from_material_state(
        FakeMaterialState(
            sample_id="gypsum-01",
            material_type="gypsum",
            chemistry=FakeChemicalComposition(
                (
                    FakeChemicalComponent("CaO", 0.326),
                    FakeChemicalComponent("SO3", 0.465),
                )
            ),
        ),
        mass_fraction=0.05,
        kind=CementComponentKind.GYPSUM,
    )

    state = formulate_cement(
        CementRecipe(
            recipe_id="xrd-only-clinker",
            cement_family="custom",
            components=(clinker, gypsum),
        )
    )

    assert state.clinker_factor == pytest.approx(0.95)
    assert state.chemistry_coverage_mass_fraction == pytest.approx(0.05)
    assert state.bulk_component_fraction("SO3") == pytest.approx(0.05 * 0.465)


def test_material_state_adapter_uses_explicit_component_kind() -> None:
    material = FakeMaterialState(
        sample_id="flyash-01",
        material_type="fly ash",
        chemistry=FakeChemicalComposition(
            (
                FakeChemicalComponent("SiO2", 0.55),
                FakeChemicalComponent("Al2O3", 0.25),
            )
        ),
    )

    component = component_from_material_state(
        material,
        mass_fraction=0.25,
        kind=CementComponentKind.FLY_ASH,
    )

    assert component.name == "fly ash"
    assert component.kind is CementComponentKind.FLY_ASH
    assert component.source_id == "flyash-01"
    assert component.chemistry is not None
    assert component.chemistry.get("SiO2") == pytest.approx(0.55)
