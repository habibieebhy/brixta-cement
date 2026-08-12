from __future__ import annotations

import importlib
import importlib.metadata
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from .errors import ThermoConfigurationError, ThermoUnavailableError

GEMS_SYSTEM_ENV = "BRIXTA_GEMS_SYSTEM"


@dataclass(frozen=True)
class ThermoEngineInfo:
    engine: str
    engine_version: str
    adapter_version: str
    python_version: str
    module_path: str
    chemical_engine_available: bool
    system_path: str | None

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "engine": self.engine,
            "engine_version": self.engine_version,
            "adapter_version": self.adapter_version,
            "python_version": self.python_version,
            "module_path": self.module_path,
            "chemical_engine_available": self.chemical_engine_available,
            "system_path": self.system_path,
        }


def _distribution_version() -> str:
    try:
        return importlib.metadata.version("xgems")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _module_path(module: ModuleType) -> str:
    path = getattr(module, "__file__", None)
    return str(path) if path is not None else "unknown"


def configured_system_path() -> Path | None:
    raw = os.environ.get(GEMS_SYSTEM_ENV)
    if raw is None or not raw.strip():
        return None

    path = Path(raw).expanduser().resolve()
    if not path.exists():
        raise ThermoConfigurationError(
            f"{GEMS_SYSTEM_ENV} points to a missing path: {path}"
        )
    return path


def import_xgems() -> ModuleType:
    try:
        return importlib.import_module("xgems")
    except Exception as exc:
        raise ThermoUnavailableError(
            "xGEMS is not importable in this Python environment. "
            "Install/configure the official xGEMS runtime before running "
            "thermodynamic calculations."
        ) from exc


def inspect_environment(*, adapter_version: str) -> ThermoEngineInfo:
    module = import_xgems()
    chemical_engine_available = hasattr(module, "ChemicalEngine")
    if not chemical_engine_available:
        raise ThermoUnavailableError(
            "xGEMS imported, but the expected ChemicalEngine API is not exposed."
        )

    system_path = configured_system_path()

    return ThermoEngineInfo(
        engine="xGEMS/GEMS3K",
        engine_version=_distribution_version(),
        adapter_version=adapter_version,
        python_version=platform.python_version(),
        module_path=_module_path(module),
        chemical_engine_available=True,
        system_path=None if system_path is None else str(system_path),
    )
