"""The renewal packet: what goes to the manning agent after approval. Drafts hold placeholders only."""
from __future__ import annotations

from .digest import digest


def build_packet(result: dict, plan: dict, *, identifier_lines: dict[str, str], recipient: str,
                 attachments: list[str] | None = None) -> dict:
    """identifier_lines maps a label to a placeholder, for example {"Seafarer": "[[NAME_1]]"}."""
    rows = []
    for d in result["documents"]:
        row = {"document": d["label"], "state": d["state"], "expiry": d["expiry"], "arithmetic": d["arithmetic"],
               "rules": [r["rule_id"] for r in d.get("rules", [])]}
        if d.get("renewal"):
            row["renewal"] = d["renewal"]
        rows.append(row)
    body = {
        "title": "Document readiness for your offered contract",
        "window": [result["window_start"], result["window_end"]],
        "verdict": result["overall"],
        "summary": result["summary"],
        "plan": plan["text"],
        "plan_source": plan["source"],
        "rows": rows,
        "identifier_lines": identifier_lines,
        "pack_hashes": result["pack_hashes"],
    }
    atts = sorted(attachments or [])
    return {"packet": body, "recipients": [recipient], "attachments": atts, "digest": digest(body, [recipient], atts)}
