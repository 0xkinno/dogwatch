"""Navigator facade: JSON in, JSON out, no model anywhere on this path."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date

from .dates import Entry
from .readiness import Document, Window, readiness
from .rulepack import load_all


def _d(v):
    if v is None or isinstance(v, date):
        return v
    return date.fromisoformat(v)


def parse_profile(profile: dict) -> tuple[list[Document], list[Entry]]:
    docs = [
        Document(id=d["id"], doc_type=d["doc_type"], administration=d.get("administration", ""),
                 expiry=_d(d.get("expiry")), unread=bool(d.get("unread")), label=d.get("label", ""),
                 endorsement=d.get("endorsement", ""))
        for d in profile["documents"]
    ]
    ledger = [
        Entry(_d(e["sign_on"]), _d(e["sign_off"]), e.get("vessel", ""), e.get("flag", ""),
              e.get("capacity", ""), e.get("ship_type", ""))
        for e in profile.get("ledger", [])
    ]
    return docs, ledger


def run_readiness(profile: dict, contract: dict, today: date | None = None) -> dict:
    packs = load_all()
    docs, ledger = parse_profile(profile)
    win = Window(_d(contract["start"]), _d(contract["end"]), int(contract.get("travel_before", 0)),
                 int(contract.get("travel_after", 0)))
    res = readiness(docs, win, packs, today or date.today(), ledger, contract.get("required_types"))
    return asdict(res)
