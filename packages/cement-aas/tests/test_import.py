from basyx.aas import model

import brixta_cement_aas


def test_package_imports() -> None:
    assert brixta_cement_aas.__version__ == "0.2.0"
    assert brixta_cement_aas.build_material_state_submodel is not None
    assert model is not None
