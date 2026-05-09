#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python}"
if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
fi

"$PYTHON_BIN" run_workflow.py --stage all --mock
HOST="${HOST:-0.0.0.0}" "$PYTHON_BIN" webapp.py
