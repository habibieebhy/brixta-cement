from brixta_cement_xrd import EngineInfo, Gsas2Engine
from brixta_cement_xrd.errors import Gsas2UnavailableError


def _engine_info() -> EngineInfo:
    return EngineInfo(
        engine="GSAS-II",
        engine_version="5.7.9",
        adapter_version="0.1.0",
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
