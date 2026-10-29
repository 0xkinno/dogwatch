"""Caps for the public judge door: one live run at a time per browser, 8 per hour per address, 60 per day overall."""
from __future__ import annotations

import os
import threading
import time


class Caps:
    def __init__(self, per_hour: int = 8, per_day: int = 60):
        self.per_hour, self.per_day = per_hour, per_day
        self._lock = threading.Lock()
        self._by_addr: dict[str, list[float]] = {}
        self._all: list[float] = []
        self._busy: set[str] = set()

    @staticmethod
    def killed() -> bool:
        return os.environ.get("DOGWATCH_KILL", "") not in ("", "0", "false")

    def acquire(self, addr: str, browser: str, now: float | None = None) -> tuple[bool, str]:
        """Returns (allowed, plain-words reason). Release with release() when the run ends."""
        now = now if now is not None else time.time()
        with self._lock:
            if self.killed():
                return False, "Live runs are switched off by the operator. The recorded run below is real and labelled."
            self._all = [t for t in self._all if now - t < 86400]
            hits = [t for t in self._by_addr.get(addr, []) if now - t < 3600]
            self._by_addr[addr] = hits
            if browser in self._busy:
                return False, "One live run at a time per browser. Wait for the current one to finish."
            if len(hits) >= self.per_hour:
                return False, f"Limit reached: {self.per_hour} live runs per hour per address. The recorded run is available."
            if len(self._all) >= self.per_day:
                return False, f"Daily limit reached: {self.per_day} live runs across all visitors. The recorded run is available."
            hits.append(now)
            self._all.append(now)
            self._busy.add(browser)
            return True, ""

    def release(self, browser: str) -> None:
        with self._lock:
            self._busy.discard(browser)

    def describe(self) -> str:
        return (f"One live run at a time per browser, {self.per_hour} per hour per address, {self.per_day} per day overall. "
                "Past the cap you get the recorded run, labelled RECORDED.")
