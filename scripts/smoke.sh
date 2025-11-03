#!/usr/bin/env bash
CACHE_DIR="${PYTHONPYCACHEPREFIX:-$(pwd)/.pyc-cache}"
export PYTHONPYCACHEPREFIX="$CACHE_DIR"
mkdir -p "$PYTHONPYCACHEPREFIX"

set -Eeuo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3.14}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

if [ -x scripts/smoke.local.sh ]; then
  bash scripts/smoke.local.sh
  exit 0
fi

ran_any=false

if find . -maxdepth 2 -type f -name '*.py' 2>/dev/null | grep -q .; then
  "$PYTHON_BIN" -m compileall -q -x '(^|/)(\.git|\.pyc-cache|\.venv|venv|env|archive)(/|$)' .
  ran_any=true
fi

if [ -f requirements.txt ]; then
  "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
  "$PYTHON_BIN" -m pip install -r requirements.txt
  ran_any=true
elif [ -f pyproject.toml ]; then
  "$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel
  "$PYTHON_BIN" -m pip install -e .
  ran_any=true
fi

if [ -d tests ] || [ -d test ] || ls test_*.py >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pip install pytest
  "$PYTHON_BIN" -m pytest -q
  ran_any=true
fi

if [ -f tox.ini ]; then
  "$PYTHON_BIN" -m pip install tox
  tox --skip-missing-interpreters
  ran_any=true
fi

if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi
  if command -v node >/dev/null 2>&1; then
    if node -e "const fs=require('fs');const s=(JSON.parse(fs.readFileSync('package.json')).scripts)||{};process.exit(s.test?0:1);"; then
      npm test -- --watch=false
      ran_any=true
    fi
    if node -e "const fs=require('fs');const s=(JSON.parse(fs.readFileSync('package.json')).scripts)||{};process.exit(s.build?0:1);"; then
      npm run build
      ran_any=true
    fi
    if node -e "const fs=require('fs');const s=(JSON.parse(fs.readFileSync('package.json')).scripts)||{};process.exit(s.lint?0:1);"; then
      npm run lint
      ran_any=true
    fi
  fi
fi

if [ -f Makefile ]; then
  if make -qp | grep -q '^lint:'; then
    make lint
    ran_any=true
  fi
  if make -qp | grep -q '^test:'; then
    make test
    ran_any=true
  elif make -qp | grep -q '^build:'; then
    make build
    ran_any=true
  fi
fi

if ! $ran_any; then
  echo "smoke.sh: No automated commands triggered; extend this script for repository-specific coverage."
fi
