#!/usr/bin/env python3
"""Run the Radio Officer: Telegram long polling, the Officer of the Watch, approvals and email.

Needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env, a model route key, and for the send step RESEND_API_KEY and
RESEND_FROM (Resend is the only sender; Gmail SMTP is not used). Pair once by sending
"/pair CODE" to the bot with the code printed at start. Usage: python scripts/run_radio.py [--once]
"""
from __future__ import annotations

import os
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "core"), str(ROOT / "radio")]

from dogwatch import envload  # noqa: E402

envload.load()

from dogwatch.persona import ARJUN  # noqa: E402
from dogwatch.vault.placeholders import Registry  # noqa: E402
from dogwatch.watch import runner  # noqa: E402
from dogwatch.watch.loop import Watch  # noqa: E402
from dogwatch.watch.state import State  # noqa: E402
from radio import sender  # noqa: E402
from radio.mail import Mailer  # noqa: E402
from radio.telegram import Bot, Pairing, Telegram  # noqa: E402


def main() -> int:
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not tok:
        print("TELEGRAM_BOT_TOKEN is not set")
        return 1
    state_dir = Path(os.environ.get("DOGWATCH_STATE_DIR", Path.home() / ".dogwatch"))
    state_dir.mkdir(parents=True, exist_ok=True)
    st = State(state_dir / "radio.db")
    tg = Telegram(tok)
    pairing = Pairing(st)
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if chat and pairing.paired_chat() is None:
        st.put("paired_chat", int(chat))  # the chat id the owner put in .env is the paired chat
    elif pairing.paired_chat() is None:
        print("pair by sending /pair", pairing.new_code(), "to the bot")
    registry = Registry()
    agent = os.environ.get("TEST_AGENT_EMAIL", "")
    lines = {"Seafarer": registry.assign("NAME", "ARJUN MENON"), "CoC number": registry.assign("COC", "123456/MUM/2019")}
    w = Watch(st, type("N", (), {"tell": lambda s, t, k: tg.send_message(int(chat), t), "post_draft": lambda s, d: None})(),
              lambda: ARJUN, recipient=agent, identifier_lines=lines)
    secret = (os.environ.get("DOGWATCH_VAULT_PASSPHRASE") or "dev-only-secret").encode().ljust(32, b"0")[:32]
    mailer = Mailer()

    def on_approve(draft_id, chat_id):
        token = sender.approve(st, secret, draft_id)
        try:
            res = sender.send_approved(st, secret, draft_id, token, registry, mailer, {agent})
            tg.send_message(chat_id, f"Sent to your agent ({res.get('mode')})." if res.get("sent") else f"Not sent: {res.get('mode')}.")
        except sender.SendRefused as e:
            tg.send_message(chat_id, f"Refused: {e}")

    bot = Bot(tg, pairing, w, on_approve, lambda d, c: (st.set_status(d, "REJECTED"), tg.send_message(c, "Rejected. Nothing was sent.")))
    once = "--once" in sys.argv
    while True:
        bot.poll_once(date.today())
        runner.tick(w)
        if once:
            return 0
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
