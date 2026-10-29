"""Draft the renewal packet with placeholders and post it to the Radio Officer for approval."""
import argparse
import json
from datetime import date

import httpx

from ..navigator import engine
from ..outbox.packet import build_packet
from ..watch import plan as planner


def main(argv=None):
    ap = argparse.ArgumentParser(prog="renewal-packet")
    ap.add_argument("profile")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--recipient", required=True)
    ap.add_argument("--radio", default="http://host.openshell.internal:8787")
    ap.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args(argv)
    prof = json.load(open(a.profile, encoding="utf-8"))
    res = engine.run_readiness(prof, {"start": a.start, "end": a.end}, date.fromisoformat(a.today))
    pk = build_packet(res, planner.write_plan(res), identifier_lines={}, recipient=a.recipient)
    r = httpx.post(f"{a.radio}/drafts", json=pk, timeout=30)
    print(json.dumps({"status": r.status_code, "body": r.json()}))


if __name__ == "__main__":
    main()
