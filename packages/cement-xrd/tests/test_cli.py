from brixta_cement_xrd.cli import _phase_argument, main


def test_phase_argument() -> None:
    phase = _phase_argument("Alite=/tmp/alite.cif")
    assert phase.name == "Alite"
    assert str(phase.cif_path) == "/tmp/alite.cif"


def test_cli_help_is_available() -> None:
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
