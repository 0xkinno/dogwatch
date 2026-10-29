#!/usr/bin/env python3
"""Write web/data/recorded.json: what the pages show when the API host is unreachable, labelled RECORDED.

Everything here is computed from the committed code and result files, not typed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "core"), str(ROOT / "scripts")]

import facts  # noqa: E402
from dogwatch.navigator import engine  # noqa: E402
from dogwatch.navigator.rulepack import load_all  # noqa: E402
from dogwatch.persona import ARJUN, CONTRACT_OFFER, DEMO_TODAY  # noqa: E402


def sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def res(name):
    p = ROOT / "eval" / "results" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def extras(readiness):
    from dogwatch.model.routing import ROLES, route
    from dogwatch.model import receipts as rc
    from dogwatch.navigator.dates import Entry
    from dogwatch.navigator.seaservice import CONVENTIONS, total_under
    from dogwatch.outbox.packet import build_packet
    from dogwatch.watch import plan as planner
    today = date.fromisoformat(DEMO_TODAY)
    ws = date(today.year - 5, today.month, today.day)
    es = [Entry(date.fromisoformat(e["sign_on"]), date.fromisoformat(e["sign_off"])) for e in ARJUN["ledger"]]
    totals = {c: dict(zip(("total", "unit"), (round(v, 2), u))) for c in CONVENTIONS for v, u in [total_under(es, ws, today, c)]}
    plan = planner.write_plan(readiness, writer=lambda s, u: (_ for _ in ()).throw(__import__("dogwatch.model.client", fromlist=["x"]).ModelUnavailable("recorded export")))
    pk = build_packet(readiness, plan, identifier_lines={"Seafarer": "[[NAME_1]]", "CoC number": "[[COC_1]]", "Passport": "[[PASSPORT_1]]"}, recipient="manning-agent@example.test")
    routes = [{"role": r, "size": route(r).size, "model": route(r).model, "thinking": route(r).thinking, "max_tokens": route(r).max_tokens, "confirmed": route(r).confirmed} for r in ROLES]
    import glob, collections
    rs = []
    for f in glob.glob(str(ROOT / "evidence" / "receipts" / "*.jsonl")):
        rs += [json.loads(x) for x in open(f, encoding="utf-8").read().splitlines() if x.strip()]
    by = collections.defaultdict(lambda: {"calls": 0, "tokens_in": 0, "tokens_out": 0})
    for r in rs:
        k = f"{r.get('route','?')}|{r['model']}"
        by[k]["calls"] += 1; by[k]["tokens_in"] += r["tokens_in"]; by[k]["tokens_out"] += r["tokens_out"]
    return {
        "ledger": ARJUN["ledger"], "ledger_window": [ws.isoformat(), today.isoformat()], "ledger_totals": totals,
        "routing": routes, "receipts": {"count": len(rs), "by_model": dict(by), "note": "No Token Factory call has been recorded; every receipt below is from the NVIDIA API Catalog development route."},
        "outbox": {"packet": pk["packet"], "recipients": pk["recipients"], "digest": pk["digest"], "status": "PENDING", "plan_source": plan["source"], "sent": []},
    }


def main():
    readiness = engine.run_readiness(ARJUN, CONTRACT_OFFER, date.fromisoformat(DEMO_TODAY))
    p3, p3v1, p6, p7, p11 = (res(n) for n in ("p3_seal_corpus.json", "p3_seal_corpus_v1.json", "p6_engine.json", "p7_conventions.json", "p11_restart.json"))
    def slim(p):
        return {k: v for k, v in p.items() if k != "cases"} if p else None
    sources = json.loads((ROOT / "evidence" / "need" / "sources.json").read_text(encoding="utf-8"))["sources"]
    out = {
        "mode": "RECORDED",
        "run_id": f"build-{sha()}",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "persona": {"name": ARJUN["name"], "role": ARJUN["role"], "today": DEMO_TODAY, "contract": CONTRACT_OFFER},
        "readiness": readiness,
        "facts": facts.build()["facts"],
        "probe": json.loads((ROOT / "evidence" / "probe" / "nvidia_build.json").read_text(encoding="utf-8")) if (ROOT / "evidence" / "probe" / "nvidia_build.json").exists() else None,
        "live": {n: slim(res(f)) for n, f in (("p6_model", "p6_model_alone.json"), ("p8", "p8_reading.json"), ("p8_v1", "p8_reading_v1.json"), ("p9", "p9_drift.json"), ("p10", "p10_unattended.json"), ("p12", "p12_cost.json"))},
        "p6_model_cases": {k: v["cases"] for k, v in (res("p6_model_alone.json") or {"contestants": {}})["contestants"].items()},
        "p8_cases": (res("p8_reading.json") or {}).get("cases"),
        "proof": {"p3": slim(p3), "p3_v1": slim(p3v1), "p6": slim(p6), "p7": slim(p7), "p11": slim(p11),
                  "p3_cases": ((p3 or {}).get("cases") or {}).get("attacks"), "p6_cases": (p6 or {}).get("cases"), "p7_cases": (p7 or {}).get("cases")},
        **extras(readiness),
        "sources": sources,
        "packs": {k: {"rules": len(p.rules), "status": p.status, "sha256": p.sha256, "administration": p.administration,
                      "rule_list": [r.to_ref(p.sha256) for r in p.rules]} for k, p in load_all().items()},
        "policy": (ROOT / "openshell" / "policy" / "dogwatch.yaml").read_text(encoding="utf-8"),
        "prover": {f.name: f.read_text(encoding="utf-8")[:4000] for f in sorted((ROOT / "evidence" / "prover").glob("*.txt"))},
        "boundary_runs": {f.name: f.read_text(encoding="utf-8")[:4000] for f in sorted((ROOT / "evidence" / "boundary").glob("*")) if f.is_file() and f.name != ".gitkeep"},
    }
    dest = ROOT / "web" / "data" / "recorded.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print("wrote", dest.relative_to(ROOT), dest.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
