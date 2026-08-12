from __future__ import annotations

from .environment import ThermoEngineInfo, inspect_environment


class GemsEngine:
    """Thin BRIXTA boundary around the external xGEMS/GEMS3K runtime."""

    def __init__(self, *, adapter_version: str) -> None:
        self._adapter_version = adapter_version

    def available(self) -> bool:
        try:
            self.info()
        except RuntimeError:
            return False
        return True

    def info(self) -> ThermoEngineInfo:
        return inspect_environment(adapter_version=self._adapter_version)

    def require_available(self) -> ThermoEngineInfo:
        return self.info()
