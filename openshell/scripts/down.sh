#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
openshell sandbox delete dogwatch || true
[ -f .seal.pid ] && kill "$(cat .seal.pid)" 2>/dev/null || true
rm -f .seal.pid
