from __future__ import annotations

import argparse
import json

from . import __version__
from .engine import GemsEngine
from .errors import ThermoError


def _doctor(as_json: bool) -> int:
    engine = GemsEngine(adapter_version=__version__)
    try:
        info = engine.require_available()
    except ThermoError as exc:
        if as_json:
            print(json.dumps({"ready": False, "error": str(exc)}, indent=2))
        else:
            print("GEMS/xGEMS: NOT READY")
            print(str(exc))
        return 1

    if as_json:
        payload = {"ready": True, **info.to_dict()}
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("GEMS/xGEMS: READY")
        print(f"Engine version:  {info.engine_version}")
        print(f"Adapter version: {info.adapter_version}")
        print(f"Python:           {info.python_version}")
        print(f"Module:           {info.module_path}")
        print(f"ChemicalEngine:   {'yes' if info.chemical_engine_available else 'no'}")
        print(f"System:           {info.system_path or 'not configured'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brixta-thermo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check the external xGEMS/GEMS3K runtime")
    doctor.add_argument("--json", action="store_true", help="Emit JSON diagnostics")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "doctor":
        return _doctor(args.json)
    raise AssertionError(f"unhandled command: {args.command}")
