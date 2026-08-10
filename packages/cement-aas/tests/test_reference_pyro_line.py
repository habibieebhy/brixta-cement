import pytest
from basyx.aas import model

from brixta_cement_aas import build_reference_pyro_line


def test_reference_pyro_line_contains_expected_equipment() -> None:
    bundle = build_reference_pyro_line("plant-001", "pyro-01")
    assert isinstance(bundle.aas, model.AssetAdministrationShell)
    assert isinstance(bundle.topology, model.Submodel)

    for element_id in ("Preheater", "Precalciner", "RotaryKiln", "ClinkerCooler"):
        assert bundle.topology.get_referable(element_id) is not None

    for cyclone in ("Cyclone01", "Cyclone02", "Cyclone03", "Cyclone04"):
        assert bundle.topology.get_referable(["Preheater", cyclone]) is not None


def test_physics_is_explicitly_external() -> None:
    bundle = build_reference_pyro_line("plant-001", "pyro-01")
    status = bundle.topology.get_referable("ModelStatus")
    assert isinstance(status, model.Property)
    assert status.value == "topology_only_external_process_model_required"


@pytest.mark.parametrize("plant_id,line_id", [("", "line"), ("plant", "   ")])
def test_blank_ids_rejected(plant_id: str, line_id: str) -> None:
    with pytest.raises(ValueError):
        build_reference_pyro_line(plant_id, line_id)
