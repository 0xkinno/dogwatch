"""P6: Nemotron alone against the pre-registered oracle verdicts, on the same 60 profiles the Navigator was run on.

The model is given the rule text and the profile and must return the overall verdict. Misses stay in the denominator.
The route is recorded in the result and every receipt. Usage: python eval/run_model_alone.py [route]
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "core")]

from dogwatch import envload  # noqa: E402

envload.load()
if len(sys.argv) > 1:
    os.environ["MODEL_ROUTE"] = sys.argv[1]

from dogwatch.model import client, receipts  # noqa: E402
from dogwatch.model.routes import selected_route  # noqa: E402
from dogwatch.model.routing import route as route_for  # noqa: E402

RULES = """Rules (all dates are ISO, inclusive):
1. A document covers the contract when its expiry date is on or after the contract end date. Travel days after the contract extend the end date by that many days; travel days before extend the start.
2. A document whose expiry date is earlier than the extended end date lapses, and then the contract is NOT_READY.
3. A document with no readable expiry date (unread) is unknown. A required document type that is not in the list is unknown.
4. Overall verdict: NOT_READY if any document lapses. Otherwise CANNOT_VERIFY if anything is unknown. Otherwise READY.
Reply with JSON only: {"overall": "READY" | "NOT_READY" | "CANNOT_VERIFY"}"""


def ask(c, model: str, p: dict) -> tuple[str, dict]:
    prof = {"documents": [{k: d[k] for k in ("doc_type", "expiry", "unread")} for d in p["documents"]], "contract": p["contract"]}
    t = time.time()
    last = ""
    for wait in (0, 4, 10, 20):
        if wait:
            time.sleep(wait)
        try:
            r = c.chat.completions.create(model=model, temperature=0, max_tokens=60,
                                          messages=[{"role": "system", "content": RULES}, {"role": "user", "content": json.dumps(prof)}],
                                          extra_body={"chat_template_kwargs": {"enable_thinking": False}})
            txt = r.choices[0].message.content or ""
            try:
                v = json.loads(client.extract_json(txt)).get("overall", "UNPARSED")
            except Exception:
                v = "UNPARSED"
            receipts.record(r, model=model, role="p6", attempt=1, started=t, route=selected_route().name)
            return v, {"tokens_in": r.usage.prompt_tokens, "tokens_out": r.usage.completion_tokens}
        except Exception as e:
            last = type(e).__name__ + (f" HTTP {e.status_code}" if hasattr(e, "status_code") else "")
            if getattr(e, "status_code", 0) not in (429, 503):
                break
    return "ERROR", {"error": last}


def main() -> int:
    r = selected_route()
    profiles = json.loads((HERE / "cases" / "profiles.json").read_text(encoding="utf-8"))
    os.environ["DOGWATCH_RECEIPTS"] = str(ROOT / "evidence" / "receipts" / f"p6-{r.name}.jsonl")
    Path(os.environ["DOGWATCH_RECEIPTS"]).unlink(missing_ok=True)
    c = client.get_client()
    contestants = {"super": route_for("structure", r.name).model, "ultra": route_for("plan", r.name).model}
    out = {"set": "P6_engine_vs_model", "status": "RUN", "route": r.name, "route_label": f"Route: {r.label}",
           "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "profiles": len(profiles), "thinking": "off", "contestants": {}}
    for name, model in contestants.items():
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(lambda p: ask(c, model, p), profiles))
        rows = []
        for p, (v, meta) in zip(profiles, res):
            rows.append({"id": p["id"], "category": p["category"], "expected": p["expected"], "got": v, "ok": v == p["expected"], **meta})
        miss = [x for x in rows if not x["ok"]]
        out["contestants"][name] = {
            "model": model, "correct": len(rows) - len(miss),
            "false_safe": sum(x["got"] == "READY" and x["expected"] != "READY" for x in rows),
            "false_alarm": sum(x["got"] not in ("READY", "ERROR") and x["expected"] == "READY" for x in rows),
            "errors": sum(x["got"] == "ERROR" for x in rows), "unparsed": sum(x["got"] == "UNPARSED" for x in rows),
            "miss_ids": [x["id"] for x in miss], "tokens_in": sum(x.get("tokens_in", 0) for x in rows),
            "tokens_out": sum(x.get("tokens_out", 0) for x in rows), "cases": rows,
        }
        print(name, model, {k: v for k, v in out["contestants"][name].items() if k not in ("cases", "miss_ids")})
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p6_model_alone.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
