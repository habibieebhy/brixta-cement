import brixta_cement_material


def test_package_imports() -> None:
    assert brixta_cement_material.__version__ == "0.1.0"
    assert brixta_cement_material.MATERIAL_STATE_SCHEMA_VERSION == "1.0"
