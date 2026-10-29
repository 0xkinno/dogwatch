#!/usr/bin/env python3
"""CI gate: docs/FACTS.json must match the result files, and README and UI numbers must match FACTS.

A number in prose is wrapped as <!--fact:KEY-->value<!--/fact--> (README) or data-fact="KEY" (web). Both are checked.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import facts  # noqa: E402

ROOT = facts.ROOT


def fmt(v) -> str:
    return f"{v:,}" if isinstance(v, int) and abs(v) >= 10000 else str(v)


def main() -> int:
    problems = []
    current = facts.build()["facts"]
    stored = json.loads(facts.OUT.read_text(encoding="utf-8"))["facts"] if facts.OUT.exists() else {}
    if stored != current:
        problems.append("docs/FACTS.json is stale: run python scripts/facts.py")
    marker = re.compile(r"<!--fact:([\w.\-]+)-->(.*?)<!--/fact-->")
    attr = re.compile(r"data-fact=\"([\w.\-]+)\"[^>]*>([^<]*)<")
    files = [ROOT / "README.md", ROOT / "JUDGE.md", ROOT / "PROOF.md", ROOT / "EVIDENCE.md"] + list((ROOT / "web").rglob("*.tsx")) \
        if (ROOT / "web").exists() else [ROOT / "README.md"]
    for f in files:
        if "node_modules" in f.parts or ".next" in f.parts or not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        for rx in (marker, attr):
            for key, shown in rx.findall(text):
                if key not in current:
                    problems.append(f"{f.relative_to(ROOT)}: unknown fact {key}")
                elif shown.strip() != fmt(current[key]["value"]) and shown.strip() != str(current[key]["value"]):
                    problems.append(f"{f.relative_to(ROOT)}: {key} shows {shown.strip()} but FACTS says {current[key]['value']}")
    if problems:
        print("check_facts FAILED")
        for p in problems:
            print("  " + p)
        return 1
    print(f"check_facts ok ({len(current)} facts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
