"""P8: read the 40 specimens. OCR text comes from Tesseract (eval/specimens/*.txt, made by eval/ocr_specimens.sh), the
Bosun replaces identifiers, Nemotron structures the placeholder text, code verifies quotes and parses dates.
Every outgoing request body is scanned for the synthetic identifiers. Usage: python eval/run_reading.py [route]"""
from __future__ import annotations

import json
import os
import re
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

import httpx  # noqa: E402
from openai import OpenAI  # noqa: E402
from dogwatch.bosun import read as bosun  # noqa: E402
from dogwatch.model import client, receipts  # noqa: E402
from dogwatch.model.routes import api_key, selected_route  # noqa: E402
from dogwatch.vault.identifiers import DEFAULT_DETECTORS, known_values_detector  # noqa: E402
from dogwatch.vault.placeholders import Registry  # noqa: E402

BODIES: list[tuple[str, str]] = []


def hook(request: httpx.Request):
    BODIES.append((request.url.host, request.content.decode("utf-8", errors="replace")))


def main() -> int:
    r = selected_route()
    truth = json.loads((HERE / "specimens" / "truth.json").read_text(encoding="utf-8"))
    os.environ["DOGWATCH_RECEIPTS"] = str(ROOT / "evidence" / "receipts" / f"p8-{r.name}.jsonl")
    Path(os.environ["DOGWATCH_RECEIPTS"]).unlink(missing_ok=True)
    client.set_client(OpenAI(base_url=r.base_url, api_key=api_key(r), timeout=120,
                             http_client=httpx.Client(event_hooks={"request": [hook]}, timeout=120)))

    def one(t):
        txt = (HERE / "specimens" / f"{t['id']}.txt").read_text(encoding="utf-8", errors="replace")
        reg = Registry()
        dets = list(DEFAULT_DETECTORS) + [known_values_detector([("NAME", t["identifiers"]["NAME"])])]
        res = None
        for wait in (0, 5, 15):
            time.sleep(wait)
            try:
                res = bosun.read_text(txt, registry=reg, doc_id=t["id"], administration_hint=t["administration_hint"], detectors=dets)
                break
            except (client.ModelUnavailable, client.ModelOutputInvalid) as e:
                res = type(e).__name__
        if isinstance(res, str) or res is None:
            return {"id": t["id"], "style": t["style"], "variant": t["variant"], "error": str(res), "exact": False, "unread": True}
        got = res.document.expiry.isoformat() if res.document.expiry else None
        return {"id": t["id"], "style": t["style"], "variant": t["variant"], "expected": t["expiry"], "got": got, "exact": got == t["expiry"],
                "unread": res.document.unread, "unread_fields": res.unread_fields, "quotes_refused": res.quotes_refused,
                "identifiers_replaced": res.identifiers_replaced}

    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(one, truth))

    secrets = [v for t in truth for v in t["identifiers"].values()]
    leaks = []
    for host, body in BODIES:
        low = body.casefold()
        squeezed = re.sub(r"[\s\-./_]", "", low)
        for s in secrets:
            if s.casefold() in low:
                leaks.append({"host": host, "kind": "literal"})
            elif re.sub(r"[\s\-./_]", "", s.casefold()) in squeezed:
                leaks.append({"host": host, "kind": "separator_variant"})
    wrong = [x for x in rows if not x["exact"] and not x["unread"]]
    out = {
        "set": "P8_reading", "detectors": "v2 (OCR-tolerant, after the v1 run found 12 identifier leaks in request bodies)", "route": r.name, "route_label": f"Route: {r.label}", "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "specimens": len(rows), "exact": sum(x["exact"] for x in rows), "unread": sum(x["unread"] for x in rows),
        "wrong_but_confident": len(wrong), "quotes_refused": sum(x.get("quotes_refused", 0) for x in rows),
        "request_bodies_scanned": len(BODIES), "identifier_leaks_in_request_bodies": len(leaks),
        "by_variant": {v: {"n": sum(x["variant"] == v for x in rows), "exact": sum(x["exact"] and x["variant"] == v for x in rows)} for v in sorted({x["variant"] for x in rows})},
        "miss_ids": [x["id"] for x in rows if not x["exact"]], "cases": rows,
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p8_reading.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print({k: v for k, v in out.items() if k not in ("cases", "by_variant")})
    print(out["by_variant"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
