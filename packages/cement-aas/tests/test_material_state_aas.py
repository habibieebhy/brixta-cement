from pathlib import Path

from basyx.aas import model
from brixta_cement_material import (
    ChemicalComponent,
    ChemicalComposition,
    MaterialState,
    MeasurementRecord,
    Mineralogy,
    MineralPhase,
)

from brixta_cement_aas import (
    build_material_sample_aas,
    build_material_state_submodel,
    write_aasx,
    write_json,
)


def _xrd_only_state() -> MaterialState:
    return MaterialState(
        sample_id="clinker-001",
        material_type="clinker",
        observed_at="2026-08-11T12:00:00Z",
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
                method_name="minimal-phase-fraction",
                method_version="1",
                method_sha256="recipe-hash",
                metrics={"wR": 7.5},
                artifacts={"project": "/tmp/run.gpx"},
            ),
        ),
    )


def test_xrd_only_material_state_maps_to_aas() -> None:
    submodel = build_material_state_submodel(_xrd_only_state())

    chemistry_status = submodel.get_referable("ChemistryStatus")
    mineralogy_status = submodel.get_referable("MineralogyStatus")
    alite_name = submodel.get_referable(["Mineralogy", "Phase001", "Name"])
    alite_fraction = submodel.get_referable(["Mineralogy", "Phase001", "MassFraction"])
    engine = submodel.get_referable(
        ["Measurements", "Measurement001", "Engine"]
    )

    assert isinstance(chemistry_status, model.Property)
    assert chemistry_status.value == "unavailable"
    assert isinstance(mineralogy_status, model.Property)
    assert mineralogy_status.value == "available"
    assert isinstance(alite_name, model.Property)
    assert alite_name.value == "Alite"
    assert isinstance(alite_fraction, model.Property)
    assert float(alite_fraction.value) == 0.62
    assert isinstance(engine, model.Property)
    assert engine.value == "GSAS-II"


def test_chemistry_is_mapped_when_available() -> None:
    state = MaterialState(
        sample_id="clinker-chemistry",
        material_type="clinker",
        observed_at="2026-08-11T12:00:00Z",
        chemistry=ChemicalComposition(
            components=(
                ChemicalComponent("CaO", 0.65),
                ChemicalComponent("SiO2", 0.22),
            )
        ),
    )

    submodel = build_material_state_submodel(state)

    chemistry_status = submodel.get_referable("ChemistryStatus")
    cao = submodel.get_referable(
        ["ChemicalComposition", "Component001", "Name"]
    )

    assert isinstance(chemistry_status, model.Property)
    assert chemistry_status.value == "available"
    assert isinstance(cao, model.Property)
    assert cao.value == "CaO"


def test_material_sample_bundle_serializes(tmp_path: Path) -> None:
    bundle = build_material_sample_aas(_xrd_only_state())

    assert isinstance(bundle.aas, model.AssetAdministrationShell)
    assert isinstance(bundle.material_state, model.Submodel)

    json_path = write_json(bundle, tmp_path / "material.json")
    aasx_path = write_aasx(bundle, tmp_path / "material.aasx")

    assert json_path.exists()
    assert aasx_path.exists()
    assert json_path.stat().st_size > 0
    assert aasx_path.stat().st_size > 0
