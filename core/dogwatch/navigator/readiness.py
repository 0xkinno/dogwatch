"""Contract readiness. Every verdict is computed here, in code, from dates and rule packs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from .dates import Entry, add_months
from .rulepack import Pack, packs_for
from .seaservice import check_requirement

VALID_THROUGH = "VALID_THROUGH"
LAPSES_DURING = "LAPSES_DURING"
EXPIRED_BEFORE_START = "EXPIRED_BEFORE_START"
WINDOW_NOT_OPEN = "WINDOW_NOT_OPEN"
WINDOW_OPEN = "WINDOW_OPEN"
UNREAD = "UNREAD"
MISSING = "MISSING"
ASK_ADMINISTRATION = "ASK_ADMINISTRATION"

READY, NOT_READY, CANNOT_VERIFY = "READY", "NOT_READY", "CANNOT_VERIFY"


@dataclass(frozen=True)
class Document:
    id: str
    doc_type: str  # coc, endorsement, medical, passport, cdc, bst, ...
    administration: str
    expiry: date | None
    unread: bool = False
    label: str = ""  # shown to the seafarer, never an identifier
    endorsement: str = ""


@dataclass(frozen=True)
class Window:
    start: date
    end: date
    travel_before: int = 0
    travel_after: int = 0

    @property
    def check_start(self) -> date:
        return self.start - timedelta(days=self.travel_before)

    @property
    def check_end(self) -> date:
        return self.end + timedelta(days=self.travel_after)

    @property
    def length(self) -> int:
        return (self.check_end - self.check_start).days + 1


@dataclass
class DocVerdict:
    document_id: str
    doc_type: str
    label: str
    state: str
    expiry: str | None
    arithmetic: str = ""
    day_x: int | None = None
    day_y: int | None = None
    renewal: dict | None = None
    rules: list[dict] = field(default_factory=list)
    sea_service: list[dict] = field(default_factory=list)


@dataclass
class Readiness:
    overall: str
    window_start: str
    window_end: str
    documents: list[DocVerdict]
    summary: str
    pack_hashes: dict


def _renewal(doc: Document, packs: dict[str, Pack], today: date) -> tuple[dict, list[dict]]:
    chosen = packs_for(packs, doc.administration.split()[0] if doc.administration else "")
    rules = [r for p in chosen for r in p.rules_of("window_open", doc.doc_type)]
    if doc.expiry is None or not rules:
        return {"state": ASK_ADMINISTRATION, "reason": "no sourced renewal window rule for this administration"}, []
    r = rules[0]
    months = int(r.params["months_before_expiry"])
    opens = add_months(doc.expiry, -months)
    state = WINDOW_OPEN if today >= opens else WINDOW_NOT_OPEN
    return (
        {"state": state, "opens_on": opens.isoformat(), "arithmetic": f"{doc.expiry} minus {months} months = {opens}"},
        [r.to_ref(packs[r.pack].sha256)],
    )


def _sea_checks(doc: Document, packs: dict[str, Pack], ledger: list[Entry], today: date) -> list[dict]:
    if not ledger or doc.doc_type not in ("coc", "endorsement"):
        return []
    out = []
    for p in packs_for(packs, doc.administration.split()[0] if doc.administration else ""):
        for kind in ("sea_service", "tanker_sea_service"):
            for r in p.rules_of(kind, doc.doc_type):
                chk = check_requirement(ledger, r.params, today)
                out.append({
                    "rule": r.to_ref(p.sha256), "verdict": chk.verdict, "agree": chk.agree,
                    "window": [chk.window_start.isoformat(), chk.window_end.isoformat()],
                    "arithmetic": chk.arithmetic,
                })
    return out


def doc_verdict(doc: Document, window: Window, packs: dict[str, Pack], today: date, ledger: list[Entry]) -> DocVerdict:
    v = DocVerdict(doc.id, doc.doc_type, doc.label or doc.doc_type, UNREAD, doc.expiry.isoformat() if doc.expiry else None)
    if doc.unread or doc.expiry is None:
        v.arithmetic = "expiry date not read; a missing fact never produces READY"
        return v
    s, e = window.check_start, window.check_end
    if doc.expiry < s:
        v.state = EXPIRED_BEFORE_START
        v.arithmetic = f"expiry {doc.expiry} is before window start {s}"
    elif doc.expiry < e:
        v.state = LAPSES_DURING
        v.day_x = (doc.expiry - s).days + 1
        v.day_y = window.length
        v.arithmetic = f"expiry {doc.expiry} minus start {s} plus 1 = day {v.day_x}; window {s} to {e} = {v.day_y} days"
    else:
        v.state = VALID_THROUGH
        v.arithmetic = f"expiry {doc.expiry} is on or after window end {e}"
    if v.state in (LAPSES_DURING, EXPIRED_BEFORE_START):
        v.renewal, v.rules = _renewal(doc, packs, today)
    v.sea_service = _sea_checks(doc, packs, ledger, today)
    return v


def readiness(documents: list[Document], window: Window, packs: dict[str, Pack], today: date,
              ledger: list[Entry] | None = None, required_types: list[str] | None = None) -> Readiness:
    ledger = ledger or []
    verdicts = [doc_verdict(d, window, packs, today, ledger) for d in documents]
    present = {d.doc_type for d in documents}
    for t in required_types or []:
        if t not in present:
            verdicts.append(DocVerdict(f"missing-{t}", t, t, MISSING, None, f"required document type {t} not in the vault"))
    states = [v.state for v in verdicts]
    if any(s in (LAPSES_DURING, EXPIRED_BEFORE_START) for s in states):
        overall = NOT_READY
    elif any(s in (UNREAD, MISSING, ASK_ADMINISTRATION) for s in states):
        overall = CANNOT_VERIFY
    else:
        overall = READY
    lapses = [v for v in verdicts if v.state == LAPSES_DURING]
    if overall == NOT_READY and lapses:
        first = min(lapses, key=lambda x: x.expiry or "")
        summary = f"Not ready: {first.label} lapses {first.expiry} (day {first.day_x} of {first.day_y})."
    elif overall == NOT_READY:
        summary = "Not ready: a certificate expires before the contract starts."
    elif overall == CANNOT_VERIFY:
        summary = "Cannot verify: at least one fact is unread, missing or needs the administration."
    else:
        summary = f"Ready: every document is valid through {window.check_end}."
    shas = {p.id: p.sha256 for p in packs.values()}
    return Readiness(overall, window.check_start.isoformat(), window.check_end.isoformat(), verdicts, summary, shas)
