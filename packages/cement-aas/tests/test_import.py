from basyx.aas import model

import brixta_cement_aas


def test_package_imports() -> None:
    assert brixta_cement_aas.__version__ == "0.1.0"
    assert model is not None