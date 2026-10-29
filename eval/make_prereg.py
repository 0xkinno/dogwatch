"""Write eval/cases/prereg.json: the case sets, expected outcomes and metric definitions, before any run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    corpus = json.loads((CASES / "seal_corpus.json").read_text(encoding="utf-8"))
    profiles = json.loads((CASES / "profiles.json").read_text(encoding="utf-8"))
    convs = json.loads((CASES / "conventions.json").read_text(encoding="utf-8"))
    prereg = {
        "version": 1,
        "registered": "2026-10-28",
        "note": "Case files are never edited after their run. An amendment is a new version with a reason.",
        "sets": {
            "P3_encoding_corpus": {
                "file": "cases/seal_corpus.json", "sha256": sha(CASES / "seal_corpus.json"),
                "attacks": len(corpus["attacks"]), "legitimate": len(corpus["legit"]),
                "expected": "every attack should be denied, every legitimate body allowed",
                "metrics": {"miss": "attack body allowed", "false_block": "legitimate body denied"},
                "guards": ["literal-only guard (case-sensitive substring on UTF-8 body)", "the Seal"],
                "synthetic_values": True,
            },
            "P6_engine_vs_model": {
                "file": "cases/profiles.json", "sha256": sha(CASES / "profiles.json"), "profiles": len(profiles),
                "expected": "verdict per profile written by an independent oracle from the rule text before any run",
                "metrics": {"false_safe": "said READY when the expected verdict is not READY",
                            "false_alarm": "said NOT_READY or CANNOT_VERIFY when the expected verdict is READY",
                            "wrong_other": "any other disagreement"},
                "contestants": ["Navigator (code)", "Nemotron Super", "Nemotron Ultra"],
                "synthetic": True,
            },
            "P7_counting_conventions": {
                "file": "cases/conventions.json", "sha256": sha(CASES / "conventions.json"), "histories": len(convs),
                "expected": "none; this set measures disagreement",
                "metrics": {"flip": "verdict differs between at least two counting conventions"},
                "conventions": ["days_inclusive", "days_exclusive", "calendar_months", "days_360", "days_365"],
                "synthetic": True,
            },
        },
    }
    out = CASES / "prereg.json"
    out.write_text(json.dumps(prereg, indent=1), encoding="utf-8", newline="\n")
    print("prereg sha256", sha(out))


if __name__ == "__main__":
    main()
