#!/usr/bin/env python3
"""The full Arjun flow, live: Telegram offer, NOT_READY reply with rule and day count, discharge-book photo and ledger update,
approval prompt with the digest, approval, email through Resend with the packet PDF, and the .ics sent to Telegram.
Then P11 on the live transport. Evidence is redacted (message ids and the Resend id, recipient redacted).

Honesty rules: if the owner has not sent a real offer, a synthetic offer is used and labelled; if the owner does not tap Approve
within the wait, the driver approves and says so. Usage: python scripts/run_live_flow.py [--wait 60]"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "core"), str(ROOT / "radio")]

from dogwatch import envload  # noqa: E402

envload.load()
os.environ.setdefault("MODEL_ROUTE", "nvidia_build")
os.environ["DOGWATCH_RECEIPTS"] = str(ROOT / "evidence" / "receipts" / "live-flow.jsonl")

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from dogwatch.bosun import ledger  # noqa: E402
from dogwatch.navigator.seaservice import total_under  # noqa: E402
from dogwatch.navigator.dates import Entry  # noqa: E402
from dogwatch.persona import ARJUN, DEMO_TODAY  # noqa: E402
from dogwatch.vault.placeholders import Registry  # noqa: E402
from dogwatch.watch.loop import Watch, parse_offer_window  # noqa: E402
from dogwatch.watch.state import State  # noqa: E402
from radio import sender  # noqa: E402
from radio.ics import booking_ics  # noqa: E402
from radio.mail import Mailer, redact  # noqa: E402
from radio.rehydrate import build_pdf  # noqa: E402
from radio.telegram import Telegram  # noqa: E402

TODAY = date.fromisoformat(DEMO_TODAY)
OFFER = "New contract for you. Joining 1 Feb to 31 Jul 2027 on the same product tanker. Can you make it?"


def ocr_wsl(png: Path) -> str:
    wsl = "/mnt/" + png.drive[0].lower() + png.as_posix()[2:]
    r = subprocess.run(["wsl", "-d", "Ubuntu-24.04", "--", "tesseract", wsl, "stdout", "--psm", "6"], capture_output=True, text=True, timeout=120)
    return r.stdout


def step(s):
    print(time.strftime('%H:%M:%S'), s, flush=True)


def main() -> int:
    wait = int(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 60
    chat = int(os.environ["TELEGRAM_CHAT_ID"])
    agent = os.environ["TEST_AGENT_EMAIL"]
    tg = Telegram(os.environ["TELEGRAM_BOT_TOKEN"])
    mailer = Mailer()
    ev: dict = {"set": "Live_flow", "host": "build machine (Windows 10, WSL2)", "route": "nvidia_build", "route_label": "Route: NVIDIA API Catalog (development)",
                "mailer": "Resend", "telegram_message_ids": {}, "notes": []}
    tmp = Path(tempfile.mkdtemp())
    st = State(tmp / "live.db")
    reg = Registry()
    lines = {"Seafarer": reg.assign("NAME", "SPECIMEN SEAFARER"), "CoC number": reg.assign("COC", "123456/MUM/2019")}
    sent = []

    class Notes:
        def tell(self, text, kind):
            m = tg.send_message(chat, text)
            sent.append((kind, m["message_id"]))

        def post_draft(self, draft):
            pass

    profile = {"documents": ARJUN["documents"], "ledger": list(ARJUN["ledger"])}
    w = Watch(st, Notes(), lambda: profile, recipient=agent, identifier_lines=lines)

    step('1 offer')
    # 1. the offer: a real inbound message if the owner sent one, otherwise a labelled synthetic one
    offer, inbound = OFFER, False
    try:
        for u in reversed(tg.get_updates(timeout=0)):
            m = u.get("message") or {}
            if m.get("chat", {}).get("id") == chat and m.get("text") and parse_offer_window(m["text"], TODAY):
                offer, inbound = m["text"], True
                break
    except Exception as e:
        ev["notes"].append(f"getUpdates failed: {type(e).__name__}")
    ev["offer_source"] = "real inbound message from the owner" if inbound else "synthetic offer injected by the test driver (not sent by the owner)"
    step('1b on_message (live Nano and Ultra)')
    out = w.on_message(offer, today=TODAY)
    ev["triage"] = out["triage"]
    ev["reply_text"] = out["reply"]
    ev["navigator_overall"] = out["result"]["overall"]
    ev["plan_source"] = out["plan"]["source"]
    draft_id, digest = out["draft_id"], out["digest"]
    m = tg.send_message(chat, f"Offer received: {offer}", None)
    ev["telegram_message_ids"]["offer_echo"] = m["message_id"]

    step('2 photo')
    # 2. discharge-book photo and ledger update
    png = tmp / "discharge_book_specimen.png"
    im = Image.new("L", (1000, 520), 245)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
    for i, l in enumerate(["SPECIMEN DISCHARGE BOOK", "Vessel: MT Specimen Three", "Capacity: Second Officer", "Ship type: Oil tanker", "Signed on: 02/08/2026", "Signed off: 22/10/2026"]):
        d.text((50, 40 + i * 70), l, fill=20, font=f)
    im.save(png)
    ph = tg.send_photo(chat, png.name, png.read_bytes(), "SPECIMEN discharge-book page (test photo)")
    ev["telegram_message_ids"]["photo"] = ph["message_id"]
    step('2b ocr+ledger')
    res = ledger.read_entry(ocr_wsl(png), registry=reg, administration_hint="india")
    if res.entry:
        profile["ledger"].append({"sign_on": res.entry.sign_on.isoformat(), "sign_off": res.entry.sign_off.isoformat(), "vessel": res.entry.vessel,
                                  "flag": "", "capacity": res.entry.capacity, "ship_type": res.entry.ship_type})
        es = [Entry(date.fromisoformat(x["sign_on"]), date.fromisoformat(x["sign_off"])) for x in profile["ledger"]]
        days, _ = total_under(es, date(TODAY.year - 5, TODAY.month, TODAY.day), TODAY, "days_inclusive")
        msg = tg.send_message(chat, f"Ledger updated from the photo: {res.entry.vessel}, {res.entry.sign_on} to {res.entry.sign_off}. Sea service in the last five years: {int(days)} days (days, both endpoints counted).")
        ev["telegram_message_ids"]["ledger_reply"] = msg["message_id"]
        ev["ledger"] = {"entry_read": True, "ledger_entries_now": len(profile["ledger"]), "days_five_years_inclusive": int(days)}
    else:
        ev["ledger"] = {"entry_read": False, "unread_fields": res.unread_fields}

    step('3 approval prompt')
    # 3. the approval prompt with the digest, then approval
    prompt = tg.send_message(chat, f"{out['reply']}\nDigest {digest[:8]}", [("Approve", f"approve:{draft_id}"), ("Reject", f"reject:{draft_id}")])
    ev["telegram_message_ids"]["approval_prompt"] = prompt["message_id"]
    approved_by_owner, deadline, offset = False, time.time() + wait, None
    while time.time() < deadline:
        for u in tg.get_updates(offset, timeout=5):
            offset = u["update_id"] + 1
            cb = u.get("callback_query")
            if cb and cb["data"] == f"approve:{draft_id}" and cb["message"]["chat"]["id"] == chat:
                tg.answer_callback(cb["id"], "Approved")
                approved_by_owner = True
        if approved_by_owner:
            break
    ev["approval"] = "tapped by the owner on Telegram" if approved_by_owner else f"executed by the test driver after waiting {wait} s (the owner did not tap Approve)"
    secret = (os.environ.get("DOGWATCH_VAULT_PASSPHRASE") or "live-flow-dev-secret").encode().ljust(32, b"0")[:32]
    token = sender.approve(st, secret, draft_id)

    step('4 resend')
    # 4. send through Resend with the PDF, then the .ics to Telegram
    res_send = sender.send_approved(st, secret, draft_id, token, reg, mailer, {agent}, ROOT / "evidence" / "actions")
    ev["email"] = {"sent": res_send.get("sent"), "mode": res_send.get("mode"), "resend_message_id": res_send.get("id"), "recipient": redact(agent), "attachment": "readiness.pdf"}
    ics = booking_ics("Book medical fitness renewal", date(2026, 11, 2), date(2026, 12, 15), "Before joining on 1 Feb 2027. Medical lapses 14 Mar 2027.")
    doc = tg.send_document(chat, "medical-booking-window.ics", ics, "Booking window")
    ev["telegram_message_ids"]["ics_document"] = doc["message_id"]
    tg.send_message(chat, f"Sent to your agent ({res_send.get('mode')}). Calendar file attached above.")
    ev["notified_by_notifier"] = sent

    step('5 p11')
    # 5. P11 on the live transport: approve, kill (close state), restart, send, second send suppressed
    pk = st.draft(draft_id)
    d2 = "p11-live"
    st.add_draft(d2, pk["digest"], pk["payload"], "idem-p11-live")
    token2 = sender.approve(st, secret, d2)
    tg.send_message(chat, "P11: approved, now killing the loop before the send.")
    st.close()
    st2 = State(tmp / "live.db")
    pending = [x["id"] for x in st2.pending_drafts()]
    r1 = sender.send_approved(st2, secret, d2, token2, reg, mailer, {agent}, ROOT / "evidence" / "actions")
    r2 = sender.send_approved(st2, secret, d2, token2, reg, mailer, {agent}, ROOT / "evidence" / "actions")
    m11 = tg.send_message(chat, f"P11 restart: resumed {d2 in pending}, first send {r1.get('mode')}, second attempt {r2.get('mode')}.")
    ev["p11_live"] = {"transport": "live Telegram and live Resend", "approval_resumed_after_restart": d2 in pending, "first_send": r1.get("mode"), "first_resend_id": r1.get("id"),
                      "second_attempt": r2.get("mode"), "emails_sent": int(bool(r1.get("sent"))), "duplicate_sends": int(bool(r2.get("sent"))), "telegram_message_id": m11["message_id"]}
    ev["ok"] = bool(res_send.get("sent")) and ev["p11_live"]["duplicate_sends"] == 0
    d = ROOT / "evidence" / "actions"
    d.mkdir(parents=True, exist_ok=True)
    (d / "live-flow.json").write_text(json.dumps(ev, indent=1), encoding="utf-8", newline="\n")
    (ROOT / "eval" / "results").mkdir(exist_ok=True)
    (ROOT / "eval" / "results" / "live_flow.json").write_text(json.dumps(ev, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: ev[k] for k in ("offer_source", "navigator_overall", "approval", "email", "ledger", "p11_live", "ok")}, indent=1))
    return 0 if ev["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
