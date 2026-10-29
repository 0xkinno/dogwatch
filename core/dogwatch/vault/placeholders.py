"""Typed placeholders for identifiers. Stable per value within a vault: [[COC_1]] always means the same CoC."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Found:
    kind: str
    value: str
    start: int
    end: int
    verified: bool = True


def _key(value: str) -> str:
    return re.sub(r"[\s\-./]", "", value).casefold()


class Registry:
    """Maps normalised identifier values to placeholders and back.

    The real values live here and in the encrypted vault only. Nothing in this class logs a value.
    """

    def __init__(self, data: dict | None = None):
        self._by_key: dict[str, str] = {}
        self._values: dict[str, str] = {}
        self._counts: dict[str, int] = {}
        if data:
            self._values = dict(data.get("values", {}))
            self._counts = dict(data.get("counts", {}))
            self._by_key = dict(data.get("by_key", {}))

    def assign(self, kind: str, value: str) -> str:
        kind = kind.upper()
        k = f"{kind}:{_key(value)}"
        if k in self._by_key:
            return self._by_key[k]
        n = self._counts.get(kind, 0) + 1
        self._counts[kind] = n
        ph = f"[[{kind}_{n}]]"
        self._by_key[k] = ph
        self._values[ph] = value
        return ph

    def rehydrate(self, text: str) -> str:
        """Host side only, after an approval token has been verified."""
        return re.sub(r"\[\[[A-Z_]+_\d+\]\]", lambda m: self._values.get(m.group(0), m.group(0)), text)

    def values(self) -> list[tuple[str, str]]:
        """(kind, value) pairs for the Seal's fingerprint set."""
        return [(ph[2:ph.rindex("_")], v) for ph, v in self._values.items()]

    def export(self) -> dict:
        return {"values": self._values, "counts": self._counts, "by_key": self._by_key}

    def __len__(self) -> int:
        return len(self._values)


def resolve_overlaps(found: list[Found]) -> list[Found]:
    """Keep the longest match when matches overlap; ties go to the earlier start."""
    ordered = sorted(found, key=lambda f: (-(f.end - f.start), f.start))
    kept: list[Found] = []
    for f in ordered:
        if all(f.end <= k.start or f.start >= k.end for k in kept):
            kept.append(f)
    return sorted(kept, key=lambda f: f.start)


def replace_identifiers(text: str, detectors, registry: Registry) -> tuple[str, list[Found]]:
    """Return text with every detected identifier replaced by its stable placeholder."""
    found: list[Found] = []
    for det in detectors:
        found.extend(det(text))
    kept = resolve_overlaps(found)
    out = text
    for f in sorted(kept, key=lambda f: f.start, reverse=True):
        out = out[:f.start] + registry.assign(f.kind, f.value) + out[f.end:]
    return out, kept
