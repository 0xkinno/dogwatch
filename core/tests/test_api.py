from fastapi.testclient import TestClient

from dogwatch.api.app import create_app
from dogwatch.api.caps import Caps


def client(caps=None):
    return TestClient(create_app(caps))


def test_status_is_measured_not_hardcoded(monkeypatch):
    for k in ("NEBIUS_API_KEY", "NVIDIA_API_KEY", "TAVILY_API_KEY", "MODEL_ROUTE"):
        monkeypatch.delenv(k, raising=False)
    s = client().get("/api/status").json()
    assert s["model_route"]["state"] == "NOT_CONFIGURED" and s["tavily"]["state"] == "NOT_CONFIGURED"
    assert s["model_route"]["route_label"] == "Route: NVIDIA API Catalog (development)"
    assert s["sandboxed"] is False and "substitute" in s["host"]
    assert s["rule_packs"]["in-dgs"]["status"] == "sourced" and s["rule_packs"]["ng-nimasa"]["status"] == "unsourced"


def test_readiness_arjun_day_42():
    r = client().post("/api/readiness", json={}).json()
    assert r["result"]["overall"] == "NOT_READY" and "day 42 of 181" in r["result"]["summary"] and r["model_used"] is False


def test_readiness_rejects_bad_date():
    assert client().post("/api/readiness", json={"start": "nope"}).status_code == 422


def test_demo_offer_uses_same_path_and_is_labelled():
    r = client().post("/api/demo/offer", json={"text": "New contract offer, joining 1 Feb to 31 Jul."}).json()
    assert r["mode"] == "DEMO" and r["result"]["overall"] == "NOT_READY"


def test_demo_offer_asks_when_dates_missing():
    r = client().post("/api/demo/offer", json={"text": "a contract offer for six months"}).json()
    assert r["result"] is None and "dates" in r["reply"]


def test_caps_hourly_and_kill_switch(monkeypatch):
    c = Caps(per_hour=2, per_day=60)
    assert c.acquire("a", "b1", 0)[0]
    c.release("b1")
    assert c.acquire("a", "b2", 1)[0]
    c.release("b2")
    ok, why = c.acquire("a", "b3", 2)
    assert not ok and "per hour" in why
    assert c.acquire("a", "b3", 4000)[0]
    monkeypatch.setenv("DOGWATCH_KILL", "1")
    ok, why = c.acquire("z", "q")
    assert not ok and "switched off" in why


def test_one_run_at_a_time_per_browser():
    c = Caps()
    assert c.acquire("a", "same", 0)[0]
    assert not c.acquire("a", "same", 1)[0]
    c.release("same")
    assert c.acquire("a", "same", 2)[0]


def test_daily_cap():
    c = Caps(per_hour=100, per_day=2)
    assert c.acquire("a", "1", 0)[0] and c.acquire("b", "2", 1)[0]
    assert "Daily limit" in c.acquire("c", "3", 2)[1]


def test_proof_lists_misses_first_and_404s():
    c = client()
    assert c.get("/api/proof/nope").status_code == 404
    r = c.get("/api/proof/p7_conventions").json()
    assert r["mode"] == "RECORDED" and r["result"]["cases"][0]["flip"] is True


def test_stats_recomputed_from_results():
    s = client().get("/api/stats").json()["facts"]
    assert s["p3.attacks"]["value"] == 200 and s["need.ilo_wage"]["value"] == 704


def test_boundary_labels_not_run_without_evidence():
    r = client().get("/api/boundary").json()
    assert r["mode"] in ("NOT_RUN", "RECORDED") and "network_policies" in r["policy"]
