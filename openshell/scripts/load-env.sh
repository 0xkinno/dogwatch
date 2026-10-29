#!/usr/bin/env bash
# Source this file: exports the variables in the repository .env without printing any value.
_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ -f "$_root/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  . <(tr -d '\r' < "$_root/.env" | grep -E '^[A-Za-z_][A-Za-z0-9_]*=' )
  set +a
fi
unset _root
