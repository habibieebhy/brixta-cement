from __future__ import annotations

from pathlib import Path

from .environment import inspect_gsas2
from .errors import Gsas2UnavailableError
from .result import EngineInfo


class Gsas2Engine:
    """Thin BRIXTA boundary around an external GSAS-II installation."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = path

    @property
    def path(self) -> str | Path | None:
        """Return the configured GSAS-II path, if explicitly provided."""

        return self._path

    def available(self) -> bool:
        """Return whether the external GSAS-II runtime is usable."""

        try:
            self.info()
        except Gsas2UnavailableError:
            return False
        return True

    def info(self) -> EngineInfo:
        """Return normalized metadata for the external GSAS-II runtime."""

        return inspect_gsas2(self._path)

    def require_available(self) -> EngineInfo:
        """Require a usable GSAS-II runtime and return its metadata."""

        return self.info()
