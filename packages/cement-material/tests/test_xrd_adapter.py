from brixta_cement_material import material_state_from_xrd


class FakeEngine:
    engine = "GSAS-II"
    engine_version = "v5.7.9"
    adapter_version = "0.2.0"


class FakePhase:
    def __init__(self, name: str, mass_fraction: float, uncertainty: float) -> None:
        self.name = name
        self.mass_fraction = mass_fraction
        self.uncertainty = uncertainty


class FakeXrdResult:
    run_id = "run-001"
    sample_id = "clinker-001"
    completed_at = "2026-08-11T12:00:00Z"
    engine = FakeEngine()
    recipe_name = "minimal-phase-fraction"
    recipe_version = "1"
    recipe_sha256 = "recipe-hash"
    phases = (
        FakePhase("Alite", 0.62, 0.01),
        FakePhase("Belite", 0.38, 0.02),
    )
    residuals = {"wR": 7.5}
    inputs = {"pattern": "/tmp/sample.xy"}
    input_sha256 = {"pattern": "abc"}
    artifacts = {"project": "/tmp/run.gpx"}
    warnings: tuple[str, ...] = ()


def test_xrd_result_maps_to_partial_material_state() -> None:
    state = material_state_from_xrd(FakeXrdResult(), material_type="clinker")

    assert state.sample_id == "clinker-001"
    assert state.chemistry is None
    assert state.mineralogy is not None
    assert [phase.name for phase in state.mineralogy.phases] == ["Alite", "Belite"]
    assert state.measurements[0].engine == "GSAS-II"
    assert state.measurements[0].method_name == "minimal-phase-fraction"
    assert state.measurements[0].metrics["wR"] == 7.5
