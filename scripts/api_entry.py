"""Vercel entry point for the judge door API (copied to api/index.py by scripts/assemble_api.py).

Vercel hands a rewritten request to the function with the rewrite target as its path, so the public path travels in the
query string (`__p`) and is restored here before the FastAPI app routes it.
"""
import sys
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "core"))
from dogwatch.api.app import app as _app  # noqa: E402


async def app(scope, receive, send):
    if scope["type"] == "http":
        pairs = parse_qsl(scope.get("query_string", b"").decode(), keep_blank_values=True)
        orig = next((v for k, v in pairs if k == "__p"), None)
        if orig is not None:
            rest = [(k, v) for k, v in pairs if k != "__p"]
            path = unquote(orig) or "/"
            scope = dict(scope, path=path, raw_path=path.encode(), query_string=urlencode(rest).encode())
    await _app(scope, receive, send)
