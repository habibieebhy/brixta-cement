#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv was not found."
  exit 1
fi

source .venv/bin/activate
python -m pip install -e "packages/cement-rawmix[dev]"
python -m ruff check packages/cement-rawmix/src packages/cement-rawmix/tests
python -m pytest packages/cement-rawmix/tests -q
rm -rf packages/cement-rawmix/dist packages/cement-rawmix/build
python -m build packages/cement-rawmix
python -m twine check packages/cement-rawmix/dist/*
echo "SUCCESS: brixta-cement-rawmix checks passed."
