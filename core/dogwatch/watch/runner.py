"""Timers for the always-on loop. A due check reads durable state, so a restart never skips or repeats a run."""
from __future__ import annotations

import time
from datetime import date, datetime, timezone

from .loop import Watch

DAY = 24 * 3600
WEEK = 7 * DAY


def last_finished(watch: Watch, kind: str) -> float | None:
    done = [r["finished"] for r in watch.state.runs() if r["kind"] == kind and r["finished"]]
    return max(done) if done else None


def due(watch: Watch, kind: str, now: float) -> bool:
    last = last_finished(watch, kind)
    interval = DAY if kind == "daily" else WEEK
    return last is None or now - last >= interval


def tick(watch: Watch, now: float | None = None, lookout=None) -> list[str]:
    """Run whatever is due. Called by the service loop every minute, or once by a scheduler."""
    now = now if now is not None else time.time()
    today: date = datetime.fromtimestamp(now, tz=timezone.utc).date()
    ran = []
    if due(watch, "daily", now):
        watch.daily(today)
        ran.append("daily")
    if due(watch, "weekly", now):
        watch.weekly(today, lookout)
        ran.append("weekly")
    return ran


def run_forever(watch: Watch, lookout=None, poll_seconds: int = 60) -> None:  # pragma: no cover
    while True:
        tick(watch, lookout=lookout)
        time.sleep(poll_seconds)
