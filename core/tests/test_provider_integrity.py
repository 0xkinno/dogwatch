"""Only two model hosts are allowed. OpenRouter and any other inference host are forbidden."""
import os
import re
from pathlib import Path

import pytest

from dogwatch.model import client
from dogwatch.model.routes import ALLOWED_HOSTS, ROUTES, selected_route

ROOT = Path(__file__).resolve().parents[2]
SCAN = [ROOT / "core" / "dogwatch", ROOT / "radio" / "radio", ROOT / "seal" / "seal", ROOT / "eval", ROOT / "scripts", ROOT / "openshell"]
SKIP_PARTS = {"gen", "__pycache__", "results", "cases"}
INFERENCE_HINTS = ("openrouter", "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com", "api.together", "api.groq", "api.mistral", "api.deepseek")


def files():
    for base in SCAN:
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in {".py", ".yaml", ".yml", ".sh", ".json"} and not (set(p.parts) & SKIP_PARTS):
                yield p


def test_exactly_two_allowed_hosts():
    assert ALLOWED_HOSTS == {"api.tokenfactory.nebius.com", "integrate.api.nvidia.com"}
    assert set(ROUTES) == {"tokenfactory", "nvidia_build"}


def test_no_other_inference_host_anywhere():
    me = Path(__file__).resolve()
    bad = []
    for p in files():
        if p == me:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore").lower()
        for h in INFERENCE_HINTS:
            if h in text:
                bad.append(f"{p.relative_to(ROOT)}: {h}")
    assert bad == []


def test_model_package_urls_are_allowed():
    for p in (ROOT / "core" / "dogwatch" / "model").glob("*.py"):
        for host in re.findall(r"https?://([a-z0-9.\-]+)", p.read_text(encoding="utf-8")):
            assert host in ALLOWED_HOSTS, f"{p.name}: {host}"


def test_route_selection(monkeypatch):
    for k in ("NEBIUS_API_KEY", "NVIDIA_API_KEY", "MODEL_ROUTE"):
        monkeypatch.delenv(k, raising=False)
    assert selected_route().name == "nvidia_build"
    monkeypatch.setenv("NEBIUS_API_KEY", "x")
    assert selected_route().name == "tokenfactory"
    monkeypatch.setenv("MODEL_ROUTE", "nvidia_build")
    assert selected_route().name == "nvidia_build"
    monkeypatch.setenv("MODEL_ROUTE", "openrouter")
    with pytest.raises(ValueError):
        selected_route()


def test_client_uses_the_selected_routes_host_and_key(monkeypatch):
    client.set_client(None)
    monkeypatch.setenv("MODEL_ROUTE", "nvidia_build")
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test")
    c = client.get_client()
    assert "integrate.api.nvidia.com" in str(c.base_url)
    client.set_client(None)
    monkeypatch.setenv("MODEL_ROUTE", "tokenfactory")
    monkeypatch.setenv("NEBIUS_API_KEY", "n-test")
    assert "api.tokenfactory.nebius.com" in str(client.get_client().base_url)
    client.set_client(None)


def test_missing_key_names_the_route(monkeypatch):
    client.set_client(None)
    monkeypatch.setenv("MODEL_ROUTE", "tokenfactory")
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    with pytest.raises(client.ModelUnavailable, match="NEBIUS_API_KEY"):
        client.get_client()
