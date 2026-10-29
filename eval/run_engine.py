"""P6 (engine side): the Navigator against the pre-registered oracle verdicts. Misses stay in the denominator."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "core"))

from dogwatch.navigator import engine  # noqa: E402


def main():
    profiles = json.loads((HERE / "cases" / "profiles.json").read_text(encoding="utf-8"))
    rows = []
    for p in profiles:
        res = engine.run_readiness({"documents": p["documents"]}, p["contract"], date(2026, 10, 28))
        got = res["overall"]
        rows.append({"id": p["id"], "category": p["category"], "expected": p["expected"], "got": got, "ok": got == p["expected"]})
    miss = [r for r in rows if not r["ok"]]
    out = {
        "set": "P6_engine", "profiles": len(rows), "correct": len(rows) - len(miss),
        "false_safe": sum(r["got"] == "READY" and r["expected"] != "READY" for r in rows),
        "false_alarm": sum(r["got"] != "READY" and r["expected"] == "READY" for r in rows),
        "wrong_other": sum(not r["ok"] and not (r["got"] == "READY" and r["expected"] != "READY")
                           and not (r["got"] != "READY" and r["expected"] == "READY") for r in rows),
        "miss_ids": [r["id"] for r in miss], "cases": rows,
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p6_engine.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print({k: out[k] for k in ("profiles", "correct", "false_safe", "false_alarm", "wrong_other", "miss_ids")})


if __name__ == "__main__":
    main()
