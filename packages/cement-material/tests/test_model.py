import json
from pathlib import Path

import pytest

from brixta_cement_material import (
    ChemicalComponent,
    ChemicalComposition,
    MaterialState,
    MeasurementRecord,
    Mineralogy,
    MineralPhase,
)


def test_material_state_supports_xrd_without_chemistry(tmp_path: Path) -> None:
    state = MaterialState(
        sample_id="clinker-001",
        material_type="clinker",
        observed_at="2026-08-11T12:00:00Z",
        chemistry=None,
        mineralogy=Mineralogy(
            phases=(
                MineralPhase("Alite", 0.62, 0.01),
                MineralPhase("Belite", 0.38, 0.02),
            )
        ),
        measurements=(
            MeasurementRecord(
                technique="XRD",
                run_id="run-001",
                completed_at="2026-08-11T12:00:00Z",
                engine="GSAS-II",
                engine_version="v5.7.9",
                adapter_version="0.2.0",
            ),
        ),
    )

    assert state.chemistry_status == "unavailable"
    assert state.mineralogy_status == "available"
    assert state.mineralogy is not None
    assert state.mineralogy.total_mass_fraction == pytest.approx(1.0)

    destination = state.write_json(tmp_path / "material-state.json")
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["sample_id"] == "clinker-001"
    assert payload["chemistry"] is None
    assert payload["mineralogy"]["phases"][0]["name"] == "Alite"


def test_material_state_can_add_chemistry_later() -> None:
    state = MaterialState(
        sample_id="clinker-002",
        material_type="clinker",
        observed_at="2026-08-11T12:00:00Z",
        chemistry=ChemicalComposition(
            components=(
                ChemicalComponent("CaO", 0.65),
                ChemicalComponent("SiO2", 0.22),
            )
        ),
    )

    assert state.chemistry_status == "available"
    assert state.mineralogy_status == "unavailable"


@pytest.mark.parametrize("fraction", [-0.01, 1.01])
def test_fraction_bounds_are_enforced(fraction: float) -> None:
    with pytest.raises(ValueError):
        MineralPhase("Alite", fraction)


def test_duplicate_phase_names_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        Mineralogy(
            phases=(
                MineralPhase("Alite", 0.6),
                MineralPhase("alite", 0.4),
            )
        )


def test_empty_material_state_is_rejected() -> None:
    with pytest.raises(ValueError, match="must contain"):
        MaterialState(
            sample_id="empty",
            material_type="clinker",
            observed_at="2026-08-11T12:00:00Z",
        )
