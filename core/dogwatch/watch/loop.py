"""Officer of the Watch: the always-on loop. Wakes on a message, a daily timer and a weekly timer."""
from __future__ import annotations

import hashlib
import re
from datetime import date, datetime
from typing import Protocol

from ..navigator import engine
from ..outbox.digest import short
from ..outbox.packet import build_packet
from . import plan as planner
from . import triage as triager
from .budget import Budget
from .state import State

_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
_RANGE = re.compile(
    r"(\d{1,2})\s*([A-Za-z]{3})[a-z]*\.?\s*(?:(\d{4})\s*)?(?:to|until|till|through|-)\s*(\d{1,2})\s*([A-Za-z]{3})[a-z]*\.?\s*(?:(\d{4}))?",
    re.I)
_ISO = re.compile(r"(\d{4}-\d{2}-\d{2})\s*(?:to|until|-|through)\s*(\d{4}-\d{2}-\d{2})")


class Notifier(Protocol):
    def tell(self, text: str, kind: str) -> None: ...
    def post_draft(self, draft: dict) -> None: ...


def parse_offer_window(text: str, today: date) -> tuple[date, date] | None:
    """Dates are read by code from the message. None means ask the seafarer."""
    m = _ISO.search(text)
    if m:
        return date.fromisoformat(m.group(1)), date.fromisoformat(m.group(2))
    m = _RANGE.search(text)
    if not m:
        return None
    d1, mon1, y1, d2, mon2, y2 = m.groups()
    if mon1.lower() not in _MONTHS or mon2.lower() not in _MONTHS:
        return None
    try:
        start_year = int(y1) if y1 else None
        if start_year is None:
            start_year = today.year
            if date(start_year, _MONTHS[mon1.lower()], int(d1)) < today:
                start_year += 1
        start = date(start_year, _MONTHS[mon1.lower()], int(d1))
        end_year = int(y2) if y2 else start.year
        end = date(end_year, _MONTHS[mon2.lower()], int(d2))
        if end < start and not y2:
            end = date(end_year + 1, _MONTHS[mon2.lower()], int(d2))
    except ValueError:
        return None
    return (start, end) if end >= start else None


class Watch:
    def __init__(self, state: State, notifier: Notifier, profile_provider, *, recipient: str,
                 identifier_lines: dict[str, str], writer=None, classifier=None):
        self.state, self.notifier, self.profile_provider = state, notifier, profile_provider
        self.recipient, self.identifier_lines = recipient, identifier_lines
        self.writer, self.classifier = writer, classifier
        self.budget = Budget(state)

    # message wake
    def on_message(self, text: str, *, today: date, has_photo: bool = False) -> dict:
        t = triager.triage(text, has_photo=has_photo, classify=self.classifier)
        label = t["label"]
        if label == "contract_offer":
            window = parse_offer_window(text, today)
            if window is None:
                return self._question("What are the start and end dates of the offered contract?", today, t)
            return self._check_offer(window, today, t)
        if label == "document_photo":
            return {"label": label, "triage": t, "reply": "Photo received. Reading it on this machine."}
        if label == "approval":
            return {"label": label, "triage": t, "reply": "Use the Approve button on the packet message; it is bound to the packet digest."}
        return {"label": label, "triage": t, "reply": "Noted."}

    def _question(self, text: str, today: date, t: dict) -> dict:
        if self.budget.allow("question", today):
            self.notifier.tell(text, "question")
            return {"label": "contract_offer", "triage": t, "reply": text, "asked": True}
        return {"label": "contract_offer", "triage": t, "reply": "", "asked": False, "deferred": text}

    def _check_offer(self, window: tuple[date, date], today: date, t: dict) -> dict:
        contract = {"start": window[0].isoformat(), "end": window[1].isoformat(), "travel_before": 0,
                    "travel_after": 0, "required_types": ["coc", "medical", "passport", "bst"]}
        result = engine.run_readiness(self.profile_provider(), contract, today)
        pl = planner.write_plan(result, writer=self.writer)
        pk = build_packet(result, pl, identifier_lines=self.identifier_lines, recipient=self.recipient)
        key = hashlib.sha256(pk["digest"].encode()).hexdigest()
        draft_id = f"d-{short(pk['digest'])}"
        created = self.state.add_draft(draft_id, pk["digest"], pk, key)
        lapse = any(d["state"] == "LAPSES_DURING" for d in result["documents"])
        if created:
            self.budget.allow("lapse" if lapse else "approval", today)
            self.notifier.post_draft(self.state.draft(draft_id))
        body = pl["text"] if pl["text"].startswith(("Not ready", "Ready", "Cannot verify")) else f"{result['summary']} {pl['text']}"
        reply = f"{body} Packet {short(pk['digest'])} ready: approve?"
        return {"label": "contract_offer", "triage": t, "result": result, "plan": pl, "draft_id": draft_id,
                "digest": pk["digest"], "reply": reply, "duplicate": not created}

    # timers
    def daily(self, today: date) -> dict:
        run = self.state.start_run("daily")
        offers = self.state.get("offers", [])
        notes = []
        for o in offers:
            res = engine.run_readiness(self.profile_provider(), o, today)
            notes.append({"contract": o["start"], "overall": res["overall"], "summary": res["summary"]})
            if res["overall"] == "NOT_READY" and self.budget.allow("lapse", today):
                self.notifier.tell(res["summary"], "lapse")
        summary = {"checked_offers": len(offers), "notes": notes}
        self.state.finish_run(run, summary)
        return summary

    def weekly(self, today: date, lookout=None) -> dict:
        run = self.state.start_run("weekly")
        items = lookout() if lookout else []
        summary = {"review_items": items, "lookout_ran": lookout is not None}
        self.state.finish_run(run, summary)
        return summary

    def remember_offer(self, window: tuple[date, date]) -> None:
        offers = self.state.get("offers", [])
        o = {"start": window[0].isoformat(), "end": window[1].isoformat(), "required_types": ["coc", "medical", "passport", "bst"]}
        if o not in offers:
            offers.append(o)
            self.state.put("offers", offers)

    def resume(self) -> list[dict]:
        """After a restart: pending approvals are still pending, nothing is sent twice."""
        return self.state.pending_drafts()
