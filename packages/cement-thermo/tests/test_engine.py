import pytest

from brixta_cement_thermo.engine import GemsEngine
from brixta_cement_thermo.errors import ThermoUnavailableError


def test_available_false_when_runtime_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = GemsEngine(adapter_version="0.1.0")

    def fail():
        raise ThermoUnavailableError("missing")

    monkeypatch.setattr(engine, "info", fail)
    assert engine.available() is False
