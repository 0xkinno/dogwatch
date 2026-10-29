#!/usr/bin/env python3
"""House style gate. Fails on emoji, em or en dashes, hype words and hashed denylist tokens.

Scans tracked and untracked-but-not-ignored text files. The denylist is stored as SHA-256 hashes
so the gate can run in CI without the repository ever spelling the banned names.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = "scripts/check_copy.py"
DENYLIST = "scripts/denylist.sha256"

DASHES = {chr(0x2014): "em dash", chr(0x2013): "en dash"}
HYPE = [
    "revolutionary", "seamless", "cutting-edge", "world-class", "zero-trust",
    "military-grade", "game-changing", "unprecedented",
]
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U0001F900-\U0001F9FF"
    "\U00002B00-\U00002BFF\U0000FE0F\U0000200D]"
)
TEXT_EXT = {
    ".md", ".txt", ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".json", ".yaml", ".yml", ".toml",
    ".css", ".html", ".sh", ".proto", ".rs", ".cfg", ".ini", ".example", ".jsonl", ".svg", ".gitignore",
}
TEXT_NAMES = {"commit-msg", ".gitignore", ".gitattributes", ".env.example", "LICENSE"}
SKIP_FILES = {"LICENSE"}  # standard licence text is used verbatim
# Verbatim third-party snapshots under /sources/ and /snapshots/ are quoted evidence, not our copy.


def tracked_files() -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, text=True
    )
    return [p for p in out.splitlines() if p]


def load_denylist() -> dict[str, str]:
    path = ROOT / DENYLIST
    table: dict[str, str] = {}
    if not path.exists():
        return table
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, scope = line.split("\t")
        table[digest] = scope
    return table


def main() -> int:
    deny = load_denylist()
    problems: list[str] = []
    for rel in tracked_files():
        p = ROOT / rel
        if not p.is_file() or rel in SKIP_FILES or "/sources/" in rel or "/snapshots/" in rel:
            continue
        if p.suffix.lower() not in TEXT_EXT and p.name not in TEXT_NAMES:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"{rel}: not valid UTF-8")
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for ch, label in DASHES.items():
                if ch in line:
                    problems.append(f"{rel}:{n}: {label}")
            if EMOJI.search(line):
                problems.append(f"{rel}:{n}: emoji")
            if rel != SELF:
                low = line.lower()
                for w in HYPE:
                    if w in low:
                        problems.append(f"{rel}:{n}: banned word '{w}'")
            if rel in (SELF, DENYLIST):
                continue
            for tok in set(re.findall(r"[a-z0-9]+", line.lower())):
                scope = deny.get(hashlib.sha256(tok.encode()).hexdigest())
                if scope is None:
                    continue
                if scope.startswith("except:") and rel == scope.split(":", 1)[1]:
                    continue
                problems.append(f"{rel}:{n}: denylisted term (hashed)")
    if problems:
        print("check_copy FAILED")
        for item in problems:
            print("  " + item)
        return 1
    print("check_copy ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
