"""Judge door API. The same Navigator, Bosun and Lookout code as the product, on the specimen profile.

This host is NOT the sandboxed product: the product runs on the seafarer's machine. Every response carries
its mode (LIVE, RECORDED or DEMO) and every recorded record carries its run id and date.
"""
from __future__ import annotations

import json
import os
import time
from datetime import date
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..model import client, receipts
from ..navigator import engine
from ..navigator.rulepack import load_all
from ..persona import ARJUN, CONTRACT_OFFER, DEMO_TODAY
from ..watch import plan as planner
from ..watch.triage import triage
from .caps import Caps

ROOT = Path(__file__).resolve().parents[3]
STARTED = time.time()


class ReadinessIn(BaseModel):
    start: str = CONTRACT_OFFER["start"]
    end: str = CONTRACT_OFFER["end"]
    travel_before: int = 0
    travel_after: int = 0


class OfferIn(BaseModel):
    text: str = "New contract offer, joining 1 Feb to 31 Jul."


def _results() -> dict:
    out = {}
    d = ROOT / "eval" / "results"
    if d.exists():
        for p in sorted(d.glob("*.json")):
            out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return out


def _probe_model_route() -> dict:
    """A real call to GET /models on the selected route, measured in this process, with a timestamp. Never hard-coded."""
    from ..model.routes import api_key, selected_route

    t0 = time.time()
    try:
        r = selected_route()
    except ValueError as e:
        return {"state": "ERROR", "error": str(e), "checked_at": t0}
    out = {"route": r.name, "route_label": f"Route: {r.label}", "checked_at": t0}
    key = api_key(r)
    if not key:
        return {**out, "state": "NOT_CONFIGURED"}
    try:
        resp = httpx.get(r.base_url.rstrip("/") + "/models", headers={"Authorization": f"Bearer {key}"}, timeout=15)
        ids = [m["id"] for m in resp.json().get("data", [])] if resp.status_code == 200 else []
        return {**out, "state": "UP" if resp.status_code == 200 else "ERROR", "http": resp.status_code,
                "nemotron_models": sorted(i for i in ids if "nemotron" in i.lower()),
                "latency_ms": int((time.time() - t0) * 1000)}
    except httpx.HTTPError as e:
        return {**out, "state": "DOWN", "error": type(e).__name__}


def _probe_tavily() -> dict:
    t0 = time.time()
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return {"state": "NOT_CONFIGURED", "checked_at": t0}
    try:
        r = httpx.post("https://api.tavily.com/search", json={"query": "STCW revalidation", "max_results": 1},
                       headers={"Authorization": f"Bearer {key}"}, timeout=15)
        return {"state": "UP" if r.status_code == 200 else "ERROR", "http": r.status_code,
                "latency_ms": int((time.time() - t0) * 1000), "checked_at": t0}
    except httpx.HTTPError as e:
        return {"state": "DOWN", "error": type(e).__name__, "checked_at": t0}


def create_app(caps: Caps | None = None) -> FastAPI:
    app = FastAPI(title="Dogwatch judge door")
    caps = caps or Caps()
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

    @app.get("/api/status")
    def status():
        mode = os.environ.get("DOGWATCH_MODE", "RECORDED")
        return {
            "mode": mode,
            "host": os.environ.get("DOGWATCH_HOST_LABEL", "API host (substitute; the product itself runs on the seafarer's machine)"),
            "sandboxed": False,
            "model_route": _probe_model_route(),
            "tavily": _probe_tavily(),
            "kill_switch": caps.killed(),
            "caps": caps.describe(),
            "rule_packs": {k: {"rules": len(p.rules), "status": p.status, "sha256": p.sha256} for k, p in load_all().items()},
            "uptime_s": int(time.time() - STARTED),
            "now": time.time(),
        }

    @app.post("/api/readiness")
    def readiness(body: ReadinessIn):
        """Pure code, no model, so it is not capped as a live model run."""
        try:
            res = engine.run_readiness(ARJUN, body.model_dump(), date.fromisoformat(DEMO_TODAY))
        except ValueError as e:
            raise HTTPException(422, str(e)) from e
        return {"mode": "LIVE", "model_used": False, "specimen": True, "result": res}

    @app.post("/api/demo/offer")
    def demo_offer(body: OfferIn, request: Request):
        """The Telegram offer flow in the browser. Same code path: triage, Navigator, plan writer."""
        addr = request.client.host if request.client else "?"
        browser = request.headers.get("x-browser-id", addr)
        ok, why = caps.acquire(addr, browser)
        if not ok:
            raise HTTPException(429, why)
        try:
            from ..watch.loop import parse_offer_window
            t = triage(body.text)
            win = parse_offer_window(body.text, date.fromisoformat(DEMO_TODAY))
            if t["label"] != "contract_offer" or win is None:
                return {"mode": "DEMO", "triage": t, "reply": "I need the start and end dates of the offered contract.", "result": None}
            res = engine.run_readiness(ARJUN, {**CONTRACT_OFFER, "start": win[0].isoformat(), "end": win[1].isoformat()},
                                       date.fromisoformat(DEMO_TODAY))
            pl = planner.write_plan(res)
            from ..model.routes import selected_route
            r = selected_route()
            return {"mode": "DEMO", "triage": t, "reply": f"{res['summary']} {pl['text']}", "plan_source": pl["source"], "result": res,
                    "route_label": f"Route: {r.label}", "caps": caps.describe()}
        finally:
            caps.release(browser)

    @app.get("/api/boundary")
    def boundary():
        d = ROOT / "evidence"
        recs = {}
        for sub in ("boundary", "prover"):
            p = d / sub
            if p.exists():
                recs[sub] = {f.name: f.read_text(encoding="utf-8")[:6000] for f in sorted(p.iterdir()) if f.is_file() and f.name != ".gitkeep"}
        policy = ROOT / "openshell" / "policy" / "dogwatch.yaml"
        return {"mode": "RECORDED" if any(recs.values()) else "NOT_RUN",
                "note": "Evidence from runs on the seafarer machine, labelled with run id and date inside each file.",
                "policy": policy.read_text(encoding="utf-8") if policy.exists() else "",
                "records": recs}

    @app.get("/api/stats")
    def stats():
        import importlib.util
        spec = importlib.util.spec_from_file_location("facts", ROOT / "scripts" / "facts.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.build()

    @app.get("/api/proof/{name}")
    def proof(name: str):
        res = _results()
        if name not in res:
            raise HTTPException(404, f"no result set {name}; available: {sorted(res)}")
        r = res[name]
        # misses first
        cases = r.get("cases")
        if isinstance(cases, list):
            r = {**r, "cases": sorted(cases, key=lambda c: (c.get("ok", True) is True, c.get("flip", False) is False, c.get("id", "")))}
        return {"mode": "RECORDED", "name": name, "result": r}

    @app.get("/api/receipts")
    def get_receipts():
        rs = receipts.load_all()
        return {"count": len(rs), "receipts": rs[-50:]}

    return app


app = create_app()
