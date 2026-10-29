#!/usr/bin/env python3
"""Phase 2 probe for one model route. Usage: python scripts/probe.py [tokenfactory|nvidia_build]

1. GET /models and record the exact Nemotron ids on that route (docs/models.json).
2. Measure thinking on versus off on one real Bosun extraction (tokens, latency).
3. Test whether JSON schema is enforced server side, and whether the repair path is used.
Writes evidence/probe/<route>.json. Prints no key and no document text.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "core")]

from dogwatch import envload  # noqa: E402

envload.load()
if len(sys.argv) > 1:
    os.environ["MODEL_ROUTE"] = sys.argv[1]

import httpx  # noqa: E402
from dogwatch.bosun.schema import SYSTEM, Extraction  # noqa: E402
from dogwatch.model import client, receipts  # noqa: E402
from dogwatch.model.routes import api_key, selected_route  # noqa: E402

SPECIMEN = """SPECIMEN
Medical Fitness Certificate
Issued by: India
Certificate No: [[COC_1]]
Date of expiry: 14/03/2027
"""


PREFER = {
    "nano": ["nemotron-3-nano-30b-a3b", "nemotron-3-nano-omni-30b-a3b-reasoning", "nemotron-3.5-lightning-30b-a3b", "nemotron-nano-3-30b-a3b"],
    "super": ["nemotron-3-super-120b-a12b", "nemotron-3.5-super-vl-120b-a12b"],
    "ultra": ["nemotron-3-ultra-550b-a55b", "llama-3.1-nemotron-ultra-253b-v1"],
}


def chat_status(base: str, key: str, model: str) -> int:
    """One-word chat. A listed model can still answer 404, so the list alone is not trusted."""
    for _ in range(2):
        try:
            r = httpx.post(base.rstrip("/") + "/chat/completions", headers={"Authorization": f"Bearer {key}"},
                           json={"model": model, "messages": [{"role": "user", "content": "Reply with the single word ok."}],
                                 "max_tokens": 16, "temperature": 0}, timeout=90)
        except httpx.HTTPError:
            return 0
        if r.status_code != 503:
            return r.status_code
        time.sleep(3)
    return 503


def pick(ids: list[str], base: str, key: str) -> tuple[dict, dict]:
    chosen, checks = {}, {}
    for size, prefs in PREFER.items():
        for suffix in prefs:
            m = next((i for i in ids if i.endswith(suffix)), None)
            if not m or m in checks and checks[m] != 200:
                continue
            st = checks.get(m) or chat_status(base, key, m)
            checks[m] = st
            if st == 200:
                chosen[size] = m
                break
    return chosen, checks


def main() -> int:
    r = selected_route()
    key = api_key(r)
    rec: dict = {"route": r.name, "route_label": f"Route: {r.label}", "probed_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if not key:
        rec["state"] = "NOT_CONFIGURED"
        print(json.dumps(rec))
        return 1
    t0 = time.time()
    resp = httpx.get(r.base_url.rstrip("/") + "/models", headers={"Authorization": f"Bearer {key}"}, timeout=30)
    rec["models_http"] = resp.status_code
    rec["models_latency_ms"] = int((time.time() - t0) * 1000)
    if resp.status_code != 200:
        rec["state"] = "ERROR"
        print(json.dumps(rec))
        return 1
    ids = sorted(m["id"] for m in resp.json().get("data", []))
    nem = [i for i in ids if "nemotron" in i.lower()]
    rec["total_models"] = len(ids)
    rec["nemotron_models"] = nem
    confirmed, checks = pick(nem, r.base_url, key)
    rec["chat_check"] = checks
    rec["confirmed_by_size"] = confirmed

    mf = ROOT / "docs" / "models.json"
    data = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    data.setdefault("routes", {})[r.name] = {"confirmed": confirmed, "all_nemotron": nem, "probed_at": rec["probed_at"]}
    mf.parent.mkdir(exist_ok=True)
    mf.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8", newline="\n")

    os.environ["DOGWATCH_RECEIPTS"] = str(ROOT / "evidence" / "receipts" / f"probe-{r.name}.jsonl")
    Path(os.environ["DOGWATCH_RECEIPTS"]).unlink(missing_ok=True)
    c = client.get_client()
    sup = confirmed.get("super") or confirmed.get("nano")
    rec["extraction_model"] = sup

    def run(thinking: bool):
        t = time.time()
        try:
            out = c.chat.completions.create(
                model=sup, temperature=0, max_tokens=3000,
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": SPECIMEN}],
                extra_body={"chat_template_kwargs": {"enable_thinking": thinking}})
        except Exception as e:  # recorded as a result, not hidden
            return {"thinking": thinking, "error": type(e).__name__ + ": " + str(e)[:160]}
        u = out.usage
        det = getattr(u, "completion_tokens_details", None)
        content = out.choices[0].message.content or ""
        reasoning = getattr(out.choices[0].message, "reasoning_content", None) or getattr(out.choices[0].message, "reasoning", None)
        parsed = None
        try:
            parsed = Extraction.model_validate_json(client.extract_json(content)).model_dump()
        except Exception:
            pass
        return {"thinking": thinking, "latency_ms": int((time.time() - t) * 1000), "tokens_in": u.prompt_tokens,
                "tokens_out": u.completion_tokens, "reasoning_tokens": getattr(det, "reasoning_tokens", None) if det else None,
                "reasoning_field_present": bool(reasoning), "content_chars": len(content), "valid_schema_reply": parsed is not None,
                "expiry_quote_found": bool(parsed and "14/03/2027" in (parsed.get("expiry_date", {}).get("quote", "")))}

    rec["thinking_comparison"] = [run(False), run(True)]

    # schema enforcement: ask for prose, with a schema attached. If the reply still parses as the schema, the server enforced it.
    trials = []
    for _ in range(3):
        try:
            out = c.chat.completions.create(
                model=sup, temperature=0, max_tokens=800,
                messages=[{"role": "system", "content": "Reply in two plain English sentences. Do not use JSON."}, {"role": "user", "content": SPECIMEN}],
                response_format={"type": "json_schema", "json_schema": {"name": "Extraction", "schema": Extraction.model_json_schema()}},
                extra_body={"chat_template_kwargs": {"enable_thinking": False}})
            txt = out.choices[0].message.content or ""
            try:
                Extraction.model_validate_json(client.extract_json(txt))
                trials.append("schema_valid")
            except Exception:
                trials.append("prose_or_invalid")
        except Exception as e:
            trials.append("error:" + type(e).__name__)
    rec["schema_enforcement_trials"] = trials
    rec["schema_enforced_server_side"] = all(t == "schema_valid" for t in trials)

    # repair path: the schema asks for a field the prompt never mentions, so the first reply tends to fail validation
    try:
        from pydantic import BaseModel

        class Strict(BaseModel):
            expiry_iso: str
            certificate_state: str

        n0 = len(receipts.load_all())
        client.structured("structure", "Return JSON with keys expiry_iso (YYYY-MM-DD) and certificate_state (one word).", SPECIMEN, Strict)
        calls = len(receipts.load_all()) - n0
        rec["repair_probe"] = {"calls": calls, "repair_used": calls > 1}
    except Exception as e:
        rec["repair_probe"] = {"error": type(e).__name__}

    rec["state"] = "LIVE RUN"
    out = ROOT / "evidence" / "probe"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{r.name}.json").write_text(json.dumps(rec, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: rec[k] for k in ("route_label", "total_models", "confirmed_by_size", "thinking_comparison", "schema_enforcement_trials", "repair_probe")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
