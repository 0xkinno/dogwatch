import json
from datetime import date

import httpx
import pytest

from dogwatch.navigator import engine
from dogwatch.outbox.digest import digest
from dogwatch.outbox.packet import build_packet
from dogwatch.persona import ARJUN, CONTRACT_OFFER
from dogwatch.vault.placeholders import Registry
from dogwatch.watch import plan as planner
from dogwatch.watch.state import State
from radio import approvals, sender
from radio.ics import booking_ics
from radio.mail import Mailer, redact
from radio.rehydrate import build_pdf, packet_text
from radio.server import create_app
from radio.telegram import Bot, Pairing, Telegram

SECRET = b"s" * 32
TODAY = date(2026, 10, 28)
AGENT = "agent@example.test"


def setup(tmp_path):
    reg = Registry()
    name, coc = reg.assign("NAME", "ARJUN MENON"), reg.assign("COC", "123456/MUM/2019")
    res = engine.run_readiness(ARJUN, CONTRACT_OFFER, TODAY)
    pl = planner.write_plan(res, writer=lambda s, u: (_ for _ in ()).throw(Exception()) if False else "Your {{V1}} lapses on {{V2}}.")
    pk = build_packet(res, pl, identifier_lines={"Seafarer": name, "CoC number": coc}, recipient=AGENT)
    st = State(tmp_path / "s.db")
    st.add_draft("d1", pk["digest"], pk, "idem-1")
    return st, reg, pk


class Capture(httpx.BaseTransport):
    def __init__(self):
        self.requests = []

    def handle_request(self, request):
        self.requests.append(request)
        return httpx.Response(200, json={"id": "em_1"})


def test_token_bound_to_digest_single_use_and_expiry(tmp_path):
    st, reg, pk = setup(tmp_path)
    tok = approvals.issue(SECRET, "d1", pk["digest"])
    approvals.verify(SECRET, tok, "d1", pk["digest"], st)
    with pytest.raises(approvals.ApprovalError, match="already used"):
        approvals.verify(SECRET, tok, "d1", pk["digest"], st)
    tok2 = approvals.issue(SECRET, "d1", pk["digest"])
    with pytest.raises(approvals.ApprovalError, match="digest mismatch"):
        approvals.verify(SECRET, tok2, "d1", "0" * 64, st)
    tok3 = approvals.issue(SECRET, "d1", pk["digest"], now=1000.0)
    with pytest.raises(approvals.ApprovalError, match="expired"):
        approvals.verify(SECRET, tok3, "d1", pk["digest"], st)
    with pytest.raises(approvals.ApprovalError, match="bad signature"):
        approvals.verify(b"x" * 32, approvals.issue(SECRET, "d1", pk["digest"]), "d1", pk["digest"], st)


def test_send_rehydrates_once_and_records_redacted(tmp_path):
    st, reg, pk = setup(tmp_path)
    cap = Capture()
    mailer = Mailer("key", "dogwatch@example.test", transport=cap)
    tok = sender.approve(st, SECRET, "d1")
    res = sender.send_approved(st, SECRET, "d1", tok, reg, mailer, {AGENT}, tmp_path / "ev")
    assert res["sent"] and st.draft("d1")["status"] == "SENT"
    body = json.loads(cap.requests[0].content)
    assert "ARJUN MENON" in body["text"] and "123456/MUM/2019" in body["text"]
    assert cap.requests[0].headers["idempotency-key"] == "idem-1"
    rec = next((tmp_path / "ev").iterdir()).read_text()
    assert AGENT not in rec and "a***@e***.test" in rec
    # second approval attempt cannot send again
    again = sender.send_approved(st, SECRET, "d1", tok, reg, mailer, {AGENT}, tmp_path / "ev")
    assert again["mode"] == "DUPLICATE_SUPPRESSED" and len(cap.requests) == 1


def test_unlisted_recipient_refused(tmp_path):
    st, reg, pk = setup(tmp_path)
    tok = sender.approve(st, SECRET, "d1")
    with pytest.raises(sender.SendRefused, match="allowlist"):
        sender.send_approved(st, SECRET, "d1", tok, reg, Mailer("k", "f@x.test", transport=Capture()), {"someone@else.test"})


def test_tampered_packet_after_approval_refused(tmp_path):
    st, reg, pk = setup(tmp_path)
    tok = sender.approve(st, SECRET, "d1")
    pk2 = json.loads(json.dumps(pk))
    pk2["packet"]["summary"] = "Ready: all good"
    st.db.execute("UPDATE drafts SET payload=? WHERE id='d1'", (json.dumps(pk2),))
    with pytest.raises(sender.SendRefused, match="digest mismatch"):
        sender.send_approved(st, SECRET, "d1", tok, reg, Mailer("k", "f@x.test", transport=Capture()), {AGENT})


def test_unconfigured_mailer_says_so_and_keeps_draft_approved(tmp_path):
    st, reg, pk = setup(tmp_path)
    tok = sender.approve(st, SECRET, "d1")
    res = sender.send_approved(st, SECRET, "d1", tok, reg, Mailer("", ""), {AGENT})
    assert res == {"sent": False, "mode": "NOT_CONFIGURED"} and st.draft("d1")["status"] == "APPROVED"


def test_restart_between_approval_and_send_no_duplicate(tmp_path):
    st, reg, pk = setup(tmp_path)
    tok = sender.approve(st, SECRET, "d1")
    st.close()
    st2 = State(tmp_path / "s.db")
    cap = Capture()
    m = Mailer("k", "f@x.test", transport=cap)
    assert sender.send_approved(st2, SECRET, "d1", tok, reg, m, {AGENT})["sent"]
    assert sender.send_approved(st2, SECRET, "d1", tok, reg, m, {AGENT})["mode"] == "DUPLICATE_SUPPRESSED"
    assert len(cap.requests) == 1


def test_pdf_contains_real_values_only_after_rehydration(tmp_path):
    st, reg, pk = setup(tmp_path)
    assert "123456" not in str(pk) and "ARJUN" not in str(pk)
    assert "ARJUN MENON" in packet_text(pk["packet"], reg)
    assert build_pdf(pk["packet"], reg)[:4] == b"%PDF"


def test_ics_booking_window():
    ics = booking_ics("Book medical", date(2026, 11, 1), date(2026, 12, 15), "before joining").decode()
    assert "DTSTART;VALUE=DATE:20261101" in ics and "DTEND;VALUE=DATE:20261216" in ics and ics.endswith("\r\n")


def test_redact():
    assert redact("agent@example.test") == "a***@e***.test"


def test_server_refuses_draft_with_vault_value_and_returns_placeholder_only(tmp_path):
    from fastapi.testclient import TestClient
    st, reg, pk = setup(tmp_path)
    c = TestClient(create_app(st, reg))
    r = c.post("/vault/identifiers", json={"kind": "PASSPORT", "value": "K1234567"})
    assert r.json() == {"placeholder": "[[PASSPORT_1]]"}
    bad = json.loads(json.dumps(pk))
    bad["packet"]["summary"] = "passport K1234567"
    bad["digest"] = digest(bad["packet"], bad["recipients"], bad["attachments"])
    assert c.post("/drafts", json=bad).status_code == 422
    ok = c.post("/drafts", json=pk)
    assert ok.status_code == 200
    mismatch = json.loads(json.dumps(pk))
    mismatch["digest"] = "0" * 64
    assert c.post("/drafts", json=mismatch).status_code == 422


class TgFake(httpx.BaseTransport):
    def __init__(self):
        self.sent = []

    def handle_request(self, request):
        from urllib.parse import unquote_plus
        self.sent.append((request.url.path.rsplit("/", 1)[-1], unquote_plus(request.content.decode(errors="ignore"))))
        return httpx.Response(200, json={"ok": True, "result": []})


class FakeWatch:
    def on_message(self, text, today):
        return {"label": "contract_offer", "reply": "Not ready. Approve?", "draft_id": "d1"}


def test_bot_pairs_then_ignores_other_chats(tmp_path):
    st = State(tmp_path / "t.db")
    pairing = Pairing(st)
    code = pairing.new_code()
    tf = TgFake()
    approved, rejected = [], []
    bot = Bot(Telegram("tok", tf), pairing, FakeWatch(), lambda d, c: approved.append(d), lambda d, c: rejected.append(d))
    msg = lambda chat, text: {"message": {"chat": {"id": chat}, "text": text}}
    assert bot.handle(msg(7, "hello"), TODAY) == "ignored_unpaired"
    assert bot.handle(msg(7, f"/pair {code}"), TODAY) == "paired"
    assert pairing.paired_chat() == 7
    assert bot.handle(msg(99, "send passport"), TODAY) == "ignored_other_chat"
    assert bot.handle(msg(7, "offer 1 Feb to 31 Jul"), TODAY) == "contract_offer"
    assert any(m == "sendMessage" and "approve:d1" in body for m, body in tf.sent)
    cb = {"callback_query": {"id": "c1", "data": "approve:d1", "message": {"chat": {"id": 7}}}}
    assert bot.handle(cb, TODAY) == "approved" and approved == ["d1"]
    cb2 = {"callback_query": {"id": "c2", "data": "reject:d1", "message": {"chat": {"id": 7}}}}
    assert bot.handle(cb2, TODAY) == "rejected" and rejected == ["d1"]
    cb3 = {"callback_query": {"id": "c3", "data": "approve:d1", "message": {"chat": {"id": 99}}}}
    assert bot.handle(cb3, TODAY) == "ignored_other_chat" and approved == ["d1"]
