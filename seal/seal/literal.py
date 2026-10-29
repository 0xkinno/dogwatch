"""A configured-literal guard: the baseline the Seal is measured against.

Same behaviour as the NVIDIA content-guard example documents for itself: case-sensitive literal terms
on a UTF-8 body, no decoding, no normalisation.
"""
from __future__ import annotations


class LiteralGuard:
    def __init__(self, values: list[tuple[str, str]]):
        self.values = [(k, v) for k, v in values if v]

    def deny(self, body: bytes) -> bool:
        text = body.decode("utf-8", errors="replace")
        return any(v in text for _, v in self.values)
