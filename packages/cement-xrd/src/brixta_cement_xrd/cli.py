from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .engine import Gsas2Engine
from .errors import Gsas2UnavailableError


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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the BRIXTA Cement XRD command-line interface."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return _doctor(args.path, args.json)

    parser.error(f"Unknown command: {args.command}")
    return 2
