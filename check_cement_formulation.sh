#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE="$ROOT/packages/cement-formulation"

python -m pip install -e "$PACKAGE[dev]"
python -m ruff check "$PACKAGE/src" "$PACKAGE/tests"
python -m pytest "$PACKAGE/tests" -q

rm -rf "$PACKAGE/dist" "$PACKAGE/build"
python -m build "$PACKAGE"
python -m twine check "$PACKAGE"/dist/*

python - <<'PY'
from brixta_cement_formulation import (
    CementComponent,
    CementComponentKind,
    CementRecipe,
    formulate_cement,
)

state = formulate_cement(
    CementRecipe(
        recipe_id="smoke",
        cement_family="custom",
        components=(
            CementComponent("clinker", CementComponentKind.CLINKER, 0.95),
            CementComponent("gypsum", CementComponentKind.GYPSUM, 0.05),
        ),
    )
)
assert state.clinker_factor == 0.95
assert state.sulfate_carrier_factor == 0.05
print("brixta-cement-formulation smoke: OK")
PY
