from basyx.aas.adapter.json.json_deserialization import read_aas_json_file

from brixta_cement_aas import build_reference_pyro_line, write_aasx, write_json


def test_json_round_trip(tmp_path) -> None:
    bundle = build_reference_pyro_line("plant-001", "pyro-01")
    output = write_json(bundle, tmp_path / "pyro-line.json")

    restored = read_aas_json_file(str(output), failsafe=False)
    assert restored.get_item(bundle.aas_id) is not None
    assert restored.get_item(bundle.topology_id) is not None


def test_aasx_export(tmp_path) -> None:
    bundle = build_reference_pyro_line("plant-001", "pyro-01")
    output = write_aasx(bundle, tmp_path / "pyro-line.aasx")

    assert output.exists()
    assert output.stat().st_size > 0