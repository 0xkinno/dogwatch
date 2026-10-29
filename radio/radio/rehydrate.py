"""Rehydration and PDF building. Host side only, after an approval token has been verified."""
from __future__ import annotations

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

from dogwatch.vault.placeholders import Registry


def packet_text(body: dict, registry: Registry) -> str:
    lines = [body["title"], f"Contract window: {body['window'][0]} to {body['window'][1]}", f"Verdict: {body['verdict']}",
             body["summary"], "", body["plan"], ""]
    for label, ph in body["identifier_lines"].items():
        lines.append(f"{label}: {ph}")
    lines.append("")
    for r in body["rows"]:
        lines.append(f"- {r['document']}: {r['state']} (expiry {r['expiry']})")
    return registry.rehydrate("\n".join(lines))


def build_pdf(body: dict, registry: Registry) -> bytes:
    """The rehydrated packet as a PDF. Real identifiers exist only in these bytes, built here."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Document readiness")
    st = getSampleStyleSheet()
    story = [Paragraph(registry.rehydrate(body["title"]), st["Title"]),
             Paragraph(f"Contract window: {body['window'][0]} to {body['window'][1]}", st["Normal"]),
             Paragraph(f"Verdict: {body['verdict']}", st["Heading3"]),
             Paragraph(registry.rehydrate(body["plan"]), st["Normal"]), Spacer(1, 12)]
    for label, ph in body["identifier_lines"].items():
        story.append(Paragraph(f"{label}: {registry.rehydrate(ph)}", st["Normal"]))
    story.append(Spacer(1, 12))
    rows = [["Document", "State", "Expiry"]] + [[r["document"], r["state"], r["expiry"] or "unread"] for r in body["rows"]]
    story.append(Table(rows))
    doc.build(story)
    return buf.getvalue()
