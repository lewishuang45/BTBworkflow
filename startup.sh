#!/usr/bin/env bash
set -euo pipefail

python run_workflow.py --stage all --mock
HOST=0.0.0.0 python webapp.py
