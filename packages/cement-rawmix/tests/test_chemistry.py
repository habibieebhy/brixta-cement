import pytest

from brixta_cement_rawmix import alumina_modulus, lime_saturation_factor, silica_modulus


def test_moduli_are_computed_from_oxide_fractions() -> None:
    oxides = {"CaO": 0.435, "SiO2": 0.145, "Al2O3": 0.048, "Fe2O3": 0.032}
    expected_lsf = 0.435 / (2.8 * 0.145 + 1.18 * 0.048 + 0.65 * 0.032)
    assert lime_saturation_factor(oxides) == pytest.approx(expected_lsf)
    assert silica_modulus(oxides) == pytest.approx(0.145 / (0.048 + 0.032))
    assert alumina_modulus(oxides) == pytest.approx(0.048 / 0.032)
