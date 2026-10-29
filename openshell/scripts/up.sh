#!/usr/bin/env bash
# Bring up the Dogwatch stack inside WSL2 or Linux with Docker. Needs the openshell CLI installed (see PLATFORM_PROBE.md).
set -euo pipefail
cd "$(dirname "$0")/../.."
set -a; [ -f .env ] && . ./.env; set +a
: "${NEBIUS_API_KEY:?set NEBIUS_API_KEY in .env}"

openshell provider profile import -f openshell/profiles/nebius-token-factory.yaml --global
openshell provider profile import -f openshell/profiles/tavily.yaml --global

# Seal: values arrive on stdin from the Radio Officer and stay in memory.
SEAL_ADDRESS="${SEAL_ADDRESS:-127.0.0.1:50061}" python -m seal.server < "${DOGWATCH_SEAL_VALUES:-/dev/null}" &
echo $! > .seal.pid

openshell sandbox create dogwatch \
  --provider nebius-token-factory --provider tavily \
  --policy openshell/policy/dogwatch.yaml \
  -- python3 -m dogwatch.watch.runner
