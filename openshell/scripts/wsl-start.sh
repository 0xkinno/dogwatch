#!/usr/bin/env bash
# Start Docker and the OpenShell gateway by hand, for WSL2 builds where systemd is not PID 1
# (the packaged service unit needs a user systemd session). Mirrors openshell-gateway.service.
# Leaves both running in the background; logs go to ~/.local/state/dogwatch/.
set -euo pipefail
LOG="$HOME/.local/state/dogwatch"
mkdir -p "$LOG"

if ! docker info >/dev/null 2>&1; then
  nohup dockerd > "$LOG/dockerd.log" 2>&1 &
  for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && break; sleep 1; done
fi
docker info >/dev/null 2>&1 || { echo "docker did not start, see $LOG/dockerd.log" >&2; exit 1; }

export OPENSHELL_LOCAL_TLS_DIR="$HOME/.local/state/openshell/tls"
mkdir -p "$OPENSHELL_LOCAL_TLS_DIR" "$HOME/.local/state/openshell/gateway"
if ! pgrep -x openshell-gatew >/dev/null 2>&1; then
  openshell-gateway config preflight
  openshell-gateway generate-certs --output-dir "$OPENSHELL_LOCAL_TLS_DIR" --server-san host.openshell.internal
  nohup openshell-gateway > "$LOG/gateway.log" 2>&1 &
  sleep 5
fi
openshell gateway add https://127.0.0.1:17670 --local --name openshell 2>&1 | tail -2 || true
openshell gateway list 2>&1 | head -5
echo "gateway log: $LOG/gateway.log"
