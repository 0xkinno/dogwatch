"""Deterministic identifier detectors. Each returns Found spans; none calls a model."""
from __future__ import annotations

import re

from .placeholders import Found

_WEIGHTS = (7, 3, 1)


def _val(ch: str) -> int:
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    if "A" <= ch <= "Z":
        return ord(ch) - ord("A") + 10
    raise ValueError(ch)


def mrz_check_digit(field: str) -> str:
    """ICAO 9303 check digit: weights 7, 3, 1 repeating, sum mod 10."""
    total = sum(_val(c) * _WEIGHTS[i % 3] for i, c in enumerate(field))
    return str(total % 10)


def parse_mrz_td3(line1: str, line2: str) -> dict:
    """Parse a two-line passport MRZ (44 characters per line) and report check digit validity."""
    if len(line1) != 44 or len(line2) != 44:
        raise ValueError("TD3 lines must be 44 characters")
    number, c_num = line2[0:9], line2[9]
    dob, c_dob = line2[13:19], line2[19]
    exp, c_exp = line2[21:27], line2[27]
    pers, c_pers = line2[28:42], line2[42]
    c_comp = line2[43]
    composite = line2[0:10] + line2[13:20] + line2[21:43]
    checks = {
        "number": mrz_check_digit(number) == c_num,
        "dob": mrz_check_digit(dob) == c_dob,
        "expiry": mrz_check_digit(exp) == c_exp,
        "personal": mrz_check_digit(pers) == c_pers or (set(pers) == {"<"} and c_pers in "<0"),
        "composite": mrz_check_digit(composite) == c_comp,
    }
    names = line1[5:].split("<<", 1)
    surname = names[0].replace("<", " ").strip()
    given = names[1].replace("<", " ").strip() if len(names) > 1 else ""
    return {
        "number": number.replace("<", ""), "issuer": line1[2:5], "surname": surname, "given": given,
        "dob": dob, "expiry": exp, "checks": checks, "valid": all(checks.values()),
    }


_MRZ = re.compile(r"(P[<A-Z][A-Z<]{3}[A-Z0-9<]{39})\s*\n\s*([A-Z0-9<]{44})")


def detect_mrz(text: str) -> list[Found]:
    """A whole MRZ block, then the name and passport number inside it. Invalid check digits are still
    redacted: over-redaction is the safe failure."""
    out: list[Found] = []
    for m in _MRZ.finditer(text):
        l1, l2 = m.group(1), m.group(2)
        try:
            info = parse_mrz_td3(l1, l2)
            ok = info["valid"]
        except ValueError:
            ok = False
            info = None
        out.append(Found("MRZ", m.group(0), m.start(), m.end(), ok))
        if info:
            if info["number"]:
                i = text.find(l2[0:9].replace("<", ""), m.start(2))
                if i >= 0:
                    out.append(Found("PASSPORT", info["number"], i, i + len(info["number"]), info["checks"]["number"]))
    return out


_PASSPORT_IN = re.compile(r"(?<![A-Z0-9])[A-PR-WY][ ]?[1-9](?:[ ]?\d){6}(?![A-Z0-9])")


def detect_passport_number(text: str) -> list[Found]:
    """India style: one letter (not Q, X, Z) then seven digits."""
    return [Found("PASSPORT", m.group(0), m.start(), m.end()) for m in _PASSPORT_IN.finditer(text)]


def _labelled(kind: str, label_pattern: str):
    rx = re.compile(
        r"(?i)(?:" + label_pattern + r")\s*(?:no\.?|number|#)?\s*[:.\-]?\s*([A-Z0-9][A-Z0-9/\-]{3,19}(?:[ ](?=[A-Z0-9/\-]*[0-9/])[A-Z0-9/\-]{1,12}){0,2})(?![A-Z0-9])"
    )

    def detect(text: str) -> list[Found]:
        out = []
        for m in rx.finditer(text):
            val = m.group(1)
            if any(c.isdigit() for c in val):
                out.append(Found(kind, val, m.start(1), m.end(1)))
        return out

    return detect


detect_coc = _labelled("COC", r"\bC\.?O\.?C\.?(?=\s|:|#|\.)")
detect_indos = _labelled("INDOS", r"\bINDoS\b")
detect_cdc = _labelled("CDC", r"\bC\.?D\.?C\.?(?=\s|:|#|\.)")
detect_coe = _labelled("COE", r"\bC\.?O\.?E\.?(?=\s|:|#|\.)")

_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def detect_email(text: str) -> list[Found]:
    return [Found("EMAIL", m.group(0), m.start(), m.end()) for m in _EMAIL.finditer(text)]


_PHONE = re.compile(r"(?<![\w/])\+?\d[\d\s().\-]{8,16}\d(?!\w)")
_DATEISH = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}$")


def detect_phone(text: str) -> list[Found]:
    out = []
    for m in _PHONE.finditer(text):
        s = m.group(0).strip()
        digits = re.sub(r"\D", "", s)
        if len(digits) < 10 or _DATEISH.match(s):
            continue
        out.append(Found("PHONE", s, m.start(), m.start() + len(s)))
    return out


def known_values_detector(values: list[tuple[str, str]]):
    """Detector built from the vault's own identifier table: exact, case-insensitive matches of values the vault holds,
    for example the holder's name, which no pattern can find."""
    pairs = [(k, v) for k, v in values if v and len(v) >= 4]

    def detect(text: str) -> list[Found]:
        low = text.casefold()
        out = []
        for kind, v in pairs:
            # OCR inserts stray punctuation and spaces between words, so match the words with a loose separator
            words = [re.escape(w) for w in re.split(r"[\s.,;:_\-]+", v) if w]
            rx = re.compile(r"[\s.,;:_\-]{0,3}".join(words), re.I)
            for m in rx.finditer(text):
                out.append(Found(kind, m.group(0), m.start(), m.end()))
        return out

    return detect


DEFAULT_DETECTORS = (detect_mrz, detect_passport_number, detect_coc, detect_indos, detect_cdc, detect_coe,
                     detect_email, detect_phone)
