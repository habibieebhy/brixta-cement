import brixta_cement_xrd


def test_package_imports() -> None:
    assert brixta_cement_xrd.__version__ == "0.2.0"
    assert brixta_cement_xrd.Gsas2Engine is not None
    assert brixta_cement_xrd.XrdAnalysisInput is not None
    assert brixta_cement_xrd.XrdResult is not None
