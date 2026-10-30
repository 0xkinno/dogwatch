"""Telegram Bot API over httpx, long polling. Answers only the chat paired at setup."""
from __future__ import annotations

import json
import secrets
from datetime import date

import httpx

API = "https://api.telegram.org"


class Telegram:
    def __init__(self, token: str, transport: httpx.BaseTransport | None = None):
        self.token = token
        self.http = httpx.Client(transport=transport, timeout=60)

    def _call(self, method: str, **params):
        files = params.pop("files", None)
        r = self.http.post(f"{API}/bot{self.token}/{method}", data=params, files=files)
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"telegram {method} failed: {data.get('description', r.status_code)}")
        return data["result"]

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[dict]:
        p = {"timeout": timeout, "allowed_updates": json.dumps(["message", "callback_query"])}
        if offset is not None:
            p["offset"] = offset
        return self._call("getUpdates", **p)

    def send_message(self, chat_id: int, text: str, buttons: list[tuple[str, str]] | None = None):
        p = {"chat_id": chat_id, "text": text}
        if buttons:
            p["reply_markup"] = json.dumps({"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in buttons]]})
        return self._call("sendMessage", **p)

    def send_document(self, chat_id: int, filename: str, content: bytes, caption: str = ""):
        return self._call("sendDocument", chat_id=chat_id, caption=caption, files={"document": (filename, content)})

    def send_photo(self, chat_id: int, filename: str, content: bytes, caption: str = ""):
        return self._call("sendPhoto", chat_id=chat_id, caption=caption, files={"photo": (filename, content)})

    def answer_callback(self, callback_id: str, text: str = ""):
        return self._call("answerCallbackQuery", callback_query_id=callback_id, text=text)

    def download_photo(self, file_id: str) -> bytes:
        info = self._call("getFile", file_id=file_id)
        r = self.http.get(f"{API}/file/bot{self.token}/{info['file_path']}")
        r.raise_for_status()
        return r.content


class Pairing:
    """A one-time code shown in the local UI. Until it is sent from the phone, no chat is trusted."""

    def __init__(self, state):
        self.state = state

    def new_code(self) -> str:
        code = secrets.token_hex(3)
        self.state.put("pairing_code", code)
        return code

    def paired_chat(self) -> int | None:
        return self.state.get("paired_chat")

    def try_pair(self, chat_id: int, text: str) -> bool:
        code = self.state.get("pairing_code")
        if code and text.strip() == f"/pair {code}":
            self.state.put("paired_chat", chat_id)
            self.state.put("pairing_code", None)
            return True
        return False


class Bot:
    """Wires Telegram updates to the Officer of the Watch and the approval flow."""

    def __init__(self, tg: Telegram, pairing: Pairing, watch, on_approve, on_reject, on_photo=None):
        self.tg, self.pairing, self.watch = tg, pairing, watch
        self.on_approve, self.on_reject, self.on_photo = on_approve, on_reject, on_photo
        self.offset: int | None = None

    def handle(self, update: dict, today: date) -> str:
        """Returns a short label of what happened, for the trace."""
        msg = update.get("message")
        cb = update.get("callback_query")
        chat = (msg or cb["message"])["chat"]["id"] if (msg or cb) else None
        paired = self.pairing.paired_chat()
        if paired is None:
            if msg and msg.get("text") and self.pairing.try_pair(chat, msg["text"]):
                self.tg.send_message(chat, "Paired. Dogwatch is watching.")
                return "paired"
            return "ignored_unpaired"
        if chat != paired:
            return "ignored_other_chat"
        if cb:
            action, _, draft_id = cb["data"].partition(":")
            self.tg.answer_callback(cb["id"])
            if action == "approve":
                self.on_approve(draft_id, chat)
                return "approved"
            self.on_reject(draft_id, chat)
            return "rejected"
        if msg.get("photo"):
            if self.on_photo:
                self.on_photo(self.tg.download_photo(msg["photo"][-1]["file_id"]), chat)
            self.tg.send_message(chat, "Photo stored in your vault on this machine.")
            return "photo"
        out = self.watch.on_message(msg.get("text", ""), today=today)
        if out.get("reply"):
            buttons = None
            if out.get("draft_id"):
                buttons = [("Approve", f"approve:{out['draft_id']}"), ("Reject", f"reject:{out['draft_id']}")]
            self.tg.send_message(chat, out["reply"], buttons)
        return out["label"]

    def poll_once(self, today: date) -> list[str]:
        labels = []
        for u in self.tg.get_updates(self.offset, timeout=25):
            self.offset = u["update_id"] + 1
            labels.append(self.handle(u, today))
        return labels
