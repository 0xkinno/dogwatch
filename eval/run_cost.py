"""P12: tokens and latency per unit of work, from receipts. No dollar figure is shown: the NVIDIA API Catalog route has no
list price and no Token Factory call has been made, and a price is never invented. The counterfactual is expressed in tokens
and seconds: what the same work costs if the largest model handled every call."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REC = HERE.parent / "evidence" / "receipts"


def load(name):
    p = REC / name
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def agg(rows):
    n = len(rows)
    return {"calls": n, "tokens_in": sum(r["tokens_in"] for r in rows), "tokens_out": sum(r["tokens_out"] for r in rows),
            "mean_latency_ms": int(sum(r["latency_ms"] for r in rows) / n) if n else 0,
            "reasoning_tokens": sum(r["reasoning_tokens"] for r in rows)}


def main():
    p6 = load("p6-nvidia_build.jsonl")
    by_model = defaultdict(list)
    for r in p6:
        by_model[r["model"]].append(r)
    p8, p9, p10 = load("p8-nvidia_build.jsonl"), load("p9-drift.jsonl"), load("p10-unattended.jsonl")
    ultra = next((m for m in by_model if "ultra" in m), None)
    sup = next((m for m in by_model if "super" in m), None)
    per_call_ultra = agg(by_model[ultra]) if ultra else None
    per_call_super = agg(by_model[sup]) if sup else None
    out = {
        "set": "P12_cost", "route": "nvidia_build", "route_label": "Route: NVIDIA API Catalog (development)", "price_available": False,
        "note": "No list price exists for this route, so no dollar figure is shown. Token Factory prices are measured once a key exists (scripts/switch_to_tokenfactory.sh).",
        "p6_by_model": {m: agg(v) for m, v in by_model.items()},
        "p8_reading_per_specimen": {**agg(p8), "per_specimen_tokens_in": int(sum(r["tokens_in"] for r in p8) / max(1, len(p8))), "per_specimen_tokens_out": int(sum(r["tokens_out"] for r in p8) / max(1, len(p8)))},
        "p9_drift_week": agg(p9), "p10_weekly_check_one_administration": agg(p10),
        "weekly_check_tokens": agg(p9)["tokens_in"] + agg(p9)["tokens_out"],
        "readiness_run_tokens": 0,
        "readiness_run_note": "The Navigator computes the verdict in code and calls no model.",
    }
    if per_call_ultra and per_call_super:
        out["counterfactual_ultra_for_every_call"] = {
            "mean_latency_ms_if_ultra": per_call_ultra["mean_latency_ms"], "mean_latency_ms_actual_super": per_call_super["mean_latency_ms"],
            "latency_ratio_ultra_over_super": round(per_call_ultra["mean_latency_ms"] / max(1, per_call_super["mean_latency_ms"]), 2),
            "note": "Same prompts (P6), so token counts are equal; the difference is latency and the larger model's price, which is not available on this route.",
        }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p12_cost.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k] for k in ("p6_by_model", "weekly_check_tokens", "counterfactual_ultra_for_every_call") if k in out}, indent=1))


if __name__ == "__main__":
    main()
