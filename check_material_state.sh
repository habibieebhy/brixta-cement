#!/usr/bin/env bash
set -euo pipefail

# BRIXTA Material State + AAS vertical-slice validation.
# Run from the repository root:
#
#   bash check_material_state.sh

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv was not found."
  echo "Create it first with: python3 -m venv .venv"
  exit 1
fi

echo "==> Activating virtual environment"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing local Material State package"
python -m pip install -e "packages/cement-material[dev]"

echo "==> Installing local AAS package against local Material State"
python -m pip install -e "packages/cement-aas[dev]"

echo "==> Running Ruff"
python -m ruff check \
  packages/cement-material/src \
  packages/cement-material/tests \
  packages/cement-aas/src \
  packages/cement-aas/tests \
  examples

echo "==> Running Material State tests"
python -m pytest packages/cement-material/tests -q

echo "==> Running AAS tests"
python -m pytest packages/cement-aas/tests -q

echo "==> Building brixta-cement-material"
rm -rf packages/cement-material/dist packages/cement-material/build
python -m build packages/cement-material
python -m twine check packages/cement-material/dist/*

echo "==> Building brixta-cement-aas"
rm -rf packages/cement-aas/dist packages/cement-aas/build
python -m build packages/cement-aas
python -m twine check packages/cement-aas/dist/*

echo
echo "SUCCESS: MaterialState -> AAS vertical slice passed."
