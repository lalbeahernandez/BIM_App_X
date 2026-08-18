#!/usr/bin/env bash
set -euo pipefail
python scripts/verify_harness.py
make lint
make typecheck
make test
make smoke
