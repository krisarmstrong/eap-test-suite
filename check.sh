#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

make build
ruff check .
black --check .
python3 -m pytest
