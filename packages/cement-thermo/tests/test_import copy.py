import brixta_cement_thermo


def test_package_imports() -> None:
    assert brixta_cement_thermo.__version__ == "0.2.0"
    assert brixta_cement_thermo.GemsEngine is not None
    assert brixta_cement_thermo.ThermoStateInput is not None
    assert brixta_cement_thermo.ThermoResult is not None
