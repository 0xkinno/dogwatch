"""Validity and windows for every document in a profile JSON. No model."""
import argparse
import json
from datetime import date

from ..navigator import engine


def main(argv=None):
    ap = argparse.ArgumentParser(prog="expiry-navigator")
    ap.add_argument("profile", help="profile JSON path")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args(argv)
    prof = json.load(open(a.profile, encoding="utf-8"))
    res = engine.run_readiness(prof, {"start": a.start, "end": a.end}, date.fromisoformat(a.today))
    print(json.dumps({d["document_id"]: d["state"] for d in res["documents"]}, indent=2))


if __name__ == "__main__":
    main()
