import pytest

from brixta_cement_clinker import ClinkerChemistry, estimate_bogue


def test_bogue_typical_clinker_major_phases() -> None:
    chemistry = ClinkerChemistry(
        CaO=0.650,
        SiO2=0.215,
        Al2O3=0.052,
        Fe2O3=0.032,
    )

    result = estimate_bogue(chemistry, normalize=False)

    assert result.method == "bogue-potential"
    assert result.phase_fraction("C3S") == pytest.approx(0.617054)
    assert result.phase_fraction("C2S") == pytest.approx(0.1508994624)
    assert result.phase_fraction("C3A") == pytest.approx(0.083656)
    assert result.phase_fraction("C4AF") == pytest.approx(0.097376)
    assert result.free_lime_mass_fraction is None
    assert result.liquid_phase_mass_fraction is None
    assert result.burnability_index is None


def test_bogue_normalizes_reported_oxide_basis() -> None:
    chemistry = ClinkerChemistry(
        CaO=0.650,
        SiO2=0.215,
        Al2O3=0.052,
        Fe2O3=0.032,
        MgO=0.015,
    )

    result = estimate_bogue(chemistry)

    assert result.chemistry is not None
    assert result.chemistry.total == pytest.approx(1.0)
    assert any("normalized to 1.0" in warning for warning in result.warnings)


def test_bogue_rejects_nonphysical_result() -> None:
    chemistry = ClinkerChemistry(CaO=0.1, SiO2=0.7, Al2O3=0.1, Fe2O3=0.1)

    with pytest.raises(ValueError, match="outside a physical mass-fraction range"):
        estimate_bogue(chemistry, normalize=False)
