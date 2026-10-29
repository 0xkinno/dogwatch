"""READY, NOT_READY or CANNOT_VERIFY for a contract window. No model."""
import argparse
import json
from datetime import date

from ..navigator import engine


def main(argv=None):
    ap = argparse.ArgumentParser(prog="contract-readiness")
    ap.add_argument("profile")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--travel-before", type=int, default=0)
    ap.add_argument("--travel-after", type=int, default=0)
    ap.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args(argv)
    prof = json.load(open(a.profile, encoding="utf-8"))
    contract = {"start": a.start, "end": a.end, "travel_before": a.travel_before, "travel_after": a.travel_after}
    res = engine.run_readiness(prof, contract, date.fromisoformat(a.today))
    print(json.dumps({"overall": res["overall"], "summary": res["summary"]}, indent=2))


if __name__ == "__main__":
    main()
