"""Durable state for the always-on loop: SQLite, so a restart resumes pending approvals.

Holds drafts that contain placeholders only, digests, statuses and counters. No identifier value is stored here.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


class State:
    def __init__(self, path: Path | str):
        self.path = str(path)
        self.db = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS drafts (
              id TEXT PRIMARY KEY, digest TEXT NOT NULL, status TEXT NOT NULL,
              payload TEXT NOT NULL, created REAL NOT NULL, sent_at REAL, idempotency_key TEXT UNIQUE);
            CREATE TABLE IF NOT EXISTS events (day TEXT NOT NULL, kind TEXT NOT NULL, n INTEGER NOT NULL,
              PRIMARY KEY (day, kind));
            CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, started REAL,
              finished REAL, summary TEXT);
            CREATE TABLE IF NOT EXISTS used_tokens (token_id TEXT PRIMARY KEY, used_at REAL NOT NULL);
            """
        )

    def close(self) -> None:
        self.db.close()

    # key value
    def get(self, k: str, default=None):
        row = self.db.execute("SELECT v FROM kv WHERE k=?", (k,)).fetchone()
        return json.loads(row[0]) if row else default

    def put(self, k: str, v) -> None:
        self.db.execute("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, json.dumps(v)))

    # interruption counters
    def event_count(self, day: str, kind: str) -> int:
        row = self.db.execute("SELECT n FROM events WHERE day=? AND kind=?", (day, kind)).fetchone()
        return row[0] if row else 0

    def count_event(self, day: str, kind: str) -> None:
        self.db.execute(
            "INSERT INTO events(day,kind,n) VALUES(?,?,1) ON CONFLICT(day,kind) DO UPDATE SET n=n+1", (day, kind))

    # drafts
    def add_draft(self, draft_id: str, digest: str, payload: dict, idempotency_key: str) -> bool:
        """False if this idempotency key already exists (no duplicate draft)."""
        try:
            self.db.execute(
                "INSERT INTO drafts(id,digest,status,payload,created,idempotency_key) VALUES(?,?,?,?,?,?)",
                (draft_id, digest, "PENDING", json.dumps(payload), time.time(), idempotency_key))
            return True
        except sqlite3.IntegrityError:
            return False

    def draft(self, draft_id: str) -> dict | None:
        row = self.db.execute(
            "SELECT id,digest,status,payload,created,sent_at,idempotency_key FROM drafts WHERE id=?", (draft_id,)
        ).fetchone()
        if not row:
            return None
        return {"id": row[0], "digest": row[1], "status": row[2], "payload": json.loads(row[3]),
                "created": row[4], "sent_at": row[5], "idempotency_key": row[6]}

    def pending_drafts(self) -> list[dict]:
        ids = [r[0] for r in self.db.execute("SELECT id FROM drafts WHERE status IN ('PENDING','APPROVED','SENDING') ORDER BY created")]
        return [self.draft(i) for i in ids]

    def set_status(self, draft_id: str, status: str) -> None:
        sent = time.time() if status == "SENT" else None
        self.db.execute("UPDATE drafts SET status=?, sent_at=COALESCE(?, sent_at) WHERE id=?", (status, sent, draft_id))

    def mark_sent_once(self, draft_id: str) -> bool:
        """Atomic: only the first caller moves APPROVED to SENT. A second send attempt gets False."""
        cur = self.db.execute(
            "UPDATE drafts SET status='SENT', sent_at=? WHERE id=? AND status='APPROVED'", (time.time(), draft_id))
        return cur.rowcount == 1

    def claim_send(self, draft_id: str) -> bool:
        """Atomic: only the first caller moves APPROVED to SENDING."""
        cur = self.db.execute("UPDATE drafts SET status='SENDING' WHERE id=? AND status='APPROVED'", (draft_id,))
        return cur.rowcount == 1

    def complete_send(self, draft_id: str) -> None:
        self.db.execute("UPDATE drafts SET status='SENT', sent_at=? WHERE id=? AND status='SENDING'", (time.time(), draft_id))

    def release_send(self, draft_id: str) -> None:
        self.db.execute("UPDATE drafts SET status='APPROVED' WHERE id=? AND status='SENDING'", (draft_id,))

    # token single use
    def use_token(self, token_id: str) -> bool:
        try:
            self.db.execute("INSERT INTO used_tokens(token_id,used_at) VALUES(?,?)", (token_id, time.time()))
            return True
        except sqlite3.IntegrityError:
            return False

    # runs
    def start_run(self, kind: str) -> int:
        cur = self.db.execute("INSERT INTO runs(kind,started) VALUES(?,?)", (kind, time.time()))
        return cur.lastrowid

    def finish_run(self, run_id: int, summary: dict) -> None:
        self.db.execute("UPDATE runs SET finished=?, summary=? WHERE id=?", (time.time(), json.dumps(summary), run_id))

    def runs(self) -> list[dict]:
        return [{"id": r[0], "kind": r[1], "started": r[2], "finished": r[3], "summary": json.loads(r[4] or "null")}
                for r in self.db.execute("SELECT id,kind,started,finished,summary FROM runs ORDER BY id")]
