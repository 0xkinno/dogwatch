"""P7: how many sea-service verdicts flip between counting conventions, per rule. Also checks the day totals."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "core"))

from dogwatch.navigator.dates import Entry  # noqa: E402
from dogwatch.navigator.rulepack import load_all  # noqa: E402
from dogwatch.navigator.seaservice import check_requirement  # noqa: E402


def main():
    packs = load_all()
    rules = {r.id: r for p in packs.values() for r in p.rules}
    case_file = sys.argv[1] if len(sys.argv) > 1 else "conventions.json"
    result_name = sys.argv[2] if len(sys.argv) > 2 else "p7_conventions.json"
    cases = json.loads((HERE / "cases" / case_file).read_text(encoding="utf-8"))
    rows, per_rule = [], {}
    arithmetic_errors = []
    for c in cases:
        r = rules[c["rule"]]
        es = [Entry(date.fromisoformat(e["sign_on"]), date.fromisoformat(e["sign_off"])) for e in c["entries"]]
        chk = check_requirement(es, r.params, date.fromisoformat(c["apply_date"]))
        meets = {x.convention: x.meets for x in chk.results}
        flip = len(set(meets.values())) > 1
        if c["inclusive_days"] is not None:
            got = next(x.total for x in chk.results if x.convention == "days_inclusive")
            if int(got) != c["inclusive_days"]:
                arithmetic_errors.append(c["id"])
        rows.append({"id": c["id"], "rule": c["rule"], "flip": flip, "meets": meets, "verdict": chk.verdict})
        s = per_rule.setdefault(c["rule"], {"histories": 0, "flips": 0, "states_convention": r.params.get("convention", "unstated")})
        s["histories"] += 1
        s["flips"] += int(flip)
    out = {"set": "P7_counting_conventions", "histories": len(rows), "flips": sum(r["flip"] for r in rows), "per_rule": per_rule,
           "day_total_errors": arithmetic_errors, "rules_stating_a_convention": [i for i, r in rules.items() if r.params.get("convention", "unstated") != "unstated"],
           "rules_checked": sorted(per_rule), "cases": rows}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / result_name).write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print({k: out[k] for k in ("histories", "flips", "per_rule", "day_total_errors", "rules_stating_a_convention")})


if __name__ == "__main__":
    main()
