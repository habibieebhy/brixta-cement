from dataclasses import dataclass

import pytest

from brixta_cement_clinker import (
    ClinkerChemistry,
    compare_major_phases,
    estimate_bogue,
    from_xrd_result,
)


@dataclass
class FakePhase:
    name: str
    mass_fraction: float
    uncertainty: float


@dataclass
class FakeXrd:
    sample_id: str
    recipe_name: str
    recipe_version: str
    phases: tuple[FakePhase, ...]
    warnings: tuple[str, ...] = ()


def test_xrd_adapter_canonicalizes_major_clinker_phases_and_free_lime() -> None:
    xrd = FakeXrd(
        sample_id="clinker-001",
        recipe_name="clinker-qpa",
        recipe_version="1",
        phases=(
            FakePhase("Alite", 0.60, 0.01),
            FakePhase("Belite", 0.17, 0.01),
            FakePhase("C3A", 0.08, 0.005),
            FakePhase("Ferrite", 0.10, 0.006),
            FakePhase("Free Lime", 0.015, 0.002),
        ),
    )

    state = from_xrd_result(xrd)

    assert state.method == "xrd-rietveld"
    assert state.phase_fraction("C3S") == pytest.approx(0.60)
    assert state.phase_fraction("C2S") == pytest.approx(0.17)
    assert state.phase_fraction("C4AF") == pytest.approx(0.10)
    assert state.free_lime_mass_fraction == pytest.approx(0.015)


def test_compare_potential_to_measured() -> None:
    potential = estimate_bogue(
        ClinkerChemistry(CaO=0.650, SiO2=0.215, Al2O3=0.052, Fe2O3=0.032),
        normalize=False,
    )
    measured = from_xrd_result(
        FakeXrd(
            sample_id="clinker-001",
            recipe_name="clinker-qpa",
            recipe_version="1",
            phases=(
                FakePhase("C3S", 0.60, 0.01),
                FakePhase("C2S", 0.17, 0.01),
                FakePhase("C3A", 0.08, 0.005),
                FakePhase("C4AF", 0.10, 0.006),
            ),
        )
    )

    comparison = compare_major_phases(potential, measured)
    c3s = next(row for row in comparison.phases if row.name == "C3S")

    assert c3s.delta_measured_minus_potential == pytest.approx(
        0.60 - potential.phase_fraction("C3S")
    )
