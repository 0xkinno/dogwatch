"""P10: one daily and one weekly run triggered by the timer loop with nobody watching, timestamps in a trace file.
The daily run checks a stored offer through the Navigator; the weekly run calls the Lookout live (Tavily and Nemotron Nano)
for one administration to keep the credit cost small. Usage: python eval/run_unattended.py [route]"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "core")]

from dogwatch import envload  # noqa: E402

envload.load()
if len(sys.argv) > 1:
    os.environ["MODEL_ROUTE"] = sys.argv[1]
os.environ["DOGWATCH_RECEIPTS"] = str(ROOT / "evidence" / "receipts" / "p10-unattended.jsonl")
Path(os.environ["DOGWATCH_RECEIPTS"]).unlink(missing_ok=True)

from dogwatch.lookout import drift  # noqa: E402
from dogwatch.lookout.tavily import Tavily  # noqa: E402
from dogwatch.model.routes import selected_route  # noqa: E402
from dogwatch.persona import ARJUN  # noqa: E402
from dogwatch.watch import runner  # noqa: E402
from dogwatch.watch.loop import Watch  # noqa: E402
from dogwatch.watch.state import State  # noqa: E402


class Log:
    def __init__(self):
        self.lines = []

    def tell(self, text, kind):
        self.lines.append({"ts": time.time(), "kind": kind, "text": text})

    def post_draft(self, draft):
        pass


def iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    r = selected_route()
    st = State(Path(tempfile.mkdtemp()) / "unattended.db")
    log = Log()
    w = Watch(st, log, lambda: ARJUN, recipient="agent@example.test", identifier_lines={})
    w.remember_offer((date(2027, 2, 1), date(2027, 7, 31)))
    tav = Tavily()
    lookout = lambda: drift.run(tav, st, admins=["au-amsa"]).items
    trace = []
    for i in range(4):  # the service loop wakes every 6 seconds; due checks run, others do not
        ran = runner.tick(w, lookout=lookout)
        trace.append({"wake": i + 1, "ts": iso(time.time()), "ran": ran})
        time.sleep(6)
    runs = st.runs()
    out = {
        "set": "P10_unattended", "route": r.name, "route_label": f"Route: {r.label}", "timer": "service loop, wake every 6 seconds (runner.tick)",
        "wakes": trace, "runs": [{"kind": x["kind"], "started": iso(x["started"]), "finished": iso(x["finished"]) if x["finished"] else None,
                                   "summary": x["summary"] if x["kind"] == "daily" else {"review_items": len(x["summary"]["review_items"]), "lookout_ran": x["summary"]["lookout_ran"]}} for x in runs],
        "alerts": [{"ts": iso(a["ts"]), "kind": a["kind"], "text": a["text"]} for a in log.lines],
        "tavily_requests": len(tav.log),
        "daily_runs": sum(x["kind"] == "daily" for x in runs), "weekly_runs": sum(x["kind"] == "weekly" for x in runs),
    }
    d = ROOT / "evidence" / "unattended"
    d.mkdir(parents=True, exist_ok=True)
    (d / "trace.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p10_unattended.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print({k: out[k] for k in ("daily_runs", "weekly_runs", "tavily_requests")}, [w["ran"] for w in trace], out["alerts"][:1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
