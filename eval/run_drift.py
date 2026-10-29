"""P9: the Lookout over the five administrations' domains with live Tavily and Nemotron Nano. Usage: python eval/run_drift.py [route]
Records review items, pages rejected by each gate, requests made, and every failure. No ground truth exists for "new rule text",
so this set reports behaviour and gates, not accuracy."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "core")]

from dogwatch import envload  # noqa: E402

envload.load()
if len(sys.argv) > 1:
    os.environ["MODEL_ROUTE"] = sys.argv[1]
os.environ["DOGWATCH_RECEIPTS"] = str(ROOT / "evidence" / "receipts" / "p9-drift.jsonl")
Path(os.environ["DOGWATCH_RECEIPTS"]).unlink(missing_ok=True)

from dogwatch.lookout import drift  # noqa: E402
from dogwatch.lookout.tavily import Tavily  # noqa: E402
from dogwatch.model.routes import selected_route  # noqa: E402
from dogwatch.watch.state import State  # noqa: E402


def main() -> int:
    r = selected_route()
    t = Tavily()
    st = State(Path(tempfile.mkdtemp()) / "drift.db")
    rep = drift.run(t, st)
    out = {
        "set": "P9_drift", "route": r.name, "route_label": f"Route: {r.label}", "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": rep.status, "detail": rep.detail, "review_items": len(rep.items), "items": rep.items,
        "gates": rep.gates.__dict__, "tavily_requests": len(t.log),
        "tavily_requests_by_path": {p: sum(x["path"] == p for x in t.log) for p in ("/search", "/extract")},
        "queries": [x["body"].get("query") for x in t.log if x["path"] == "/search"],
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p9_drift.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print({k: v for k, v in out.items() if k not in ("items", "queries")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
