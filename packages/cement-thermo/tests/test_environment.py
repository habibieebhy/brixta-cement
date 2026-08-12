from __future__ import annotations

from types import ModuleType

import pytest

from brixta_cement_thermo import ThermoConfigurationError, environment


def test_missing_configured_system_path_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    missing = tmp_path / "missing"
    monkeypatch.setenv(environment.GEMS_SYSTEM_ENV, str(missing))

    with pytest.raises(ThermoConfigurationError, match="missing path"):
        environment.configured_system_path()


def test_existing_system_path_is_accepted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    system = tmp_path / "cement-system"
    system.mkdir()
    monkeypatch.setenv(environment.GEMS_SYSTEM_ENV, str(system))

    assert environment.configured_system_path() == system.resolve()


def test_environment_accepts_xgems_with_chemical_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = ModuleType("xgems")
    fake.__file__ = "/tmp/xgems.so"
    fake.ChemicalEngine = object  # type: ignore[attr-defined]

    monkeypatch.delenv(environment.GEMS_SYSTEM_ENV, raising=False)
    monkeypatch.setattr(environment, "import_xgems", lambda: fake)
    monkeypatch.setattr(environment, "_distribution_version", lambda: "test-version")

    info = environment.inspect_environment(adapter_version="0.1.0")

    assert info.engine == "xGEMS/GEMS3K"
    assert info.engine_version == "test-version"
    assert info.chemical_engine_available is True
    assert info.system_path is None
