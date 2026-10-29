"""Quote verification and date parsing. Dates come from verified quotes parsed by code, never from the model."""
from __future__ import annotations

import re
from datetime import date, datetime

_DASHES = {cp: "-" for cp in (0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2212)}


def normalise(s: str) -> str:
    """Whitespace and hyphen normalisation only."""
    s = s.translate(_DASHES).replace(" ", " ")
    s = re.sub(r"\s*-\s*", "-", s)
    return " ".join(s.split())


def quote_in_text(quote: str, text: str) -> bool:
    q = normalise(quote)
    return bool(q) and q in normalise(text)


DATE_FORMATS = {
    "default": ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %b %Y", "%d %B %Y", "%d-%b-%Y", "%Y-%m-%d"),
    "india": ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %b %Y", "%d %B %Y", "%d-%b-%Y"),
    "singapore": ("%d/%m/%Y", "%d %b %Y", "%d %B %Y", "%d-%b-%Y", "%Y-%m-%d"),
    "uk": ("%d/%m/%Y", "%d %b %Y", "%d %B %Y", "%d.%m.%Y"),
    "australia": ("%d/%m/%Y", "%d %b %Y", "%d %B %Y", "%Y-%m-%d"),
    "nigeria": ("%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d %B %Y"),
}

_CAND = re.compile(
    r"\d{4}-\d{2}-\d{2}|\d{1,2}[/.\-]\d{1,2}[/.\-]\d{4}|\d{1,2}[ \-][A-Za-z]{3,9}\.?[ \-]\d{4}"
)


def parse_date_from_quote(quote: str, administration: str = "default") -> date | None:
    """The one date inside a verified quote, or None if there is none or it is ambiguous."""
    fmts = DATE_FORMATS.get(administration.lower(), DATE_FORMATS["default"])
    found: set[date] = set()
    for m in _CAND.finditer(normalise(quote)):
        s = m.group(0).replace(".", " ") if re.search(r"[A-Za-z]", m.group(0)) else m.group(0)
        s = " ".join(s.split())
        for f in fmts:
            try:
                found.add(datetime.strptime(s, f).date())
                break
            except ValueError:
                continue
    return next(iter(found)) if len(found) == 1 else None
