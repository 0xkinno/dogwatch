"""Add a discharge-book entry and recompute totals under every counting convention."""
import argparse
import json
from datetime import date

from ..navigator.dates import Entry
from ..navigator.seaservice import CONVENTIONS, total_under


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sea-service-ledger")
    ap.add_argument("ledger", help="ledger JSON path (list of entries)")
    ap.add_argument("--add", nargs=2, metavar=("SIGN_ON", "SIGN_OFF"))
    ap.add_argument("--window", nargs=2, metavar=("START", "END"), required=True)
    a = ap.parse_args(argv)
    led = json.load(open(a.ledger, encoding="utf-8"))
    if a.add:
        led.append({"sign_on": a.add[0], "sign_off": a.add[1]})
        json.dump(led, open(a.ledger, "w", encoding="utf-8"), indent=2)
    es = [Entry(date.fromisoformat(e["sign_on"]), date.fromisoformat(e["sign_off"])) for e in led]
    ws, we = (date.fromisoformat(x) for x in a.window)
    out = {c: dict(zip(("total", "unit"), total_under(es, ws, we, c))) for c in CONVENTIONS}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
