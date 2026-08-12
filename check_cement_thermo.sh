#!/usr/bin/env bash
set -euo pipefail

# BRIXTA Cement Thermodynamics — local package validation.
# The scientific xGEMS/GEMS3K runtime is external and is checked only when available.

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv was not found."
  exit 1
fi

source .venv/bin/activate

echo "==> Installing brixta-cement-thermo development package"
python -m pip install -e "packages/cement-thermo[dev]"

echo "==> Running Ruff"
python -m ruff check packages/cement-thermo/src packages/cement-thermo/tests

echo "==> Running tests"
python -m pytest packages/cement-thermo/tests -q

echo "==> Building distributions"
rm -rf packages/cement-thermo/dist packages/cement-thermo/build
python -m build packages/cement-thermo
python -m twine check packages/cement-thermo/dist/*

echo "==> Thermodynamic engine doctor"
if python -c "import xgems" >/dev/null 2>&1; then
  brixta-thermo doctor
else
  echo "xGEMS is not installed in this Python environment; real-engine doctor skipped."
fi

echo
echo "SUCCESS: brixta-cement-thermo package checks passed."
