"""Minimal .env loader. Never overrides a variable already set, never prints a value."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path | None = None) -> list[str]:
    """Returns the names that were set from the file (names only)."""
    p = path or ROOT / ".env"
    if not p.exists():
        return []
    done = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        if v and k not in os.environ:
            os.environ[k] = v
            done.append(k)
    return done
