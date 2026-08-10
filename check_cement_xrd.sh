#!/usr/bin/env bash
set -euo pipefail

# BRIXTA Cement XRD — local validation.
# Run from the repository root:
#
#   bash check_cement_xrd.sh

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv was not found."
  echo "Create it first with a GSAS-II-compatible Python runtime."
  exit 1
fi

echo "==> Activating virtual environment"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing brixta-cement-xrd development dependencies"
python -m pip install -e "packages/cement-xrd[dev]"

echo "==> Running Ruff"
python -m ruff check \
  packages/cement-xrd/src \
  packages/cement-xrd/tests

echo "==> Running tests"
python -m pytest packages/cement-xrd/tests -q

echo "==> Building distributions"
rm -rf packages/cement-xrd/dist packages/cement-xrd/build
python -m build packages/cement-xrd
python -m twine check packages/cement-xrd/dist/*

if [[ -z "${BRIXTA_GSASII_PATH:-}" ]] \
  && [[ -f "$HOME/brixta-engines/GSASII/GSASIIscriptable.py" ]]; then
  export BRIXTA_GSASII_PATH="$HOME/brixta-engines"
fi

if [[ -n "${BRIXTA_GSASII_PATH:-}" ]]; then
  echo "==> Running real GSAS-II doctor"
  brixta-xrd doctor
else
  echo "==> BRIXTA_GSASII_PATH not configured; external GSAS-II doctor skipped"
fi

echo
echo "SUCCESS: brixta-cement-xrd checks passed."
