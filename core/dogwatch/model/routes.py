"""Model routes. Exactly two hosts are allowed. Token Factory is the submission target; the NVIDIA API Catalog
is a development route for the same Nemotron models while a Token Factory key is unavailable.

A result produced on one route is never described as a result of the other. Every receipt, status response and
result file carries the route label.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Route:
    name: str
    base_url: str
    key_env: str
    host: str
    label: str


ROUTES = {
    "tokenfactory": Route("tokenfactory", "https://api.tokenfactory.nebius.com/v1/", "NEBIUS_API_KEY",
                          "api.tokenfactory.nebius.com", "Nebius Token Factory"),
    "nvidia_build": Route("nvidia_build", "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY",
                          "integrate.api.nvidia.com", "NVIDIA API Catalog (development)"),
}
ALLOWED_HOSTS = {r.host for r in ROUTES.values()}

# One table: size class to model id, per route. Ids are NOT trusted until the probe confirms them from GET /v1/models
# on that route (docs/models.json). Defaults below are the ids named in the build notes and the catalog sample.
DEFAULT_IDS = {
    "tokenfactory": {
        "nano": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
        "super": "nvidia/nemotron-3-super-120b-a12b",
        "ultra": "nvidia/Nemotron-3-Ultra-550b-a55b",
    },
    "nvidia_build": {
        "nano": "nvidia/nemotron-3-nano-30b-a3b",
        "super": "nvidia/nemotron-3-super-120b-a12b",
        "ultra": "nvidia/nemotron-3-ultra-550b-a55b",
    },
}


def selected_route() -> Route:
    """MODEL_ROUTE wins when set. Otherwise Token Factory when its key exists, else the development route."""
    want = (os.environ.get("MODEL_ROUTE") or "").strip().lower()
    if want:
        if want not in ROUTES:
            raise ValueError(f"MODEL_ROUTE must be one of {sorted(ROUTES)}")
        return ROUTES[want]
    if os.environ.get("NEBIUS_API_KEY"):
        return ROUTES["tokenfactory"]
    return ROUTES["nvidia_build"]


def models_file() -> dict:
    p = ROOT / "docs" / "models.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def confirmed_ids(route: str) -> dict:
    return models_file().get("routes", {}).get(route, {}).get("confirmed", {})


def api_key(route: Route) -> str:
    return os.environ.get(route.key_env, "")
