#!/usr/bin/env bash
# Bring up the gateway, the Seal, the NVIDIA provider and the dogwatch sandbox on a plain Linux host (the GitHub Actions
# ubuntu-24.04 runner). Needs Docker Engine 28 or newer, the openshell package, and NVIDIA_API_KEY in the environment.
# Never prints a secret.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATE="$HOME/.local/state/dogwatch"; mkdir -p "$STATE" "$ROOT/evidence/boundary"
: "${NVIDIA_API_KEY:?NVIDIA_API_KEY is not set}"

python3 -m venv "$HOME/dwvenv" && "$HOME/dwvenv/bin/pip" -q install grpcio protobuf
printf '%s' '[["PASSPORT","K7654321"],["COC","654321/MUM/2018"],["NAME","SPECIMEN SEAFARER"],["PASSPORT","K1234567"],["COC","123456/MUM/2019"]]' > "$STATE/seal-values.json"
HOST_IP="$(hostname -I | awk '{print $1}')"
SEAL_ADDRESS="0.0.0.0:50061" SEAL_LOG="$ROOT/evidence/boundary/seal-decisions.jsonl" PYTHONPATH="$ROOT/seal" \
  nohup "$HOME/dwvenv/bin/python" -m seal.server < "$STATE/seal-values.json" > "$STATE/seal.log" 2>&1 &
sleep 3; cat "$STATE/seal.log"

mkdir -p "$HOME/.config/openshell"
cat > "$HOME/.config/openshell/gateway.toml" <<EOT
[openshell]
version = 2

[[openshell.supervisor.middleware]]
name = "dogwatch-seal"
grpc_endpoint = "http://$HOST_IP:50061"
allow_insecure_transport = true
max_payload_bytes = 4194304
timeout = "2s"
EOT
chmod 600 "$HOME/.config/openshell/gateway.toml"
export OPENSHELL_LOCAL_TLS_DIR="$HOME/.local/state/openshell/tls"; mkdir -p "$OPENSHELL_LOCAL_TLS_DIR"
openshell-gateway config preflight
openshell-gateway generate-certs --output-dir "$OPENSHELL_LOCAL_TLS_DIR" --server-san host.openshell.internal
# The installer may already have started a gateway without the Seal registered: stop any running one first.
systemctl --user stop openshell-gateway 2>/dev/null || true
sudo systemctl stop openshell-gateway 2>/dev/null || true
pkill -f openshell-gateway 2>/dev/null || true
for _ in $(seq 1 20); do ss -ltn | grep -q ':17670' || break; sleep 1; done
ss -ltn | grep -q ':17670' && { echo "port 17670 still in use by:"; ss -ltnp | grep ':17670'; exit 1; }
OPENSHELL_DRIVERS=docker nohup openshell-gateway > "$STATE/gateway.log" 2>&1 &
for _ in $(seq 1 90); do ss -ltn | grep -q ':17670' && break; sleep 2; done
ss -ltn | grep -q ':17670' || { sed 's/\x1b\[[0-9;]*m//g' "$STATE/gateway.log" | tail -20; exit 1; }
echo "gateway processes:"; pgrep -af openshell-gateway || true
echo "gateway log (middleware lines):"; sed 's/\[[0-9;]*m//g' "$STATE/gateway.log" | grep -i -E "middleware|config|seal|listen" | head -10 || true
openshell gateway add https://127.0.0.1:17670 --local --name openshell >/dev/null 2>&1 || true

docker build -q -f "$ROOT/openshell/sandbox/Dockerfile" -t dogwatch-sandbox:local "$ROOT"
openshell provider profile import -f "$ROOT/openshell/profiles/nvidia-build.yaml" --global
openshell provider create --name nvidia --type nvidia --credential NVIDIA_API_KEY --global-profile
nohup openshell sandbox create --name dogwatch --from dogwatch-sandbox:local --provider nvidia \
  --policy "$ROOT/openshell/policy/dogwatch.yaml" -- sleep 7200 > "$STATE/sandbox-create.log" 2>&1 &
for _ in $(seq 1 120); do
  openshell sandbox get dogwatch 2>/dev/null | grep -qi 'ready' && break
  grep -qi 'error' "$STATE/sandbox-create.log" && { sed 's/\x1b\[[0-9;]*m//g' "$STATE/sandbox-create.log" | tail -15; exit 1; }
  sleep 3
done
openshell sandbox get dogwatch > "$STATE/sandbox-get.txt" 2>&1 || true
sed 's/\[[0-9;]*m//g' "$STATE/sandbox-get.txt" > "$STATE/sandbox-get.clean.txt"
head -12 "$STATE/sandbox-get.clean.txt" || true
grep -qi "phase: *ready" "$STATE/sandbox-get.clean.txt" || { echo "sandbox is not Ready"; exit 1; }
