"""Rule pack loader. Packs are YAML with a source quote per rule, checked against a snapshot."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PACK_ROOT = Path(__file__).resolve().parents[2] / "rulepacks"


@dataclass(frozen=True)
class Rule:
    id: str
    administration: str
    kind: str
    applies_to: dict
    params: dict
    source: dict
    status: str = ""
    pack: str = ""

    def to_ref(self, pack_sha: str) -> dict:
        return {
            "rule_id": self.id,
            "kind": self.kind,
            "quote": self.source.get("quote", ""),
            "url": self.source.get("url", ""),
            "section": self.source.get("section", ""),
            "retrieved": self.source.get("retrieved", ""),
            "status": self.status,
            "pack": self.pack,
            "pack_sha256": pack_sha,
        }


@dataclass
class Pack:
    id: str
    version: str
    administration: str
    status: str
    path: Path
    rules: list[Rule] = field(default_factory=list)
    sha256: str = ""

    def rules_of(self, kind: str, document: str | None = None) -> list[Rule]:
        out = []
        for r in self.rules:
            if r.kind != kind:
                continue
            docs = r.applies_to.get("document")
            if document and docs and document not in docs:
                continue
            out.append(r)
        return out


def norm(s: str) -> str:
    """Whitespace and hyphen normalisation only, as the quote check requires."""
    s = s.replace(" ", " ").replace("‐", "-").replace("‑", "-")
    s = re.sub(r"\s*-\s*", "-", s)
    return " ".join(s.split())


def pack_sha256(path: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(x for x in path.rglob("*") if x.is_file() and x.name != ".gitkeep"):
        h.update(p.relative_to(path).as_posix().encode())
        h.update(b"\0")
        h.update(p.read_bytes().replace(b"\r\n", b"\n"))
        h.update(b"\0")
    return h.hexdigest()


def load_pack(path: Path) -> Pack:
    meta = yaml.safe_load((path / "pack.yaml").read_text(encoding="utf-8"))
    raw = yaml.safe_load((path / meta["rules_file"]).read_text(encoding="utf-8")) or []
    pack = Pack(
        id=meta["id"], version=str(meta["version"]), administration=meta["administration"],
        status=meta.get("status", "sourced"), path=path,
    )
    for r in raw:
        pack.rules.append(Rule(
            id=r["id"], administration=r["administration"], kind=r["kind"],
            applies_to=r.get("applies_to", {}), params=r.get("params", {}),
            source=r["source"], status=r.get("status", ""), pack=meta["id"],
        ))
    pack.sha256 = pack_sha256(path)
    return pack


def load_all(root: Path = PACK_ROOT) -> dict[str, Pack]:
    return {p.name: load_pack(p) for p in sorted(root.iterdir()) if (p / "pack.yaml").exists()}


def verify_quotes(pack: Pack) -> list[str]:
    """Return failures: every rule quote must appear verbatim in its snapshot."""
    failures = []
    for r in pack.rules:
        snap = pack.path / "sources" / r.source["file"]
        if not snap.exists():
            failures.append(f"{r.id}: snapshot {r.source['file']} missing")
            continue
        quote = r.source.get("quote", "")
        if len(quote.split()) >= 60:
            failures.append(f"{r.id}: quote is 60 words or longer")
        if norm(quote) not in norm(snap.read_text(encoding="utf-8")):
            failures.append(f"{r.id}: quote not found in {r.source['file']}")
    return failures


def packs_for(packs: dict[str, Pack], administration: str) -> list[Pack]:
    """The convention pack plus any pack whose administration or id contains the key."""
    key = administration.lower()
    chosen = []
    for p in packs.values():
        if p.id == "stcw-core" or (key and (key in p.administration.lower() or key in p.id.lower())):
            chosen.append(p)
    return chosen
