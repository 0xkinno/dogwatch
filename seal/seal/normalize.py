"""The Seal's matcher: does a request carry a vault value under any normalisation?

Views of a body are produced by decoders (URL, base64, base64url, hex, JSON unescape, adjacent-field
concatenation). Each view is folded (NFKC, case-fold, separators and zero-width characters removed,
digit homoglyphs for numeric identifiers) and compared with the folded needles, forwards and reversed.
Needles live in memory only. Decisions name the kind and the transform path, never the value.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import unicodedata
import urllib.parse
from dataclasses import dataclass, field

MIN_NEEDLE = 5
MAX_DEPTH = 3
MAX_TOKENS = 200

_SEPS = re.compile(r"[\s\-./_" + "".join(chr(c) for c in (0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x00AD)) + "]+")
_HOMO = str.maketrans({"o": "0", "i": "1", "l": "1", "s": "5", "b": "8"})
_B64 = re.compile(r"[A-Za-z0-9+/_\-]{12,}={0,2}")
_HEX = re.compile(r"(?:[0-9a-fA-F]{2}){6,}")


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).casefold()
    return _SEPS.sub("", s)


def homo(s: str) -> str:
    return s.translate(_HOMO)


def _numericish(s: str) -> bool:
    return sum(c.isdigit() for c in s) * 2 >= max(1, len(s))


@dataclass(frozen=True)
class Needle:
    kind: str
    folded: str
    homo_folded: str | None
    fp: str  # salted fingerprint for logs; the value never appears in a log


@dataclass
class Decision:
    deny: bool
    kind: str = ""
    path: tuple[str, ...] = ()
    fp: str = ""


def build_needles(values: list[tuple[str, str]], salt: bytes) -> list[Needle]:
    out = []
    for kind, v in values:
        f = fold(v)
        if len(f) < MIN_NEEDLE:
            continue
        h = homo(f) if _numericish(f) else None
        fp = hashlib.sha256(salt + f.encode()).hexdigest()[:8]
        out.append(Needle(kind, f, h, fp))
    return out


def _printable(b: bytes) -> str | None:
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s and sum(c.isprintable() or c in "\r\n\t" for c in s) / len(s) > 0.85 else None


def _decode_b64(tok: str) -> str | None:
    t = tok.rstrip("=")
    for alt in (False, True):
        try:
            raw = base64.b64decode((t.replace("-", "+").replace("_", "/") if alt else t) + "=" * (-len(t) % 4), validate=False)
        except (binascii.Error, ValueError):
            continue
        s = _printable(raw)
        if s:
            return s
    return None


def _leaves(obj, out: list[str], keys: list[str] | None = None) -> None:
    """String values in document order. Keys go to a separate list so split values stay adjacent."""
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            (keys if keys is not None else out).append(str(k))
            _leaves(v, out, keys)
    elif isinstance(obj, list):
        for v in obj:
            _leaves(v, out, keys)


def views(text: str, path: tuple[str, ...] = (), depth: int = 0):
    """Yield (view_text, transform_path). Depth limited; each decoder adds one step to the path."""
    yield text, path
    if depth >= MAX_DEPTH:
        return
    # JSON unescape and adjacent-field concatenation
    stripped = text.strip()
    if stripped[:1] in "{[":
        try:
            obj = json.loads(stripped)
        except ValueError:
            obj = None
        if obj is not None:
            leaves: list[str] = []
            keys: list[str] = []
            _leaves(obj, leaves, keys)
            if leaves:
                yield "\n".join(keys + leaves), path + ("json",)
                if len(leaves) > 1:
                    yield "".join(leaves), path + ("json", "concat")
                    for a, b in zip(leaves, leaves[1:]):
                        yield a + b, path + ("json", "adjacent")
                for leaf in leaves:
                    if leaf != text:
                        yield from views(leaf, path + ("json",), depth + 1)
    # URL decode, repeated
    cur = text
    for i in range(3):
        nxt = urllib.parse.unquote_plus(cur)
        if nxt == cur:
            break
        cur = nxt
        yield cur, path + ("urldecode",) * (i + 1)
        if i == 0:
            yield from views(cur, path + ("urldecode",), depth + 1) if depth + 1 < MAX_DEPTH else ()
    # base64 and hex tokens
    seen = 0
    for m in _B64.finditer(text):
        seen += 1
        if seen > MAX_TOKENS:
            break
        dec = _decode_b64(m.group(0))
        if dec and dec != text:
            yield dec, path + ("base64",)
            yield from views(dec, path + ("base64",), depth + 1)
    for m in _HEX.finditer(text):
        seen += 1
        if seen > MAX_TOKENS:
            break
        try:
            dec = _printable(bytes.fromhex(m.group(0)))
        except ValueError:
            dec = None
        if dec:
            yield dec, path + ("hex",)
            yield from views(dec, path + ("hex",), depth + 1)


def match(text: str, needles: list[Needle]) -> Decision:
    for view, path in views(text):
        f = fold(view)
        fh = homo(f)
        for n in needles:
            if n.folded in f:
                return Decision(True, n.kind, path + ("fold",), n.fp)
            if n.folded[::-1] in f:
                return Decision(True, n.kind, path + ("reversed",), n.fp)
            if n.homo_folded and (n.homo_folded in fh or n.homo_folded[::-1] in fh):
                return Decision(True, n.kind, path + ("homoglyph",), n.fp)
    return Decision(False)


def check_body(body: bytes, extra: list[str], needles: list[Needle]) -> Decision:
    """Scan the body, plus the query string, path and header values passed in extra."""
    texts = [body.decode("utf-8", errors="replace")] + [e for e in extra if e]
    for t in texts:
        d = match(t, needles)
        if d.deny:
            return d
    return Decision(False)
