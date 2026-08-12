import brixta_cement_thermo


def test_package_imports() -> None:
    assert brixta_cement_thermo.__version__ == "0.1.0"
    assert brixta_cement_thermo.GemsEngine is not None
