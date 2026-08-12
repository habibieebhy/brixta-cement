#!/usr/bin/env bash
set -euo pipefail

# BRIXTA Cement AAS local validation.
# Run this script from the repository root:
#
#   bash check_cement_aas.sh

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv was not found."
  echo "Create it first with:"
  echo "  python3 -m venv .venv"
  exit 1
fi

echo "==> Activating virtual environment"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing local brixta-cement-material dependency"
python -m pip install -e "packages/cement-material"

echo "==> Installing/updating brixta-cement-aas development dependencies"
python -m pip install -e "packages/cement-aas[dev]"

echo "==> Running Ruff"
python -m ruff check packages/cement-aas/src packages/cement-aas/tests examples

echo "==> Running tests"
python -m pytest packages/cement-aas/tests -q

echo
echo "SUCCESS: brixta-cement-aas local checks passed."
