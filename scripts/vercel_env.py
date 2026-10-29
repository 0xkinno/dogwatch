#!/usr/bin/env python3
"""Push environment variables to a Vercel project's production environment without printing any value.
Usage: python scripts/vercel_env.py <project_dir> NAME [NAME=literal ...]
A bare NAME is read from the repository .env; NAME=value uses the literal."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def dotenv() -> dict[str, str]:
    out = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k] = v.strip().strip('"').strip("'")
    return out


def main() -> int:
    proj = Path(sys.argv[1])
    env = dotenv()
    rc = 0
    for spec in sys.argv[2:]:
        name, _, lit = spec.partition("=")
        val = lit if "=" in spec else env.get(name, "")
        if not val:
            print(f"skip {name}: empty")
            continue
        subprocess.run(["npx", "vercel", "env", "rm", name, "production", "--yes"], cwd=proj, capture_output=True, shell=True)
        r = subprocess.run(["npx", "vercel", "env", "add", name, "production"], cwd=proj, input=val, text=True, capture_output=True, shell=True)
        print(f"{name}: {'added' if r.returncode == 0 else 'FAILED ' + r.stderr[-120:].replace(val, '<value>')}")
        rc |= r.returncode
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
