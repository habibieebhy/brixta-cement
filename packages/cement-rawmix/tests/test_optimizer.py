import pytest

from brixta_cement_rawmix import (
    ModulusTarget,
    OxideComposition,
    RawMaterial,
    RawMixProblem,
    build_pyomo_model,
    solve_raw_mix,
)


def _problem() -> RawMixProblem:
    return RawMixProblem(
        materials=(
            RawMaterial("Limestone", OxideComposition(0.52, 0.03, 0.01, 0.005), 0.65, 0.90),
            RawMaterial("Clay", OxideComposition(0.08, 0.58, 0.18, 0.07), 0.05, 0.30),
            RawMaterial("IronCorrective", OxideComposition(0.03, 0.12, 0.05, 0.62), 0.0, 0.10),
        ),
        lsf=ModulusTarget(0.96, 0.90, 1.02),
        sm=ModulusTarget(2.4, 1.8, 3.0),
        am=ModulusTarget(1.5, 1.0, 2.5),
    )


def test_builds_pyomo_model() -> None:
    built = build_pyomo_model(_problem())
    assert built.material_names == ("Limestone", "Clay", "IronCorrective")
    assert "CaO" in built.oxide_names


def test_highs_solves_reference_problem() -> None:
    solution = solve_raw_mix(_problem())
    assert sum(solution.material_fractions.values()) == pytest.approx(1.0, abs=1e-8)
    assert 0.90 <= solution.lsf <= 1.02
    assert 1.8 <= solution.sm <= 3.0
    assert 1.0 <= solution.am <= 2.5
