"""Send an approved packet: verify the token against a freshly computed digest, check the allowlist, rehydrate, send once."""
from __future__ import annotations

from pathlib import Path

from dogwatch.outbox.digest import digest as compute_digest
from dogwatch.vault.placeholders import Registry
from dogwatch.watch.state import State

from . import approvals
from .mail import Mailer, record_action
from .rehydrate import build_pdf, packet_text


class SendRefused(Exception):
    pass


def approve(state: State, secret: bytes, draft_id: str) -> str:
    """Called when the seafarer taps Approve. Marks the draft approved and returns the token."""
    d = state.draft(draft_id)
    if not d or d["status"] not in ("PENDING", "APPROVED"):
        raise SendRefused("draft is not pending")
    token = approvals.issue(secret, draft_id, d["digest"])
    state.set_status(draft_id, "APPROVED")
    return token


def send_approved(state: State, secret: bytes, draft_id: str, token: str, registry: Registry, mailer: Mailer,
                  allowlist: set[str], evidence_dir: Path | None = None) -> dict:
    d = state.draft(draft_id)
    if not d:
        raise SendRefused("unknown draft")
    if d["status"] == "SENT":
        return {"sent": False, "mode": "DUPLICATE_SUPPRESSED"}
    pk = d["payload"]
    current = compute_digest(pk["packet"], pk["recipients"], pk["attachments"])
    try:
        approvals.verify(secret, token, draft_id, current, state)
    except approvals.ApprovalError as e:
        raise SendRefused(str(e)) from e
    to = pk["recipients"][0]
    if to.strip().lower() not in {a.strip().lower() for a in allowlist}:
        raise SendRefused("recipient is not on the allowlist")
    if not state.claim_send(draft_id):
        return {"sent": False, "mode": "DUPLICATE_SUPPRESSED"}
    try:
        pdf = build_pdf(pk["packet"], registry)
        res = mailer.send(to=to, subject="Document readiness", text=packet_text(pk["packet"], registry),
                          attachments=[("readiness.pdf", pdf)], idempotency_key=d["idempotency_key"])
    except Exception:
        state.release_send(draft_id)
        raise
    if res.get("sent"):
        state.complete_send(draft_id)
        record_action("email", to, current, res, evidence_dir)
    else:
        state.release_send(draft_id)
    return res
