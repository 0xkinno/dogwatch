"""Discharge-book page to a sea-service ledger entry. Same rule as the Bosun: the model quotes, code verifies and parses dates."""
from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from ..model import client
from ..navigator.dates import Entry
from ..vault.identifiers import DEFAULT_DETECTORS
from ..vault.placeholders import Registry, replace_identifiers
from .schema import QuotedField
from .verify_quote import parse_date_from_quote, quote_in_text


class LedgerExtraction(BaseModel):
    vessel: QuotedField = Field(default_factory=QuotedField)
    capacity: QuotedField = Field(default_factory=QuotedField)
    ship_type: QuotedField = Field(default_factory=QuotedField)
    sign_on: QuotedField = Field(default_factory=QuotedField)
    sign_off: QuotedField = Field(default_factory=QuotedField)


SYSTEM = (
    "You read one discharge-book entry whose identifiers have been replaced by placeholders. Return JSON only with keys "
    "vessel, capacity, ship_type, sign_on, sign_off. Each is an object with value and quote, and the quote is copied exactly "
    "from the text. If a field is absent, leave value and quote empty. Never guess a date."
)


@dataclass
class LedgerResult:
    entry: Entry | None
    unread_fields: list[str] = field(default_factory=list)
    quotes_refused: int = 0


def read_entry(raw_text: str, *, registry: Registry, administration_hint: str = "default", structure=None) -> LedgerResult:
    ph, _ = replace_identifiers(raw_text, DEFAULT_DETECTORS, registry)
    ex = (structure or (lambda t: client.structured("structure", SYSTEM, t, LedgerExtraction)))(ph)
    unread, refused = [], 0
    dates = {}
    for name in ("sign_on", "sign_off"):
        f: QuotedField = getattr(ex, name)
        if not quote_in_text(f.quote, ph):
            refused += bool(f.quote)
            unread.append(name)
            continue
        d = parse_date_from_quote(f.quote, administration_hint)
        if d is None:
            unread.append(name)
        dates[name] = d
    vessel = ex.vessel.value if quote_in_text(ex.vessel.quote, ph) else ""
    if not vessel:
        unread.append("vessel")
    if dates.get("sign_on") and dates.get("sign_off") and dates["sign_off"] >= dates["sign_on"]:
        return LedgerResult(Entry(dates["sign_on"], dates["sign_off"], vessel, "", ex.capacity.value if quote_in_text(ex.capacity.quote, ph) else "",
                                  ex.ship_type.value if quote_in_text(ex.ship_type.quote, ph) else ""), sorted(set(unread)), refused)
    return LedgerResult(None, sorted(set(unread)), refused)
