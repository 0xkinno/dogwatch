"""Token Factory client. Inside OpenShell the API key is a placeholder; the gateway injects the real one at egress."""
from __future__ import annotations

import json
import os
import re
import time

from pydantic import BaseModel, ValidationError

from . import receipts
from .routes import ROUTES, api_key, selected_route
from .routing import route


class ModelOutputInvalid(Exception):
    pass


class ModelUnavailable(Exception):
    pass


BASE = ROUTES["tokenfactory"].base_url  # kept for callers that print the submission target

_client = None
_client_route: str | None = None


def get_client():
    """Lazy so that importing this module never needs a key (RECORDED mode, tests). One client per route."""
    global _client, _client_route
    r = selected_route()
    if _client is not None and (_client_route == r.name or _client_route == "injected"):
        return _client
    from openai import OpenAI

    key = api_key(r)
    if not key:
        raise ModelUnavailable(f"{r.key_env} is not set for route {r.name}")
    _client = OpenAI(base_url=r.base_url, api_key=key, timeout=120)
    _client_route = r.name
    return _client


def set_client(c) -> None:
    """Tests and the judge door inject a client here."""
    global _client, _client_route
    _client = c
    _client_route = "injected" if c is not None else None


_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def extract_json(text: str) -> str:
    """First JSON object in a reply that may be wrapped in prose or code fences."""
    text = _CTRL.sub(" ", (text or "").replace("\t", " "))
    start = text.find("{")
    if start < 0:
        return text
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]


def _call(role: str, messages: list[dict], json_schema: dict | None, attempt: int):
    r = route(role)
    kwargs = dict(model=r.model, temperature=0, messages=messages, max_tokens=r.max_tokens,
                  extra_body={"chat_template_kwargs": {"enable_thinking": r.thinking}})
    if json_schema is not None:
        kwargs["response_format"] = {"type": "json_schema", "json_schema": json_schema}
    started = time.time()
    resp = None
    for wait in (0, 4, 10):  # a busy worker (HTTP 503 or 429) is retried; anything else is surfaced
        if wait:
            time.sleep(wait)
        try:
            resp = get_client().chat.completions.create(**kwargs)
            break
        except ModelUnavailable:
            raise
        except Exception as e:  # network or API failure: never swallowed into a made-up answer
            code = getattr(e, "status_code", None)
            if code in (429, 503) and wait != 10:
                continue
            raise ModelUnavailable(f"{type(e).__name__}{'' if code is None else f' HTTP {code}'}") from e
    receipts.record(resp, model=r.model, role=role, attempt=attempt, started=started, route=r.route)
    return resp


def text(role: str, system: str, user: str) -> str:
    resp = _call(role, [{"role": "system", "content": system}, {"role": "user", "content": user}], None, 1)
    return resp.choices[0].message.content or ""


def structured(role: str, system: str, user: str, schema: type[BaseModel]):
    """Validate every reply with Pydantic; one repair retry carries the validation errors."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    js = {"name": schema.__name__, "schema": schema.model_json_schema()}
    last_err = ""
    for attempt in (1, 2):
        resp = _call(role, messages, js, attempt)
        raw = resp.choices[0].message.content or ""
        try:
            return schema.model_validate_json(extract_json(raw))
        except (ValidationError, ValueError, json.JSONDecodeError) as e:
            last_err = str(e)[:400]
            messages = messages + [
                {"role": "assistant", "content": raw[:2000]},
                {"role": "user", "content": f"Your reply failed validation: {last_err}. Reply with JSON only."},
            ]
    raise ModelOutputInvalid(f"{role}: {last_err}")
