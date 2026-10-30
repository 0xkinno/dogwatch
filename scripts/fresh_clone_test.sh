#!/usr/bin/env bash
# Fresh-clone test: clone into a temporary folder and follow the README offline steps exactly. Records time and failures.
# Usage: bash scripts/fresh_clone_test.sh [repo_url_or_path]   (default: the GitHub repository)
set -u
SRC="${1:-https://github.com/0xkinno/dogwatch.git}"
PYBIN="${PYTHON:-python}"
T="$(mktemp -d)"; cd "$T"
start=$(date +%s); fail=0
step() { s=$(date +%s); echo "== $1"; shift; "$@" > "$T/step.log" 2>&1 || { echo "FAILED: $*"; tail -15 "$T/step.log"; fail=1; }; echo "   $(( $(date +%s) - s )) s"; }
step "git clone" git clone -q "$SRC" dogwatch
cd dogwatch
step "python -m venv .venv" "$PYBIN" -m venv .venv
if [ -x .venv/Scripts/python.exe ]; then PIP=.venv/Scripts/python.exe; else PIP=.venv/bin/python; fi
step "pip install -r requirements.txt" "$PIP" -m pip install -q -r requirements.txt
step "core tests" bash -c "cd core && ../$PIP -m pytest -q"
step "radio tests" bash -c "cd radio && ../$PIP -m pytest -q"
step "seal tests" bash -c "cd seal && ../$PIP -m pytest -q"
step "python eval/run_seal_corpus.py" "$PIP" eval/run_seal_corpus.py
step "python eval/run_conventions.py" "$PIP" eval/run_conventions.py
step "python scripts/check_facts.py" "$PIP" scripts/check_facts.py
step "python scripts/check_copy.py" "$PIP" scripts/check_copy.py
echo "TOTAL $(( $(date +%s) - start )) s, failures: $fail, clone of: $SRC"
exit $fail
