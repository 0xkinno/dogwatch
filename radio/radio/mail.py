"""Email through Resend's REST API. Without a key it reports NOT_CONFIGURED; it never pretends to send."""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]


def redact(addr: str) -> str:
    local, _, domain = addr.partition("@")
    return f"{local[:1]}***@{domain[:1]}***.{domain.rsplit('.', 1)[-1]}" if domain else "***"


class Mailer:
    def __init__(self, api_key: str | None = None, sender: str | None = None, transport: httpx.BaseTransport | None = None):
        self.api_key = api_key if api_key is not None else os.environ.get("RESEND_API_KEY", "")
        self.sender = sender or os.environ.get("RESEND_FROM", "")
        self.client = httpx.Client(transport=transport, timeout=30)

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.sender)

    def send(self, *, to: str, subject: str, text: str, attachments: list[tuple[str, bytes]], idempotency_key: str) -> dict:
        if not self.configured:
            return {"sent": False, "mode": "NOT_CONFIGURED"}
        payload = {"from": self.sender, "to": [to], "subject": subject, "text": text,
                   "attachments": [{"filename": n, "content": base64.b64encode(b).decode()} for n, b in attachments]}
        r = self.client.post("https://api.resend.com/emails", content=json.dumps(payload),
                             headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                                      "Idempotency-Key": idempotency_key})
        ok = r.status_code in (200, 201)
        return {"sent": ok, "mode": "LIVE", "status": r.status_code, "id": r.json().get("id") if ok else None}


def record_action(kind: str, recipient: str, digest: str, result: dict, directory: Path | None = None) -> Path:
    """Evidence of a real action, recipient redacted, no packet content."""
    d = directory or Path(os.environ.get("DOGWATCH_ACTIONS_DIR", ROOT / "evidence" / "actions"))
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{int(time.time())}-{kind}-{digest[:8]}.json"
    p.write_text(json.dumps({"kind": kind, "recipient": redact(recipient), "digest": digest[:8], "result": result,
                             "ts": time.time()}, indent=2), encoding="utf-8")
    return p
