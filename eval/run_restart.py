"""P11: kill the loop with a pending approval, restart, approve, and confirm exactly one send.

The mail transport is a local capture, so this proves the state machine and idempotency, not a provider.
Labelled FIXTURE transport in the result.
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "core"), str(HERE.parent / "radio")]

from dogwatch.persona import ARJUN  # noqa: E402
from dogwatch.vault.placeholders import Registry  # noqa: E402
from dogwatch.watch.loop import Watch  # noqa: E402
from dogwatch.watch.state import State  # noqa: E402
from dogwatch.model import client  # noqa: E402
from radio import sender  # noqa: E402
from radio.mail import Mailer  # noqa: E402

TODAY = date(2026, 10, 28)
SECRET = b"p11" * 11
AGENT = "agent@example.test"


class Capture(httpx.BaseTransport):
    def __init__(self):
        self.sent = 0

    def handle_request(self, request):
        self.sent += 1
        return httpx.Response(200, json={"id": "fixture"})


class Quiet:
    def tell(self, text, kind):
        pass

    def post_draft(self, draft):
        pass


def down(system, user):
    raise client.ModelUnavailable("fixture")


def main():
    tmp = Path(tempfile.mkdtemp())
    reg = Registry()
    lines = {"Seafarer": reg.assign("NAME", "SPECIMEN NAME")}
    cap = Capture()
    mailer = Mailer("fixture-key", "dogwatch@example.test", transport=cap)
    steps = []
    st = State(tmp / "s.db")
    w = Watch(st, Quiet(), lambda: ARJUN, recipient=AGENT, identifier_lines=lines, writer=down, classifier=lambda t: type("T", (), {"label": "contract_offer"})())
    out = w.on_message("joining 1 Feb to 31 Jul", today=TODAY)
    draft_id = out["draft_id"]
    steps.append({"step": "draft created, status PENDING", "status": st.draft(draft_id)["status"]})
    token = sender.approve(st, SECRET, draft_id)
    steps.append({"step": "approved, then the process is killed before sending", "status": st.draft(draft_id)["status"]})
    st.close()  # the kill
    st2 = State(tmp / "s.db")
    pending = [d["id"] for d in Watch(st2, Quiet(), lambda: ARJUN, recipient=AGENT, identifier_lines=lines).resume()]
    steps.append({"step": "restart: pending approval resumed", "pending": pending})
    first = sender.send_approved(st2, SECRET, draft_id, token, reg, mailer, {AGENT}, tmp / "ev")
    second = sender.send_approved(st2, SECRET, draft_id, token, reg, mailer, {AGENT}, tmp / "ev")
    steps.append({"step": "send after restart", "result": first.get("mode"), "sent": first.get("sent")})
    steps.append({"step": "second send attempt", "result": second.get("mode")})
    result = {
        "set": "P11_restart", "transport": "FIXTURE (local capture, no provider)", "sends_observed": cap.sent,
        "duplicate_sends": max(0, cap.sent - 1), "approval_resumed": draft_id in pending, "steps": steps,
        "ok": cap.sent == 1 and draft_id in pending and second.get("mode") == "DUPLICATE_SUPPRESSED",
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p11_restart.json").write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    print(result["ok"], result["sends_observed"], result["duplicate_sends"])


if __name__ == "__main__":
    main()
