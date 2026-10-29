"""Interruption budget, in code: two questions per day. Lapses and approval requests always pass."""
from __future__ import annotations

from datetime import date

from .state import State

MAX_QUESTIONS_PER_DAY = 2
ALWAYS = {"lapse", "approval"}


class Budget:
    def __init__(self, state: State):
        self.state = state

    def allow(self, kind: str, today: date) -> bool:
        """Record and allow the interruption, or refuse it. Refused questions are kept for the next day."""
        if kind in ALWAYS:
            self.state.count_event(today.isoformat(), kind)
            return True
        if kind != "question":
            raise ValueError(f"unknown interruption kind {kind}")
        used = self.state.event_count(today.isoformat(), "question")
        if used >= MAX_QUESTIONS_PER_DAY:
            return False
        self.state.count_event(today.isoformat(), "question")
        return True
