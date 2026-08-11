from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .engine import Gsas2Engine
from .errors import Gsas2Error, Gsas2UnavailableError
from .inputs import PhaseModel, RefinementRecipe, XrdAnalysisInput


def _phase_argument(value: str) -> PhaseModel:
    try:
        name, path = value.split("=", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Phase must be supplied as NAME=/path/to/model.cif"
        ) from exc
    if not name.strip() or not path.strip():
        raise argparse.ArgumentTypeError("Phase must be supplied as NAME=/path/to/model.cif")
    return PhaseModel(name=name.strip(), cif_path=path.strip())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brixta-xrd",
        description="BRIXTA Cement XRD utilities.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser(
        "doctor",
        help="Check the external GSAS-II runtime.",
    )
    doctor.add_argument(
        "--path",
        help="GSAS-II installation root. Overrides BRIXTA_GSASII_PATH.",
    )
    doctor.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON.",
    )

    analyze = subparsers.add_parser(
        "analyze",
        help="Run one quantitative powder-XRD refinement with an explicit recipe.",
    )
    analyze.add_argument("--sample-id", required=True)
    analyze.add_argument("--pattern", required=True, type=Path)
    analyze.add_argument("--instrument", required=True, type=Path)
    analyze.add_argument(
        "--phase",
        action="append",
        required=True,
        type=_phase_argument,
        help="Candidate phase as NAME=/path/to/model.cif. Repeat for every phase.",
    )
    analyze.add_argument("--recipe", required=True, type=Path)
    analyze.add_argument("--output-dir", required=True, type=Path)
    analyze.add_argument("--data-format", default=None)
    analyze.add_argument("--data-bank", type=int, default=None)
    analyze.add_argument("--instrument-bank", type=int, default=None)
    analyze.add_argument(
        "--path",
        help="GSAS-II installation root. Overrides BRIXTA_GSASII_PATH.",
    )
    analyze.add_argument("--json", action="store_true")

    return parser


def _doctor(path: str | None, as_json: bool) -> int:
    engine = Gsas2Engine(path)

    try:
        info = engine.require_available()
    except Gsas2UnavailableError as exc:
        if as_json:
            print(json.dumps({"available": False, "error": str(exc)}, indent=2))
        else:
            print("BRIXTA Cement XRD")
            print("GSAS-II: NOT READY")
            print(str(exc))
        return 1

    payload = {"available": True, **info.to_dict()}
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("BRIXTA Cement XRD")
        print("GSAS-II: READY")
        print(f"Engine version:  {info.engine_version}")
        print(f"Adapter version: {info.adapter_version}")
        print(f"Python:           {info.python_version}")
        print(f"NumPy:            {info.numpy_version}")
        print(f"Source:           {info.source_path}")
        print(f"Binaries:         {info.binary_path}")

    return 0


def _analyze(args: argparse.Namespace) -> int:
    engine = Gsas2Engine(args.path)
    request = XrdAnalysisInput(
        sample_id=args.sample_id,
        pattern_path=args.pattern,
        instrument_path=args.instrument,
        phases=tuple(args.phase),
        output_dir=args.output_dir,
        pattern_format_hint=args.data_format,
        data_bank=args.data_bank,
        instrument_bank=args.instrument_bank,
    )
    recipe = RefinementRecipe.from_json(args.recipe)
    result = engine.analyze(request, recipe)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"Sample: {result.sample_id}")
        print(f"Run:    {result.run_id}")
        for phase in result.phases:
            print(f"{phase.name}: {phase.percent:.4f}% ± {phase.uncertainty * 100:.4f}%")
        print(f"GPX:    {result.artifacts['gpx']}")
        print(f"Result: {result.artifacts['result_json']}")
        for warning in result.warnings:
            print(f"WARNING: {warning}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the BRIXTA Cement XRD command-line interface."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "doctor":
            return _doctor(args.path, args.json)
        if args.command == "analyze":
            return _analyze(args)
    except Gsas2Error as exc:
        parser.exit(1, f"ERROR: {exc}\n")

    parser.error(f"Unknown command: {args.command}")
    return 2
