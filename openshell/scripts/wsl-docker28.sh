#!/usr/bin/env bash
# OpenShell needs Docker Engine 28 or newer (support matrix). WSL here ships 27.1.1, whose daemon rejects the
# copyUIDGID upload the Docker driver uses ("getent unable to find entry 1000:1000"). Rather than upgrade the
# system daemon (other containers depend on it), run a second, isolated 28.x daemon on its own socket.
set -euo pipefail
VER="${DOCKER_STATIC_VERSION:-28.0.4}"
DIR="$HOME/docker28"
SOCK=/var/run/docker28.sock
if [ ! -x "$DIR/docker/dockerd" ]; then
  mkdir -p "$DIR"
  curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-$VER.tgz" -o "$DIR/docker.tgz"
  tar -xzf "$DIR/docker.tgz" -C "$DIR"
fi
if ! DOCKER_HOST=unix://$SOCK "$DIR/docker/docker" info >/dev/null 2>&1; then
  mkdir -p /var/lib/docker28 /var/run/docker28
  PATH="$DIR/docker:$PATH" nohup "$DIR/docker/dockerd" --host "unix://$SOCK" --data-root /var/lib/docker28 \
    --exec-root /var/run/docker28 --pidfile /var/run/docker28.pid --bip 172.31.0.1/24 \
    --containerd-namespace dw28 --containerd-plugins-namespace dw28p > "$HOME/.local/state/dogwatch/dockerd28.log" 2>&1 &
  for _ in $(seq 1 40); do DOCKER_HOST=unix://$SOCK "$DIR/docker/docker" info >/dev/null 2>&1 && break; sleep 1; done
fi
DOCKER_HOST=unix://$SOCK "$DIR/docker/docker" version --format 'engine {{.Server.Version}}'
