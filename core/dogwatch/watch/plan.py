"""Plan writer. A model writes prose around locked value tokens; code supplies every date and number.

Any digit outside a token, or a token we did not offer, replaces the model text with a deterministic template.
"""
from __future__ import annotations

import re
from datetime import date

from ..model import client

_TOKEN = re.compile(r"\{\{(V\d+)\}\}")
_DASHES = {0x2013: ",", 0x2014: ","}

SYSTEM = (
    "You write a short, calm plan for a seafarer whose certificate needs attention before a contract. "
    "Use the value tokens such as {{V1}} exactly where a date or number belongs. Never write a digit yourself. "
    "Do not decide validity. No emoji. Under 90 words."
)


def _fmt(d: str) -> str:
    return date.fromisoformat(d).strftime("%d %b %Y").lstrip("0")


def locked_values(result: dict) -> dict[str, str]:
    """Token to display string, built from the navigator result only."""
    vals: dict[str, str] = {}
    n = 0
    lapse = next((d for d in result["documents"] if d["state"] == "LAPSES_DURING"), None)
    if lapse:
        for key, text in (("label", lapse["label"]), ("expiry", _fmt(lapse["expiry"])),
                          ("x", str(lapse["day_x"])), ("y", str(lapse["day_y"]))):
            n += 1
            vals[f"V{n}"] = text
    n += 1
    vals[f"V{n}"] = _fmt(result["window_start"])
    n += 1
    vals[f"V{n}"] = _fmt(result["window_end"])
    return vals


def template_plan(result: dict) -> str:
    lapse = next((d for d in result["documents"] if d["state"] == "LAPSES_DURING"), None)
    if lapse:
        return (f"Not ready: {lapse['label']} lapses on {_fmt(lapse['expiry'])}, day {lapse['day_x']} of "
                f"{lapse['day_y']} of the contract. Book the renewal before joining. Everything else is checked in code "
                f"and listed in the packet. Approve the packet to send it to your agent.")
    if result["overall"] == "READY":
        return f"Ready: every document is valid through {_fmt(result['window_end'])}. Approve the packet to send it."
    return "Cannot verify yet: some facts are unread or need the administration. Open the packet to see which."


def valid_text(text: str, tokens: dict[str, str]) -> bool:
    used = set(_TOKEN.findall(text))
    if not used or not used <= set(tokens):
        return False
    stripped = _TOKEN.sub("", text)
    return not re.search(r"\d", stripped)


def write_plan(result: dict, *, writer=None) -> dict:
    """Returns {"text", "source"} where source is MODEL or TEMPLATE (labelled, never silent)."""
    tokens = locked_values(result)
    if result["overall"] == "READY" or not any(d["state"] == "LAPSES_DURING" for d in result["documents"]):
        return {"text": template_plan(result), "source": "TEMPLATE", "reason": "no lapse to plan around"}
    prompt = "Tokens:\n" + "\n".join(f"{{{{{k}}}}} = {v}" for k, v in tokens.items()) + "\nWrite the plan."
    try:
        raw = (writer or (lambda s, u: client.text("plan", s, u)))(SYSTEM, prompt)
    except (client.ModelUnavailable, client.ModelOutputInvalid) as e:
        return {"text": template_plan(result), "source": "TEMPLATE", "reason": f"model unavailable: {type(e).__name__}"}
    raw = raw.translate(_DASHES)
    if not valid_text(raw, tokens):
        return {"text": template_plan(result), "source": "TEMPLATE", "reason": "free digit or unknown token in model text"}
    return {"text": _TOKEN.sub(lambda m: tokens[m.group(1)], raw), "source": "MODEL", "reason": ""}
