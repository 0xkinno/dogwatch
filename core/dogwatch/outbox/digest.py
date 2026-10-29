"""Digest of exactly what will be sent. The seafarer approves the digest; sending recomputes it."""
from __future__ import annotations

import hashlib
import json


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(packet_with_placeholders: dict, recipients: list[str], attachment_hashes: list[str]) -> str:
    payload = {
        "packet": packet_with_placeholders,
        "recipients": sorted(r.strip().lower() for r in recipients),
        "attachments": sorted(attachment_hashes),
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def short(d: str) -> str:
    return d[:8]
