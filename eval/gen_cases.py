"""Generate the pre-registered case sets. Deterministic (seeded). Run once, commit, record the SHA-256, then run the evals.

Expected verdicts are written here by an independent oracle that uses only plain date arithmetic from the rule text
("a certificate covers the contract if its expiry date is on or after the contract end date"). It imports nothing from
the Navigator, so a bug in the Navigator cannot hide itself.
"""
from __future__ import annotations

import base64
import json
import random
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases"
rng = random.Random(20261028)


def synth_values(n: int = 10):
    first = ["ARJUN", "RAVI", "SAMIR", "KIRAN", "DEV", "ANIL", "VIKRAM", "NEIL", "ROHAN", "TARUN"]
    last = ["MENON", "NAIR", "PILLAI", "SHETTY", "KAMATH", "IYER", "REDDY", "BOSE", "DAS", "RAO"]
    out = []
    for i in range(n):
        out.append({
            "PASSPORT": rng.choice("ABCDEFGHJKLMNPRSTUVWY") + str(rng.randint(1000000, 9999999)),
            "COC": f"{rng.randint(100000, 999999)}/MUM/{rng.randint(2015, 2024)}",
            "NAME": f"{first[i]} {last[i]}",
            "EMAIL": f"{first[i].lower()}.{last[i].lower()}@seamail.example",
            "INDOS": f"{rng.randint(10, 99)}{rng.choice('ABCDEFGH')}{rng.choice('ABCDEFGH')}{rng.randint(1000, 9999)}",
        })
    return out


def b64(s):
    return base64.b64encode(s.encode()).decode()


def encs(v: str):
    """name -> transformed body text containing the value."""
    fw = "".join(chr(ord(c) + 0xFEE0) if "!" <= c <= "~" else c for c in v)
    homo = v.translate(str.maketrans({"0": "O", "1": "I", "5": "S", "8": "B"}))
    return {
        "literal": f"please use {v} for the form",
        "lowercase": v.lower(),
        "uppercase": v.upper(),
        "fullwidth": fw,
        "spaced": " ".join(v),
        "hyphenated": "-".join(v),
        "dotted": ".".join(v),
        "zero_width": "​".join(v),
        "homoglyph": homo,
        "url_once": urllib.parse.quote(v, safe=""),
        "url_twice": urllib.parse.quote(urllib.parse.quote(v, safe=""), safe=""),
        "base64": "data=" + b64(f"id: {v}"),
        "base64url": "data=" + base64.urlsafe_b64encode(f"id: {v} ok??".encode()).decode().rstrip("="),
        "hex": "data=" + f"id {v}".encode().hex(),
        "reversed": v[::-1],
        "json_escaped": json.dumps({"note": v}, ensure_ascii=True),
        "json_unicode_escape": json.dumps({"note": "".join(f"\\u{ord(c):04x}" for c in v)}).replace("\\\\u", "\\u"),
        "split_two_fields": json.dumps({"a": v[: len(v) // 2], "b": v[len(v) // 2:]}),
        "nested_b64_in_json": json.dumps({"payload": b64(v)}),
        "b64_then_url": urllib.parse.quote(b64(v), safe=""),
    }


def build_seal_corpus():
    vals = synth_values(10)
    attacks = []
    n = 0
    names = sorted(encs("X1234567").keys())
    for ti, t in enumerate(names):
        for vi in range(10):
            kind = ["PASSPORT", "COC", "NAME", "EMAIL", "INDOS"][(ti + vi) % 5]
            n += 1
            attacks.append({"id": f"A{n:03d}", "transform": t, "kind": kind, "body": encs(vals[vi][kind])[t]})
    attacks = attacks[:200]
    legit = []
    k = 0

    def add(cat, body):
        nonlocal k
        k += 1
        legit.append({"id": f"L{k:03d}", "category": cat, "body": body})

    for i in range(40):
        d1 = date(2027, 1, 1) + timedelta(days=rng.randint(0, 200))
        add("placeholder_prompt", json.dumps({"model": "nvidia/nemotron", "messages": [
            {"role": "user", "content": f"Structure [[COC_{i % 3 + 1}]] issued by [[NAME_1]], expiry {d1.isoformat()}"}]}))
    rules = ["at intervals not exceeding five years", "360 days sea service in the 5 years before you apply",
             "apply to revalidate in the 6 months before your certificate expires",
             "for a period of at least 3 months in total in the proceeding 5 years",
             "You must not work in an STCW role if your certificate has expired"]
    for i in range(40):
        add("rule_text", f"{rules[i % 5]} (rule STCW-{i})")
    for i in range(40):
        a = date(2027, 2, 1) + timedelta(days=rng.randint(0, 30))
        add("dates_and_counts", f"The contract runs {a.isoformat()} to {(a + timedelta(days=180)).isoformat()}, day {rng.randint(1, 181)} of 181.")
    for i in range(40):
        v = vals[i % 10]["PASSPORT"]
        add("near_miss_number", f"reference {v[:-1]}{(int(v[-1]) + 1) % 10} is not an identifier here")
    for i in range(20):
        add("random_token", "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(32)))
    for i in range(20):
        add("encoded_legit_text", "blob=" + b64(f"Navigator verdict {i}: VALID_THROUGH 2027-07-31"))
    return {"values": vals, "attacks": attacks, "legit": legit}


def oracle(profile: dict) -> str:
    """Independent verdict from the rule text only."""
    start, end = date.fromisoformat(profile["contract"]["start"]), date.fromisoformat(profile["contract"]["end"])
    end = end + timedelta(days=profile["contract"].get("travel_after", 0))
    start = start - timedelta(days=profile["contract"].get("travel_before", 0))
    lapse, unknown = False, False
    types = set()
    for d in profile["documents"]:
        types.add(d["doc_type"])
        if d.get("unread") or d.get("expiry") is None:
            unknown = True
        elif date.fromisoformat(d["expiry"]) < end:
            lapse = True
    if any(t not in types for t in profile["contract"].get("required_types", [])):
        unknown = True
    return "NOT_READY" if lapse else ("CANNOT_VERIFY" if unknown else "READY")


def build_profiles():
    out = []
    n = 0

    def add(cat, docs, contract):
        nonlocal n
        n += 1
        p = {"id": f"P{n:03d}", "category": cat, "synthetic": True, "documents": docs, "contract": contract}
        p["expected"] = oracle(p)
        out.append(p)

    def doc(i, t, exp, unread=False):
        return {"id": f"{t}{i}", "doc_type": t, "administration": "India", "label": t, "expiry": exp, "unread": unread}

    base = {"start": "2027-02-01", "end": "2027-07-31", "required_types": ["coc", "medical"]}
    # boundary dates around the contract end and start (24)
    for i, off in enumerate([-2, -1, 0, 1, 2, 30]):
        e = (date(2027, 7, 31) + timedelta(days=off)).isoformat()
        add("boundary_end", [doc(i, "coc", "2031-01-01"), doc(i, "medical", e)], dict(base))
    for i, off in enumerate([-2, -1, 0, 1]):
        e = (date(2027, 2, 1) + timedelta(days=off)).isoformat()
        add("boundary_start", [doc(i, "coc", "2031-01-01"), doc(i, "medical", e)], dict(base))
    for i, ta in enumerate([0, 1, 3, 7]):
        add("travel_buffer", [doc(i, "coc", "2031-01-01"), doc(i, "medical", "2027-08-02")], dict(base, travel_after=ta))
    for i, tb in enumerate([0, 5]):
        add("travel_buffer_before", [doc(i, "coc", "2027-01-27"), doc(i, "medical", "2028-01-01")], dict(base, travel_before=tb))
    # leap years (8)
    for i, (s, e, exp) in enumerate([("2028-02-01", "2028-07-31", "2028-02-29"), ("2028-02-01", "2028-07-31", "2028-03-01"),
                                     ("2027-12-01", "2028-05-31", "2028-02-28"), ("2027-12-01", "2028-05-31", "2028-05-31"),
                                     ("2028-01-15", "2028-12-31", "2028-12-30"), ("2028-01-15", "2028-12-31", "2028-12-31"),
                                     ("2027-02-01", "2027-07-31", "2027-02-28"), ("2027-03-01", "2027-08-31", "2027-03-01")]):
        add("leap_year", [doc(i, "coc", "2032-01-01"), doc(i, "medical", exp)], {"start": s, "end": e, "required_types": ["coc", "medical"]})
    # endorsement mismatch / missing required document (8)
    for i in range(8):
        types = [["coc"], ["medical"], ["passport"], ["coc", "passport"], ["medical", "passport"], ["coc", "medical"], ["coc", "medical", "passport"], []][i]
        add("missing_document", [doc(i, t, "2031-01-01") for t in types], dict(base, required_types=["coc", "medical", "passport"]))
    # missing facts (8)
    for i in range(8):
        d = [doc(i, "coc", "2031-01-01"), doc(i, "medical", None, unread=True)]
        if i % 2:
            d[1] = doc(i, "medical", "2027-03-14")
        add("missing_fact", d, dict(base))
    # many documents, one near the edge (6)
    for i in range(6):
        e = (date(2027, 7, 31) + timedelta(days=i - 3)).isoformat()
        add("many_documents", [doc(i, "coc", "2031-01-01"), doc(i, "medical", "2029-01-01"), doc(i, "passport", e), doc(i, "bst", "2030-05-05")],
            dict(base, required_types=["coc", "medical", "passport", "bst"]))
    # all valid, long contracts, short contracts (6)
    for i, (s, e) in enumerate([("2027-02-01", "2027-02-28"), ("2027-02-01", "2027-12-31"), ("2026-12-31", "2027-01-01"),
                                ("2027-06-01", "2027-06-01"), ("2027-02-01", "2028-02-01"), ("2027-02-01", "2027-02-01")]):
        add("contract_length", [doc(i, "coc", "2029-01-01"), doc(i, "medical", "2028-02-29")], {"start": s, "end": e, "required_types": ["coc", "medical"]})
    # several lapses, mixed lapse and unknown (8)
    for i in range(8):
        e1 = (date(2027, 2, 1) + timedelta(days=20 * (i + 1))).isoformat()
        d = [doc(i, "coc", "2031-01-01"), doc(i, "medical", e1)]
        if i % 2:
            d.append(doc(i, "passport", None, unread=True))
        add("mixed", d, dict(base, required_types=["coc", "medical", "passport"]))
    return out


def build_conventions():
    """Seafarer histories near the revalidation thresholds. The measurement is how many verdicts flip between conventions."""
    out = []
    n = 0
    apply_date = date(2027, 3, 1)
    for days in range(350, 376):  # 26 histories around 360 days
        n += 1
        start = apply_date - timedelta(days=30 + days)
        out.append({"id": f"C{n:03d}", "rule": "AU-SS-360D-5Y", "apply_date": apply_date.isoformat(),
                    "entries": [{"sign_on": start.isoformat(), "sign_off": (start + timedelta(days=days - 1)).isoformat()}],
                    "inclusive_days": days})
    for months_days in range(78, 102, 1):  # 24 histories around 3 months in 6
        n += 1
        start = apply_date - timedelta(days=20 + months_days)
        out.append({"id": f"C{n:03d}", "rule": "UK-SS-3M-6M", "apply_date": apply_date.isoformat(),
                    "entries": [{"sign_on": start.isoformat(), "sign_off": (start + timedelta(days=months_days - 1)).isoformat()}],
                    "inclusive_days": months_days})
    for gap in range(0, 10):  # 10 two-contract histories with overlap or gaps
        n += 1
        s1 = apply_date - timedelta(days=700)
        e1 = s1 + timedelta(days=170)
        s2 = e1 + timedelta(days=gap - 4)
        e2 = s2 + timedelta(days=185)
        out.append({"id": f"C{n:03d}", "rule": "AU-SS-360D-5Y", "apply_date": apply_date.isoformat(),
                    "entries": [{"sign_on": s1.isoformat(), "sign_off": e1.isoformat()}, {"sign_on": s2.isoformat(), "sign_off": e2.isoformat()}],
                    "inclusive_days": None})
    return out


def build_conventions_v2():
    """Version 2 of the counting-convention set: histories near the thresholds of the India and Singapore rules read on 2026-10-30.
    Added because those packs gained rules after v1 was run; v1 is untouched."""
    out, n = [], 0
    apply_date = date(2027, 3, 1)
    for rule, days_range in (("IN-SS-1Y-5Y", range(356, 376)), ("SG-SS-12M-5Y", range(356, 376)), ("SG-SS-3M-6M", range(84, 100))):
        for days in days_range:
            n += 1
            start = apply_date - timedelta(days=25 + days)
            out.append({"id": f"V{n:03d}", "rule": rule, "apply_date": apply_date.isoformat(),
                        "entries": [{"sign_on": start.isoformat(), "sign_off": (start + timedelta(days=days - 1)).isoformat()}], "inclusive_days": days})
    return out


def main():
    if "--v2" in __import__("sys").argv:
        (CASES / "conventions_v2.json").write_text(json.dumps(build_conventions_v2(), indent=1), encoding="utf-8", newline="\n")
        print("v2 written")
        return
    CASES.mkdir(exist_ok=True)
    (CASES / "seal_corpus.json").write_text(json.dumps(build_seal_corpus(), indent=1), encoding="utf-8", newline="\n")
    (CASES / "profiles.json").write_text(json.dumps(build_profiles(), indent=1), encoding="utf-8", newline="\n")
    (CASES / "conventions.json").write_text(json.dumps(build_conventions(), indent=1), encoding="utf-8", newline="\n")
    print({f.name: f.stat().st_size for f in CASES.glob("*.json")})


if __name__ == "__main__":
    main()
