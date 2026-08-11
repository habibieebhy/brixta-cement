import json

from brixta_cement_xrd import EngineInfo, PhaseFraction, XrdResult


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


def test_engine_info_is_json_friendly() -> None:
    info = _engine_info()

    assert info.to_dict()["engine"] == "GSAS-II"
    assert info.to_dict()["engine_version"] == "5.7.9"


def test_xrd_result_writes_json(tmp_path) -> None:
    result = XrdResult(
        run_id="run-1",
        sample_id="clinker-001",
        started_at="start",
        completed_at="end",
        engine=_engine_info(),
        recipe_name="clinker-qpa",
        recipe_version="1",
        recipe_sha256="abc",
        phases=(PhaseFraction("Alite", 0.6, 0.01),),
        residuals={"wR": 7.2},
        inputs={"pattern": "/tmp/sample.xy"},
        input_sha256={"pattern": "hash"},
        artifacts={"gpx": "/tmp/run.gpx"},
    )

    path = result.write_json(tmp_path / "result.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["phases"][0]["name"] == "Alite"
    assert result.phases[0].percent == 60.0
