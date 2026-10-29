"""Tavily Search and Extract. Queries are built by code from rule topics; no vault value ever goes in one."""
from __future__ import annotations

import os

import httpx

BASE = "https://api.tavily.com"


class TavilyUnavailable(Exception):
    pass


class Tavily:
    def __init__(self, api_key: str | None = None, transport: httpx.BaseTransport | None = None):
        # Inside OpenShell this is a placeholder; the gateway injects the real key at egress.
        self.api_key = api_key if api_key is not None else os.environ.get("TAVILY_API_KEY", "")
        self.http = httpx.Client(transport=transport, timeout=60)
        self.log: list[dict] = []  # every request body, for the no-leak test

    def _post(self, path: str, body: dict) -> dict:
        if not self.api_key:
            raise TavilyUnavailable("TAVILY_API_KEY is not set")
        self.log.append({"path": path, "body": body})
        try:
            r = self.http.post(f"{BASE}{path}", json=body, headers={"Authorization": f"Bearer {self.api_key}"})
        except httpx.HTTPError as e:
            raise TavilyUnavailable(type(e).__name__) from e
        if r.status_code != 200:
            raise TavilyUnavailable(f"HTTP {r.status_code}")
        return r.json()

    def search(self, query: str, include_domains: list[str], max_results: int = 5) -> list[dict]:
        out = self._post("/search", {"query": query, "include_domains": include_domains, "max_results": max_results})
        return out.get("results", [])

    def extract(self, urls: list[str]) -> list[dict]:
        out = self._post("/extract", {"urls": urls})
        return out.get("results", [])
