#!/usr/bin/env python3
"""Assemble .deploy-api/: the judge door API as a Vercel Python function (a substitute host, labelled as such).
Copies only what the API reads. Contains no .env, no vault, no reference material."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".deploy-api"

OUT.mkdir(exist_ok=True)
for child in OUT.iterdir():  # clear everything except the Vercel project link
    if child.name in (".vercel", ".gitignore"):
        continue
    shutil.rmtree(child, ignore_errors=True) if child.is_dir() else child.unlink()
(OUT / "api").mkdir(parents=True, exist_ok=True)
ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "tests")
shutil.copytree(ROOT / "core" / "dogwatch", OUT / "core" / "dogwatch", ignore=ignore)
shutil.copytree(ROOT / "core" / "rulepacks", OUT / "core" / "rulepacks", ignore=ignore)
shutil.copytree(ROOT / "eval" / "results", OUT / "eval" / "results")
shutil.copytree(ROOT / "evidence" / "need", OUT / "evidence" / "need")
for sub in ("prover", "boundary", "probe"):
    if (ROOT / "evidence" / sub).exists():
        shutil.copytree(ROOT / "evidence" / sub, OUT / "evidence" / sub)
shutil.copytree(ROOT / "docs", OUT / "docs", ignore=shutil.ignore_patterns("img"))
(OUT / "openshell" / "policy").mkdir(parents=True)
shutil.copy(ROOT / "openshell" / "policy" / "dogwatch.yaml", OUT / "openshell" / "policy" / "dogwatch.yaml")
(OUT / "scripts").mkdir()
shutil.copy(ROOT / "scripts" / "facts.py", OUT / "scripts" / "facts.py")
(OUT / "eval" / "cases").mkdir(parents=True, exist_ok=True)
shutil.copy(ROOT / "eval" / "cases" / "prereg.json", OUT / "eval" / "cases" / "prereg.json")
shutil.copy(ROOT / "scripts" / "api_entry.py", OUT / "api" / "index.py")
(OUT / "requirements.txt").write_text("fastapi\npydantic\npyyaml\npython-dateutil\nhttpx\nopenai\n", encoding="utf-8")
(OUT / "vercel.json").write_text(json.dumps({
    "functions": {"api/index.py": {"includeFiles": "{core,eval,evidence,docs,openshell,scripts}/**", "maxDuration": 60}},
    "rewrites": [{"source": "/api/:path*", "destination": "/api/index?__p=/api/:path*"}],
}, indent=1), encoding="utf-8")
total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
print(f"assembled {OUT.name}: {total / 1e6:.1f} MB")
