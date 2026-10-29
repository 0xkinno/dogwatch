import base64
import json
import urllib.parse
from pathlib import Path

import grpc
import pytest

import seal.gen  # noqa: F401
import supervisor_middleware_pb2 as pb  # type: ignore
import supervisor_middleware_pb2_grpc as pbg  # type: ignore
from seal import normalize
from seal.literal import LiteralGuard
from seal.server import SealService, serve

VALUES = [("PASSPORT", "K1234567"), ("COC", "123456/MUM/2019"), ("NAME", "ARJUN MENON"),
          ("EMAIL", "arjun.menon@seamail.example")]
SALT = b"0" * 16
NEEDLES = normalize.build_needles(VALUES, SALT)


def deny(body: str) -> bool:
    return normalize.check_body(body.encode(), [], NEEDLES).deny


ATTACKS = {
    "literal": "passport K1234567 attached",
    "case": "passport k1234567 attached",
    "fullwidth": "passport Ｋ１２３４５６７ attached",
    "separators": "passport K-123 456.7 attached",
    "zero_width": "passport K12​34567 attached",
    "homoglyph": "passport KI234S67 attached",
    "url": "q=" + urllib.parse.quote("K1234567"),
    "url_double": "q=" + urllib.parse.quote(urllib.parse.quote("123456/MUM/2019")),
    "base64": "blob=" + base64.b64encode(b"my passport is K1234567 ok").decode(),
    "base64url": "blob=" + base64.urlsafe_b64encode(b"passport K1234567 ok??").decode().rstrip("="),
    "hex": "blob=" + b"passport K1234567".hex(),
    "reversed": "7654321K",
    "json_escape": json.dumps({"a": "ARJUN MENON"}),
    "split_fields": json.dumps({"p1": "K12345", "p2": "67"}),
    "nested_b64_in_json": json.dumps({"data": base64.b64encode(b"K1234567 here").decode()}),
    "email_upper": "ARJUN.MENON@SEAMAIL.EXAMPLE",
    "name_spaced": "A R J U N   M E N O N",
}
LEGIT = [
    "Your medical lapses on 14 Mar 2027, day 42 of 181. Book it before joining.",
    json.dumps({"model": "nvidia/nemotron", "messages": [{"role": "user", "content": "classify [[COC_1]] [[PASSPORT_1]]"}]}),
    "revalidation certificate of competency circular DG Shipping India",
    "The contract runs from 2027-02-01 to 2027-07-31 for 181 days.",
    "Regulation I/11 requires revalidation at intervals not exceeding five years.",
]


@pytest.mark.parametrize("name", sorted(ATTACKS))
def test_attack_is_denied(name):
    assert deny(ATTACKS[name]), name


@pytest.mark.parametrize("body", LEGIT)
def test_legitimate_is_allowed(body):
    assert not deny(body)


def test_literal_guard_misses_what_the_seal_catches():
    g = LiteralGuard(VALUES)
    assert g.deny(ATTACKS["literal"].encode())
    missed = [n for n, b in ATTACKS.items() if not g.deny(b.encode())]
    assert len(missed) >= 10
    assert all(deny(ATTACKS[n]) for n in missed)


def test_decision_never_contains_the_value():
    d = normalize.check_body(b"K1234567", [], NEEDLES)
    assert d.deny and d.kind == "PASSPORT" and "K1234567" not in repr(d) and len(d.fp) == 8


def test_query_and_headers_are_scanned():
    assert normalize.check_body(b"{}", ["k1234567"], NEEDLES).deny


def test_short_values_are_ignored():
    n = normalize.build_needles([("X", "ab12")], SALT)
    assert n == []


def test_grpc_describe_and_decisions(tmp_path):
    log = tmp_path / "d.jsonl"
    server, svc, port = serve(VALUES, "127.0.0.1:0", log)
    try:
        ch = grpc.insecure_channel(f"127.0.0.1:{port}")
        stub = pbg.SupervisorMiddlewareStub(ch)
        man = stub.Describe(pb.MiddlewareDescribeRequest())
        assert man.name == "dogwatch-seal" and man.bindings[0].max_payload_bytes == 4 * 1024 * 1024
        assert "openshell.supervisor-middleware.contract" in man.extension.supported_capabilities
        bad = pb.HttpRequestEvaluation(
            phase=pb.SUPERVISOR_MIDDLEWARE_PHASE_PRE_CREDENTIALS, body=b'{"x":"K1234567"}',
            target=pb.HttpRequestTarget(host="evil.example", port=443, method="POST", path="/"),
            context=pb.RequestContext(request_id="r1"))
        r = stub.EvaluateHttpRequest(bad)
        assert r.decision == pb.DECISION_DENY and r.reason_code == "vault_value" and r.reason == "vault_value:PASSPORT"
        ok = pb.HttpRequestEvaluation(
            phase=pb.SUPERVISOR_MIDDLEWARE_PHASE_PRE_CREDENTIALS, body=b'{"x":"hello"}',
            target=pb.HttpRequestTarget(host="api.tokenfactory.nebius.com", port=443, method="POST", path="/v1/chat/completions"))
        assert stub.EvaluateHttpRequest(ok).decision == pb.DECISION_ALLOW
        lines = [json.loads(x) for x in log.read_text().splitlines()]
        assert [x["decision"] for x in lines] == ["deny", "allow"]
        assert "K1234567" not in log.read_text()
    finally:
        server.stop(0)


def test_large_body_under_four_mib_handled():
    body = ("x" * 3_000_000).encode()
    assert not normalize.check_body(body, [], NEEDLES).deny
