import json
from datetime import date
from types import SimpleNamespace

import pytest

from dogwatch.bosun import read as bosun
from dogwatch.bosun.schema import Extraction
from dogwatch.bosun.verify_quote import normalise, parse_date_from_quote, quote_in_text
from dogwatch.model import client, receipts
from dogwatch.vault.placeholders import Registry

SPECIMEN = """SPECIMEN
Medical Fitness Certificate
Issued by: India
CoC No: 123456/MUM/2019
Date of expiry: 14/03/2027
"""


def test_quote_normalisation_whitespace_and_hyphens_only():
    assert quote_in_text("Date  of expiry:\n14/03/2027", SPECIMEN)
    assert quote_in_text("14 - 03", "14-03")
    assert not quote_in_text("Date of expiry: 15/03/2027", SPECIMEN)
    assert not quote_in_text("", SPECIMEN)


def test_date_parse_explicit_formats():
    assert parse_date_from_quote("Date of expiry: 14/03/2027", "india") == date(2027, 3, 14)
    assert parse_date_from_quote("valid until 14 March 2027", "uk") == date(2027, 3, 14)
    assert parse_date_from_quote("2027-03-14", "default") == date(2027, 3, 14)


def test_date_parse_refuses_ambiguity_and_absence():
    assert parse_date_from_quote("issued 01/02/2025 expires 14/03/2027", "india") is None
    assert parse_date_from_quote("no date here", "india") is None


def fake_structure(ex: Extraction):
    return lambda text: ex


def good():
    return Extraction.model_validate({
        "doc_type": "medical", "doc_type_quote": "Medical Fitness Certificate",
        "administration": {"value": "India", "quote": "Issued by: India"},
        "expiry_date": {"value": "14/03/2027", "quote": "Date of expiry: 14/03/2027"},
    })


def test_bosun_reads_and_never_shows_identifier_to_model():
    seen = {}

    def structure(text):
        seen["text"] = text
        return good()

    res = bosun.read_text(SPECIMEN, registry=Registry(), doc_id="medical", administration_hint="india", structure=structure)
    assert "123456" not in seen["text"] and "[[COC_1]]" in seen["text"]
    assert res.document.expiry == date(2027, 3, 14) and not res.document.unread
    assert res.identifiers_replaced == 1


def test_fabricated_quote_is_refused_and_field_unread():
    ex = good()
    ex.expiry_date.quote = "Date of expiry: 14/03/2030"
    res = bosun.read_text(SPECIMEN, registry=Registry(), doc_id="m", administration_hint="india", structure=fake_structure(ex))
    assert res.document.unread and res.document.expiry is None
    assert res.quotes_refused >= 1 and "expiry_date" in res.unread_fields


def test_model_date_field_is_ignored_code_parses_quote():
    ex = good()
    ex.expiry_date.value = "01/01/2099"  # the model's own value is never used
    res = bosun.read_text(SPECIMEN, registry=Registry(), doc_id="m", administration_hint="india", structure=fake_structure(ex))
    assert res.document.expiry == date(2027, 3, 14)


class FakeResp:
    def __init__(self, content):
        self.id = "resp-1"
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]
        self.usage = SimpleNamespace(prompt_tokens=10, completion_tokens=5, completion_tokens_details=None)


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kw):
        self.calls.append(kw)
        return FakeResp(self.replies.pop(0))


def test_structured_repair_retry_and_receipts(tmp_path, monkeypatch):
    monkeypatch.setenv("DOGWATCH_RECEIPTS", str(tmp_path / "r.jsonl"))
    fc = FakeClient(["Sure! not json", "Here you go: " + good().model_dump_json() + " thanks"])
    client.set_client(fc)
    out = client.structured("structure", "sys", "text", Extraction)
    assert out.doc_type == "medical" and len(fc.calls) == 2
    assert fc.calls[0]["extra_body"] == {"chat_template_kwargs": {"enable_thinking": False}}
    rs = receipts.load_all()
    assert len(rs) == 2 and rs[0]["cost_usd"] is None and "text" not in json.dumps(rs)
    client.set_client(None)


def test_structured_gives_up_after_one_repair(monkeypatch, tmp_path):
    monkeypatch.setenv("DOGWATCH_RECEIPTS", str(tmp_path / "r.jsonl"))
    client.set_client(FakeClient(["nope", "still nope"]))
    with pytest.raises(client.ModelOutputInvalid):
        client.structured("structure", "s", "t", Extraction)
    client.set_client(None)


def test_extract_json_handles_braces_in_strings():
    raw = 'prefix {"a": "x } y", "b": {"c": 1}} suffix'
    assert json.loads(client.extract_json(raw)) == {"a": "x } y", "b": {"c": 1}}


def test_no_key_raises_unavailable(monkeypatch):
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    client.set_client(None)
    with pytest.raises(client.ModelUnavailable):
        client.get_client()
