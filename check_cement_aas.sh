#!/usr/bin/env bash
set -euo pipefail

# BRIXTA Cement — Phase 1A local validation
# Run this script from the repository root:
#
#   bash check_cement_aas.sh
#
# Expected repository:
#   https://github.com/habibieebhy/brixta-cement

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv was not found."
  echo "Create it first with:"
  echo "  python3 -m venv .venv"
  exit 1
fi

echo "==> Activating virtual environment"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing/updating brixta-cement-aas development dependencies"
python -m pip install -e "packages/cement-aas[dev]"

echo "==> Running Ruff"
python -m ruff check   packages/cement-aas/src   packages/cement-aas/tests   examples

echo "==> Running tests"
python -m pytest packages/cement-aas/tests -q

echo
echo "SUCCESS: brixta-cement-aas local checks passed."