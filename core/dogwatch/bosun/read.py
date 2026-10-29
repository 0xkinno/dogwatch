"""Bosun: placeholder text in, typed document out. Quotes are verified; dates are parsed by code."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from ..model import client
from ..navigator.readiness import Document
from ..vault.identifiers import DEFAULT_DETECTORS
from ..vault.placeholders import Registry, replace_identifiers
from .schema import SYSTEM, Extraction, QuotedField
from .verify_quote import parse_date_from_quote, quote_in_text


@dataclass
class ReadResult:
    document: Document
    placeholder_text: str
    unread_fields: list[str] = field(default_factory=list)
    quotes_refused: int = 0
    extraction: Extraction | None = None
    identifiers_replaced: int = 0


def _structure(text: str) -> Extraction:
    return client.structured("structure", SYSTEM, text, Extraction)


def read_text(raw_text: str, *, registry: Registry, doc_id: str, label: str = "", administration_hint: str = "default",
              structure=_structure, detectors=DEFAULT_DETECTORS) -> ReadResult:
    """Run the Bosun on OCR text. The model only ever sees the placeholder text."""
    ph_text, found = replace_identifiers(raw_text, detectors, registry)
    ex = structure(ph_text)
    unread: list[str] = []
    refused = 0

    def checked(name: str, f: QuotedField) -> QuotedField | None:
        nonlocal refused
        if not f.value and not f.quote:
            unread.append(name)
            return None
        if not quote_in_text(f.quote, ph_text):
            refused += 1
            unread.append(name)
            return None
        return f

    admin = checked("administration", ex.administration)
    expiry_f = checked("expiry_date", ex.expiry_date)
    checked("issue_date", ex.issue_date)
    checked("capacity", ex.capacity)

    if ex.doc_type != "other" and not quote_in_text(ex.doc_type_quote, ph_text):
        refused += 1
        unread.append("doc_type")
        doc_type = "other"
    else:
        doc_type = ex.doc_type

    expiry: date | None = None
    if expiry_f is not None:
        expiry = parse_date_from_quote(expiry_f.quote, administration_hint)
        if expiry is None:
            unread.append("expiry_date")
    doc = Document(
        id=doc_id, doc_type=doc_type, administration=(admin.value if admin else administration_hint.title()),
        expiry=expiry, unread=expiry is None or "doc_type" in unread, label=label or doc_type,
    )
    return ReadResult(doc, ph_text, sorted(set(unread)), refused, ex, len(found))
