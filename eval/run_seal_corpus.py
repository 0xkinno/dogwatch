"""P3: a literal-only guard against the Seal, both directions, every case by id."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "seal"))

from seal import normalize  # noqa: E402
from seal.literal import LiteralGuard  # noqa: E402


def main():
    corpus = json.loads((HERE / "cases" / "seal_corpus.json").read_text(encoding="utf-8"))
    values = [(k, v) for row in corpus["values"] for k, v in row.items()]
    lit = LiteralGuard(values)
    needles = normalize.build_needles(values, b"eval-salt-0000000")
    rows = {"attacks": [], "legit": []}
    for a in corpus["attacks"]:
        body = a["body"].encode()
        s = normalize.check_body(body, [], needles)
        rows["attacks"].append({"id": a["id"], "transform": a["transform"], "literal_denied": lit.deny(body),
                                "seal_denied": s.deny, "seal_path": list(s.path)})
    for c in corpus["legit"]:
        body = c["body"].encode()
        s = normalize.check_body(body, [], needles)
        rows["legit"].append({"id": c["id"], "category": c["category"], "literal_denied": lit.deny(body), "seal_denied": s.deny})
    atk, leg = rows["attacks"], rows["legit"]
    by_t = {}
    for t in sorted({a["transform"] for a in atk}):
        sub = [a for a in atk if a["transform"] == t]
        by_t[t] = {"n": len(sub), "literal_missed": sum(not a["literal_denied"] for a in sub),
                   "seal_missed": sum(not a["seal_denied"] for a in sub)}
    res = {
        "set": "P3_encoding_corpus", "seal_version": "v2 (base64 token minimum lowered from 12 to 8 characters after the v1 run, see PROOF.md)", "attacks": len(atk), "legitimate": len(leg),
        "literal": {"missed": sum(not a["literal_denied"] for a in atk), "false_blocks": sum(c["literal_denied"] for c in leg),
                    "missed_ids": [a["id"] for a in atk if not a["literal_denied"]],
                    "false_block_ids": [c["id"] for c in leg if c["literal_denied"]]},
        "seal": {"missed": sum(not a["seal_denied"] for a in atk), "false_blocks": sum(c["seal_denied"] for c in leg),
                 "missed_ids": [a["id"] for a in atk if not a["seal_denied"]],
                 "false_block_ids": [c["id"] for c in leg if c["seal_denied"]]},
        "by_transform": by_t,
        "false_blocks_by_category": dict(Counter(c["category"] for c in leg if c["seal_denied"])),
        "cases": rows,
    }
    out = HERE / "results" / "p3_seal_corpus.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print({k: res[k] for k in ("attacks", "legitimate")}, {g: {k: res[g][k] for k in ("missed", "false_blocks")} for g in ("literal", "seal")})
    print("seal missed ids:", res["seal"]["missed_ids"], "seal false blocks:", res["seal"]["false_block_ids"])


if __name__ == "__main__":
    main()
