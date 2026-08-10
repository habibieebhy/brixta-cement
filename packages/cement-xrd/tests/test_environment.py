from pathlib import Path

import pytest

from brixta_cement_xrd.environment import GSASII_ENV_VAR, resolve_gsas2_root
from brixta_cement_xrd.errors import Gsas2UnavailableError


def _fake_gsas2_tree(tmp_path: Path) -> Path:
    root = tmp_path / "engine"
    package = root / "GSASII"
    package.mkdir(parents=True)
    (package / "GSASIIscriptable.py").write_text("# fake\n", encoding="utf-8")
    return root


def test_missing_environment_variable(monkeypatch) -> None:
    monkeypatch.delenv(GSASII_ENV_VAR, raising=False)

    with pytest.raises(Gsas2UnavailableError, match=GSASII_ENV_VAR):
        resolve_gsas2_root()


def test_resolves_installation_root_from_environment(tmp_path, monkeypatch) -> None:
    root = _fake_gsas2_tree(tmp_path)
    monkeypatch.setenv(GSASII_ENV_VAR, str(root))

    assert resolve_gsas2_root() == root.resolve()


def test_accepts_gsasii_package_directory_directly(tmp_path) -> None:
    root = _fake_gsas2_tree(tmp_path)

    assert resolve_gsas2_root(root / "GSASII") == root.resolve()


def test_rejects_invalid_installation_root(tmp_path) -> None:
    with pytest.raises(Gsas2UnavailableError, match="GSAS-II was not found"):
        resolve_gsas2_root(tmp_path)
