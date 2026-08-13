import pytest

from brixta_cement_formulation import (
    CementComponent,
    CementComponentKind,
    CementRecipe,
    ComponentChemistry,
    formulate_cement,
)


def test_opc_mass_balance_and_bulk_chemistry() -> None:
    recipe = CementRecipe(
        recipe_id="opc-demo",
        cement_family="OPC",
        components=(
            CementComponent(
                name="clinker",
                kind=CementComponentKind.CLINKER,
                mass_fraction=0.95,
                chemistry=ComponentChemistry(
                    {
                        "CaO": 0.650,
                        "SiO2": 0.215,
                        "Al2O3": 0.052,
                        "Fe2O3": 0.032,
                        "SO3": 0.008,
                    }
                ),
            ),
            CementComponent(
                name="gypsum",
                kind=CementComponentKind.GYPSUM,
                mass_fraction=0.05,
                chemistry=ComponentChemistry({"CaO": 0.326, "SO3": 0.465}),
            ),
        ),
    )

    state = formulate_cement(recipe)

    assert state.clinker_factor == pytest.approx(0.95)
    assert state.sulfate_carrier_factor == pytest.approx(0.05)
    assert state.scm_factor == pytest.approx(0.0)
    assert state.chemistry_coverage_mass_fraction == pytest.approx(1.0)
    assert state.bulk_component_fraction("CaO") == pytest.approx(
        0.95 * 0.650 + 0.05 * 0.326
    )
    assert state.bulk_component_fraction("SO3") == pytest.approx(
        0.95 * 0.008 + 0.05 * 0.465
    )


def test_lc3_style_recipe_tracks_factors_without_imposing_standard_limits() -> None:
    recipe = CementRecipe(
        recipe_id="lc3-style",
        cement_family="LC3-style",
        components=(
            CementComponent("clinker", CementComponentKind.CLINKER, 0.50),
            CementComponent("calcined clay", CementComponentKind.CALCINED_CLAY, 0.30),
            CementComponent("limestone", CementComponentKind.LIMESTONE, 0.15),
            CementComponent("gypsum", CementComponentKind.GYPSUM, 0.05),
        ),
    )

    state = formulate_cement(recipe)

    assert state.clinker_factor == pytest.approx(0.50)
    assert state.scm_factor == pytest.approx(0.30)
    assert state.limestone_factor == pytest.approx(0.15)
    assert state.sulfate_carrier_factor == pytest.approx(0.05)


def test_recipe_rejects_mass_balance_error() -> None:
    with pytest.raises(ValueError, match="must sum to 1.0"):
        CementRecipe(
            recipe_id="bad",
            cement_family="custom",
            components=(
                CementComponent("clinker", CementComponentKind.CLINKER, 0.90),
                CementComponent("gypsum", CementComponentKind.GYPSUM, 0.05),
            ),
        )


def test_recipe_rejects_duplicate_component_names() -> None:
    with pytest.raises(ValueError, match="component names must be unique"):
        CementRecipe(
            recipe_id="bad",
            cement_family="custom",
            components=(
                CementComponent("clinker", CementComponentKind.CLINKER, 0.90),
                CementComponent("Clinker", CementComponentKind.CLINKER, 0.10),
            ),
        )


def test_partial_chemistry_is_reported_not_renormalized() -> None:
    recipe = CementRecipe(
        recipe_id="partial",
        cement_family="custom",
        components=(
            CementComponent(
                "clinker",
                CementComponentKind.CLINKER,
                0.90,
                chemistry=ComponentChemistry({"CaO": 0.65}),
            ),
            CementComponent("gypsum", CementComponentKind.GYPSUM, 0.10),
        ),
    )

    state = formulate_cement(recipe)

    assert state.chemistry_coverage_mass_fraction == pytest.approx(0.90)
    assert state.bulk_component_fraction("CaO") == pytest.approx(0.90 * 0.65)
    assert any("Bulk chemistry is partial" in warning for warning in state.warnings)
