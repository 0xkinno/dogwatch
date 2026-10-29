import httpx
import pytest

from dogwatch.lookout import drift
from dogwatch.lookout.drift import Judgement
from dogwatch.lookout.tavily import Tavily, TavilyUnavailable
from dogwatch.watch.state import State

PAGE = "Circular. Revalidation of certificates must be applied for within the stated period."


class Fake(httpx.BaseTransport):
    def __init__(self, results=None, fail=False):
        self.results = results if results is not None else []
        self.fail = fail
        self.bodies = []

    def handle_request(self, request):
        import json
        body = json.loads(request.content)
        self.bodies.append((request.url.path, body))
        if self.fail:
            return httpx.Response(500, json={})
        if request.url.path == "/search":
            return httpx.Response(200, json={"results": self.results})
        return httpx.Response(200, json={"results": [{"url": body["urls"][0], "raw_content": PAGE}]})


def test_unavailable_is_never_no_change(tmp_path):
    t = Tavily("k", Fake(fail=True))
    rep = drift.run(t, State(tmp_path / "s.db"), admins=["au-amsa"])
    assert rep.status == "DRIFT_UNAVAILABLE"


def test_missing_key_is_unavailable(tmp_path):
    rep = drift.run(Tavily("", Fake()), State(tmp_path / "s.db"), admins=["au-amsa"])
    assert rep.status == "DRIFT_UNAVAILABLE"


def test_gates_domain_keyword_quote_and_review_item(tmp_path):
    res = [{"url": "https://www.amsa.gov.au/a"}, {"url": "https://evil.example/b"}]
    fake = Fake(res)
    t = Tavily("k", fake)
    st = State(tmp_path / "s.db")
    good = lambda page: Judgement(label="new_rule_text", quote="Revalidation of certificates must be applied for")
    rep = drift.run(t, st, classify=good, admins=["au-amsa"])
    assert rep.status == "OK" and rep.gates.off_domain >= 1
    assert rep.items and rep.items[0]["administration"] == "au-amsa"
    bad = lambda page: Judgement(label="new_rule_text", quote="a sentence that is not on the page")
    st2 = State(tmp_path / "s2.db")
    rep2 = drift.run(Tavily("k", Fake(res)), st2, classify=bad, admins=["au-amsa"])
    assert rep2.items == [] and rep2.gates.quote_refused >= 1


def test_seen_pages_are_not_reread(tmp_path):
    st = State(tmp_path / "s.db")
    cls = lambda page: Judgement(label="same_as_pack")
    res = [{"url": "https://www.amsa.gov.au/a"}]
    drift.run(Tavily("k", Fake(res)), st, classify=cls, admins=["au-amsa"])
    rep = drift.run(Tavily("k", Fake(res)), st, classify=cls, admins=["au-amsa"])
    assert rep.gates.already_seen >= 1 and rep.gates.classified == 0


def test_no_vault_value_or_placeholder_in_any_tavily_request(tmp_path):
    fake = Fake([{"url": "https://www.amsa.gov.au/a"}])
    t = Tavily("k", fake)
    drift.run(t, State(tmp_path / "s.db"), classify=lambda p: Judgement(label="unrelated"))
    blob = str(t.log).lower()
    for forbidden in ("[[", "arjun", "menon", "k1234567", "123456"):
        assert forbidden not in blob
    assert all(set(b) <= {"query", "include_domains", "max_results", "urls"} for _, b in fake.bodies)


def test_on_domain():
    assert drift.on_domain("https://www.amsa.gov.au/x", ["amsa.gov.au"])
    assert not drift.on_domain("https://amsa.gov.au.evil.example/x", ["amsa.gov.au"])
