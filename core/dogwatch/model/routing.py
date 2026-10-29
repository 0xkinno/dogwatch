"""Which Nemotron handles which job, on the selected route."""
from __future__ import annotations

import os
from dataclasses import dataclass

from .routes import DEFAULT_IDS, confirmed_ids, selected_route

# Role to (size class, thinking, token cap).
ROLES = {
    "triage": ("nano", False, 400),
    "structure": ("super", False, 2000),
    "plan": ("ultra", True, 3000),
    "drift": ("nano", False, 600),
}


@dataclass(frozen=True)
class Route:
    role: str
    size: str
    model: str
    thinking: bool
    max_tokens: int
    confirmed: bool
    route: str
    route_label: str


def route(role: str, route_name: str | None = None) -> Route:
    from .routes import ROUTES

    r = ROUTES[route_name] if route_name else selected_route()
    size, thinking, cap = ROLES[role]
    env = os.environ.get(f"DOGWATCH_MODEL_{size.upper()}")
    probed = confirmed_ids(r.name).get(size)
    model = env or probed or DEFAULT_IDS[r.name][size]
    return Route(role, size, model, thinking, cap, confirmed=bool(env or probed), route=r.name, route_label=r.label)
