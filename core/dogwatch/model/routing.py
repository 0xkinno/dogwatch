"""Which Nemotron handles which job. Ids come from docs/models.json, written by the Phase 2 probe."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# Role to (size class, thinking, token cap). Size classes resolve to a model id at call time.
ROLES = {
    "triage": ("nano", False, 400),
    "structure": ("super", False, 2000),
    "plan": ("ultra", True, 3000),
    "drift": ("nano", False, 600),
}

# Ids listed in the build notes. NOT confirmed until the probe writes docs/models.json.
UNCONFIRMED_DEFAULTS = {
    "nano": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    "super": "nvidia/nemotron-3-super-120b-a12b",
    "ultra": "nvidia/Nemotron-3-Ultra-550b-a55b",
}


@dataclass(frozen=True)
class Route:
    role: str
    size: str
    model: str
    thinking: bool
    max_tokens: int
    confirmed: bool


def _models_file() -> dict:
    p = ROOT / "docs" / "models.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def route(role: str) -> Route:
    size, thinking, cap = ROLES[role]
    env = os.environ.get(f"DOGWATCH_MODEL_{size.upper()}")
    probed = _models_file().get("confirmed", {}).get(size)
    model = env or probed or UNCONFIRMED_DEFAULTS[size]
    return Route(role, size, model, thinking, cap, confirmed=bool(env or probed))
