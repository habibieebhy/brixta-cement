from types import SimpleNamespace

from brixta_cement_xrd import (
    EngineInfo,
    Gsas2Engine,
    PhaseModel,
    RefinementRecipe,
    XrdAnalysisInput,
)
from brixta_cement_xrd.errors import Gsas2UnavailableError
from brixta_cement_xrd.result import XrdResult


def _engine_info() -> EngineInfo:
    return EngineInfo(
        engine="GSAS-II",
        engine_version="5.7.9",
        adapter_version="0.2.0",
        source_path="/opt/gsas2/GSASII",
        binary_path="/opt/gsas2/GSASII-bin/test",
        python_version="3.13.7",
        numpy_version="2.2.6",
    )


def test_engine_info_delegates_to_environment(monkeypatch) -> None:
    expected = _engine_info()
    monkeypatch.setattr(
        "brixta_cement_xrd.engine.inspect_gsas2",
        lambda path: expected,
    )

    engine = Gsas2Engine("/opt/gsas2")

    assert engine.available() is True
    assert engine.info() == expected
    assert engine.require_available() == expected


def test_engine_available_is_false_when_runtime_is_unavailable(monkeypatch) -> None:
    def unavailable(path):
        raise Gsas2UnavailableError("missing")

    monkeypatch.setattr(
        "brixta_cement_xrd.engine.inspect_gsas2",
        unavailable,
    )

    assert Gsas2Engine().available() is False


def test_engine_analyze_loads_runtime_and_delegates(monkeypatch, tmp_path) -> None:
    expected_info = _engine_info()
    fake_scriptable = SimpleNamespace()
    expected_result = XrdResult(
        run_id="run",
        sample_id="sample",
        started_at="start",
        completed_at="end",
        engine=expected_info,
        recipe_name="recipe",
        recipe_version="1",
        recipe_sha256="abc",
        phases=(),
        residuals={},
        inputs={},
        input_sha256={},
        artifacts={},
    )
    monkeypatch.setattr(
        "brixta_cement_xrd.engine.load_gsas2",
        lambda path: (expected_info, fake_scriptable),
    )
    monkeypatch.setattr(
        "brixta_cement_xrd.engine.run_quantitative_analysis",
        lambda **kwargs: expected_result,
    )

    request = XrdAnalysisInput(
        sample_id="sample",
        pattern_path=tmp_path / "pattern",
        instrument_path=tmp_path / "instrument",
        phases=(PhaseModel("Alite", tmp_path / "alite.cif"),),
        output_dir=tmp_path,
    )
    recipe = RefinementRecipe.minimal_phase_fraction()

    assert Gsas2Engine().analyze(request, recipe) is expected_result
