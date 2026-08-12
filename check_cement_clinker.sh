#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE="$ROOT/packages/cement-clinker"

python -m pip install -e "$PACKAGE[dev]"
python -m ruff check "$PACKAGE/src" "$PACKAGE/tests"
python -m pytest "$PACKAGE/tests" -q

rm -rf "$PACKAGE/dist" "$PACKAGE/build"
python -m build "$PACKAGE"
python -m twine check "$PACKAGE"/dist/*

python - <<'PY'
from brixta_cement_clinker import ClinkerChemistry, estimate_bogue

state = estimate_bogue(
    ClinkerChemistry(CaO=0.650, SiO2=0.215, Al2O3=0.052, Fe2O3=0.032),
    normalize=False,
)
assert state.phase_fraction("C3S") is not None
print("brixta-cement-clinker smoke: OK")
PY
