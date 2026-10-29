#!/usr/bin/env bash
# Regenerate the Python stubs from the proto files copied from NVIDIA/OpenShell (Apache-2.0).
set -euo pipefail
cd "$(dirname "$0")"
python -m grpc_tools.protoc -Iproto --python_out=seal/gen --grpc_python_out=seal/gen proto/supervisor_middleware.proto proto/extension.proto
