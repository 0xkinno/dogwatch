"""Token Factory client. Inside OpenShell the API key is a placeholder; the gateway injects the real one at egress."""
from __future__ import annotations

import json
import os
import re
import time

from pydantic import BaseModel, ValidationError

from . import receipts
from .routing import route


class ModelOutputInvalid(Exception):
    pass


class ModelUnavailable(Exception):
    pass


BASE = os.environ.get("TOKEN_FACTORY_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")

_client = None


def get_client():
    """Lazy so that importing this module never needs a key (RECORDED mode, tests)."""
    global _client
    if _client is None:
        from openai import OpenAI

        key = os.environ.get("NEBIUS_API_KEY")
        if not key:
            raise ModelUnavailable("NEBIUS_API_KEY is not set")
        _client = OpenAI(base_url=BASE, api_key=key, timeout=120)
    return _client


def set_client(c) -> None:
    """Tests and the judge door inject a client here."""
    global _client
    _client = c


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
    try:
        resp = get_client().chat.completions.create(**kwargs)
    except ModelUnavailable:
        raise
    except Exception as e:  # network or API failure: never swallowed into a made-up answer
        raise ModelUnavailable(f"{type(e).__name__}") from e
    receipts.record(resp, model=r.model, role=role, attempt=attempt, started=started)
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
