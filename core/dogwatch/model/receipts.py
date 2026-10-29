"""One receipt per model call: id, model, tokens, latency, cost. Never stores prompt or reply text."""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_lock = threading.Lock()


def receipts_path() -> Path:
    return Path(os.environ.get("DOGWATCH_RECEIPTS", ROOT / "evidence" / "receipts" / "receipts.jsonl"))


def pricing() -> dict:
    """List prices (USD per million tokens) read at probe time. Absent until the Phase 2 probe writes them."""
    p = ROOT / "docs" / "pricing.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


@dataclass
class Receipt:
    response_id: str
    model: str
    role: str
    tokens_in: int
    tokens_out: int
    reasoning_tokens: int
    latency_ms: int
    attempt: int
    cost_usd: float | None
    ts: float


def cost_for(model: str, tokens_in: int, tokens_out: int) -> float | None:
    price = pricing().get("models", {}).get(model)
    if not price:
        return None  # never invent a price
    return round((tokens_in * price["input_per_m"] + tokens_out * price["output_per_m"]) / 1_000_000, 8)


def record(response, *, model: str, role: str, attempt: int, started: float) -> Receipt:
    usage = getattr(response, "usage", None)
    t_in = int(getattr(usage, "prompt_tokens", 0) or 0)
    t_out = int(getattr(usage, "completion_tokens", 0) or 0)
    details = getattr(usage, "completion_tokens_details", None)
    reasoning = int(getattr(details, "reasoning_tokens", 0) or 0) if details else 0
    rc = Receipt(
        response_id=str(getattr(response, "id", "")), model=model, role=role, tokens_in=t_in, tokens_out=t_out,
        reasoning_tokens=reasoning, latency_ms=int((time.time() - started) * 1000), attempt=attempt,
        cost_usd=cost_for(model, t_in, t_out), ts=time.time(),
    )
    path = receipts_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(rc)) + "\n")
    return rc


def load_all() -> list[dict]:
    p = receipts_path()
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
