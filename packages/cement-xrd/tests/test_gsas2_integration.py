import os

import pytest

from brixta_cement_xrd import Gsas2Engine

pytestmark = pytest.mark.skipif(
    not os.environ.get("BRIXTA_GSASII_PATH"),
    reason="BRIXTA_GSASII_PATH is not configured",
)


def test_real_gsas2_runtime_is_available() -> None:
    info = Gsas2Engine().require_available()

    assert info.engine == "GSAS-II"
    assert info.engine_version
    assert info.source_path
    assert info.binary_path
