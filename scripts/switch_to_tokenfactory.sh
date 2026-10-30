#!/usr/bin/env bash
# Switch Dogwatch from the NVIDIA API Catalog development route to Nebius Token Factory and re-run the live evidence on it.
# Needs NEBIUS_API_KEY in .env. Run from the repository root: bash scripts/switch_to_tokenfactory.sh
#
# What it does, in order:
#   1. sets MODEL_ROUTE=tokenfactory in .env
#   2. imports and attaches the Nebius Token Factory OpenShell provider profile (skipped, and said so, if openshell is absent)
#   3. re-runs the Phase 2 probe (model ids, thinking on versus off, schema enforcement) on Token Factory
#   4. re-runs P6 (engine against Nemotron), P8 (reading) and P12 (cost) on Token Factory
#   5. regenerates docs/FACTS.json and web/data/recorded.json
# Results from the earlier development route are kept under eval/results/devroute/ so no number is overwritten or relabelled.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python}"
[ -x .venv/bin/python ] && PY=.venv/bin/python
[ -x .venv/Scripts/python.exe ] && PY=.venv/Scripts/python.exe

set -a; . <(tr -d '\r' < .env | grep -E '^[A-Za-z_][A-Za-z0-9_]*='); set +a
NEBIUS_API_KEY="${NEBIUS_API_KEY_OVERRIDE:-$NEBIUS_API_KEY}"   # the override exists only for the dry run
: "${NEBIUS_API_KEY:?NEBIUS_API_KEY is empty in .env}"
export NEBIUS_API_KEY

if [ -z "${DRY_RUN:-}" ]; then
if grep -q '^MODEL_ROUTE=' .env; then sed -i 's/^MODEL_ROUTE=.*/MODEL_ROUTE=tokenfactory/' .env; else echo 'MODEL_ROUTE=tokenfactory' >> .env; fi
fi
export MODEL_ROUTE=tokenfactory

[ -z "${DRY_RUN:-}" ] && mkdir -p eval/results/devroute || true
[ -n "${DRY_RUN:-}" ] || for f in p6_model_alone p8_reading p8_reading_v1 p9_drift p10_unattended p12_cost; do
  [ -f "eval/results/$f.json" ] && cp -n "eval/results/$f.json" "eval/results/devroute/$f.json"
done

if command -v openshell >/dev/null 2>&1; then
  openshell provider profile import -f openshell/profiles/nebius-token-factory.yaml --global || true
  openshell provider create --name nebius-token-factory --type nebius-token-factory --credential NEBIUS_API_KEY --global-profile || true
  echo "profile attached as provider; attach it to a sandbox with --provider nebius-token-factory"
else
  echo "openshell not found: profile attachment skipped"
fi

"$PY" scripts/probe.py tokenfactory
"$PY" eval/run_model_alone.py tokenfactory
"$PY" eval/run_reading.py tokenfactory
"$PY" eval/run_cost.py
"$PY" scripts/facts.py
"$PY" scripts/export_recorded.py
"$PY" scripts/check_facts.py
echo "done: results on Route: Nebius Token Factory. Review eval/results/ and update README and PROOF.md route labels."
