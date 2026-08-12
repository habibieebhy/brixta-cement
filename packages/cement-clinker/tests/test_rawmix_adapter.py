from dataclasses import dataclass

import pytest

from brixta_cement_clinker import chemistry_from_raw_mix, estimate_from_raw_mix


@dataclass
class FakeRawMixSolution:
    oxide_composition: dict[str, float]
    lsf: float
    sm: float
    am: float
    model_name: str


def test_rawmix_bridge_normalizes_represented_oxides() -> None:
    solution = FakeRawMixSolution(
        oxide_composition={
            "CaO": 0.48,
            "SiO2": 0.16,
            "Al2O3": 0.04,
            "Fe2O3": 0.025,
            "MgO": 0.01,
        },
        lsf=0.96,
        sm=2.46,
        am=1.6,
        model_name="brixta_raw_mix_lp_v1",
    )

    chemistry = chemistry_from_raw_mix(solution)

    assert chemistry.total == pytest.approx(1.0)
    assert chemistry.basis == "normalized-rawmix-represented-oxide"


def test_rawmix_solution_becomes_potential_clinker_state() -> None:
    solution = FakeRawMixSolution(
        oxide_composition={
            "CaO": 0.650,
            "SiO2": 0.215,
            "Al2O3": 0.052,
            "Fe2O3": 0.032,
        },
        lsf=0.95,
        sm=2.56,
        am=1.625,
        model_name="brixta_raw_mix_lp_v1",
    )

    state = estimate_from_raw_mix(solution)

    assert state.method == "bogue-potential"
    assert state.lsf == pytest.approx(0.95)
    assert state.provenance["rawmix_model"] == "brixta_raw_mix_lp_v1"
    assert any("does not model calcination" in warning for warning in state.warnings)
