from __future__ import annotations

import importlib
import os
import sys
from importlib.metadata import version
from pathlib import Path
from types import ModuleType

from .errors import Gsas2UnavailableError
from .result import EngineInfo

GSASII_ENV_VAR = "BRIXTA_GSASII_PATH"


def resolve_gsas2_root(path: str | Path | None = None) -> Path:
    """Resolve the directory that contains the upstream ``GSASII`` package."""

    raw_path = path if path is not None else os.environ.get(GSASII_ENV_VAR)
    if raw_path is None or not str(raw_path).strip():
        raise Gsas2UnavailableError(
            f"{GSASII_ENV_VAR} is not set. Point it to the directory containing "
            "GSASII/GSASIIscriptable.py."
        )

    candidate = Path(raw_path).expanduser().resolve()

    if (candidate / "GSASIIscriptable.py").is_file() and candidate.name == "GSASII":
        candidate = candidate.parent

    scriptable = candidate / "GSASII" / "GSASIIscriptable.py"
    if not scriptable.is_file():
        raise Gsas2UnavailableError(
            f"GSAS-II was not found under {candidate}. Expected {scriptable}."
        )

    return candidate


def _import_gsas2(root: Path) -> tuple[ModuleType, ModuleType]:
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)

    try:
        scriptable = importlib.import_module("GSASII.GSASIIscriptable")
        gsas_path = importlib.import_module("GSASII.GSASIIpath")
    except Exception as exc:
        raise Gsas2UnavailableError(
            f"GSAS-II exists at {root}, but its scripting runtime could not be imported: {exc}"
        ) from exc

    loaded_file = Path(getattr(scriptable, "__file__", "")).resolve()
    expected_package = (root / "GSASII").resolve()
    if expected_package not in loaded_file.parents:
        raise Gsas2UnavailableError(
            "A different GSAS-II installation is already loaded in this Python process. "
            f"Loaded: {loaded_file}. Requested root: {root}."
        )

    return scriptable, gsas_path


def _require_binary_path(gsas_path: ModuleType) -> Path:
    raw_binary_path = getattr(gsas_path, "binaryPath", "")
    if not raw_binary_path:
        raise Gsas2UnavailableError(
            "GSAS-II imported, but no binary directory was loaded. "
            "Install a matching upstream GSAS-II binary bundle."
        )

    binary_path = Path(raw_binary_path).expanduser().resolve()
    if not binary_path.is_dir():
        raise Gsas2UnavailableError(
            f"GSAS-II binary directory does not exist: {binary_path}"
        )

    missing = [
        module_name
        for module_name in ("pyspg", "pypowder")
        if not any(binary_path.glob(f"{module_name}.*"))
    ]
    if missing:
        names = ", ".join(missing)
        raise Gsas2UnavailableError(
            f"GSAS-II binary directory {binary_path} is missing required module(s): {names}."
        )

    return binary_path


def _engine_info(root: Path, gsas_path: ModuleType, binary_path: Path) -> EngineInfo:
    try:
        engine_version = str(gsas_path.GetVersionTag())
    except Exception as exc:
        raise Gsas2UnavailableError(
            f"GSAS-II loaded from {root}, but its version could not be determined: {exc}"
        ) from exc

    try:
        numpy_module = importlib.import_module("numpy")
        numpy_version = str(numpy_module.__version__)
    except Exception as exc:
        raise Gsas2UnavailableError(
            f"GSAS-II loaded from {root}, but NumPy metadata could not be read: {exc}"
        ) from exc

    source_path = Path(getattr(gsas_path, "path2GSAS2", root / "GSASII")).resolve()

    return EngineInfo(
        engine="GSAS-II",
        engine_version=engine_version,
        adapter_version=version("brixta-cement-xrd"),
        source_path=str(source_path),
        binary_path=str(binary_path),
        python_version=".".join(str(part) for part in sys.version_info[:3]),
        numpy_version=numpy_version,
    )


def load_gsas2(path: str | Path | None = None) -> tuple[EngineInfo, ModuleType]:
    """Load and validate GSAS-II, returning metadata and its scripting module."""

    root = resolve_gsas2_root(path)
    scriptable, gsas_path = _import_gsas2(root)
    binary_path = _require_binary_path(gsas_path)
    return _engine_info(root, gsas_path, binary_path), scriptable


def inspect_gsas2(path: str | Path | None = None) -> EngineInfo:
    """Import GSAS-II and return normalized runtime metadata."""

    info, _ = load_gsas2(path)
    return info
