from brixta_cement_xrd import EngineInfo


def test_engine_info_is_json_friendly() -> None:
    info = EngineInfo(
        engine="GSAS-II",
        engine_version="5.7.9",
        adapter_version="0.1.0",
        source_path="/opt/gsas2/GSASII",
        binary_path="/opt/gsas2/GSASII-bin/test",
        python_version="3.13.7",
        numpy_version="2.2.6",
    )

    assert info.to_dict()["engine"] == "GSAS-II"
    assert info.to_dict()["engine_version"] == "5.7.9"
