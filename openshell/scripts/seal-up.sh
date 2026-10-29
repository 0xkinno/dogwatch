#!/usr/bin/env bash
# Start the Seal, register it with the gateway (fail closed is set in the sandbox policy), and restart the gateway.
# Values the Seal protects come from SEAL_VALUES (a JSON file of [kind, value] pairs kept outside the repository).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATE="$HOME/.local/state/dogwatch"
VENV="$HOME/dwvenv"
VALUES="${SEAL_VALUES:-$STATE/seal-values.json}"
PORT="${SEAL_PORT:-50061}"
mkdir -p "$STATE" "$ROOT/evidence/boundary"

[ -x "$VENV/bin/python" ] || { python3 -m venv "$VENV"; "$VENV/bin/pip" -q install grpcio protobuf; }
[ -f "$VALUES" ] || { echo "missing $VALUES" >&2; exit 1; }

pkill -f "seal.server" 2>/dev/null || true
sleep 1
HOST_IP="$(ip -4 addr show eth0 | awk '/inet /{print $2}' | cut -d/ -f1 | head -1)"
SEAL_ADDRESS="0.0.0.0:$PORT" SEAL_LOG="$ROOT/evidence/boundary/seal-decisions.jsonl" PYTHONPATH="$ROOT/seal" \
  nohup "$VENV/bin/python" -m seal.server < "$VALUES" > "$STATE/seal.log" 2>&1 &
sleep 2
cat "$STATE/seal.log"

mkdir -p "$HOME/.config/openshell"
cat > "$HOME/.config/openshell/gateway.toml" <<EOF
[openshell]
version = 2

[[openshell.supervisor.middleware]]
name = "dogwatch-seal"
grpc_endpoint = "http://$HOST_IP:$PORT"
allow_insecure_transport = true
max_payload_bytes = 4194304
timeout = "2s"
EOF
chmod 600 "$HOME/.config/openshell/gateway.toml"

pkill -x openshell-gatew 2>/dev/null || true
sleep 2
export DOCKER_HOST="${DOCKER_HOST_OPENSHELL:-unix:///var/run/docker28.sock}"
export OPENSHELL_LOCAL_TLS_DIR="$HOME/.local/state/openshell/tls"
nohup openshell-gateway > "$STATE/gateway.log" 2>&1 &
sleep 6
tail -6 "$STATE/gateway.log"
echo "seal at $HOST_IP:$PORT"
