import brixta_cement_rawmix


def test_package_imports() -> None:
    assert brixta_cement_rawmix.__version__ == "0.1.0"
    assert brixta_cement_rawmix.solve_raw_mix is not None
