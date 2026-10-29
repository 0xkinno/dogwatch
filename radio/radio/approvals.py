"""Approval tokens: single-use HMAC bound to a packet digest, expiring in 24 hours."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

TTL_SECONDS = 24 * 3600


class ApprovalError(Exception):
    pass


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def issue(secret: bytes, draft_id: str, digest: str, now: float | None = None) -> str:
    """Created only when the seafarer taps Approve on the message that shows the digest."""
    body = {"d": draft_id, "g": digest, "e": int((now or time.time()) + TTL_SECONDS), "t": secrets.token_hex(8)}
    raw = _b64(json.dumps(body, sort_keys=True).encode())
    sig = _b64(hmac.new(secret, raw.encode(), hashlib.sha256).digest())
    return f"{raw}.{sig}"


def verify(secret: bytes, token: str, draft_id: str, current_digest: str, state, now: float | None = None) -> None:
    """Raises ApprovalError unless the token is genuine, unexpired, unused and bound to the digest recomputed now."""
    try:
        raw, sig = token.split(".", 1)
    except ValueError as e:
        raise ApprovalError("malformed token") from e
    good = _b64(hmac.new(secret, raw.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(good, sig):
        raise ApprovalError("bad signature")
    body = json.loads(_unb64(raw))
    if body["d"] != draft_id:
        raise ApprovalError("token is for a different draft")
    if (now or time.time()) > body["e"]:
        raise ApprovalError("token expired")
    if not hmac.compare_digest(body["g"], current_digest):
        raise ApprovalError("digest mismatch: the packet changed after approval")
    if not state.use_token(body["t"]):
        raise ApprovalError("token already used")
