"""Date arithmetic for sea service. Pure functions, no model, no I/O."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from dateutil.relativedelta import relativedelta


@dataclass(frozen=True)
class Entry:
    """One discharge-book entry: a stay on board from sign_on to sign_off."""

    sign_on: date
    sign_off: date
    vessel: str = ""
    flag: str = ""
    capacity: str = ""
    ship_type: str = ""

    def __post_init__(self) -> None:
        if self.sign_off < self.sign_on:
            raise ValueError("sign_off is before sign_on")


def add_months(d: date, n: int) -> date:
    return d + relativedelta(months=n)


def months_between_calendar(a: date, b: date) -> int:
    """Whole calendar months from a to b (a + n months <= b)."""
    rd = relativedelta(b, a)
    return rd.years * 12 + rd.months


def merge_intervals(entries, window_start: date, window_end: date) -> list[tuple[date, date]]:
    """Clip each entry to the window and merge overlaps and touching ranges so a day counts once."""
    clipped = []
    for e in entries:
        s, f = max(e.sign_on, window_start), min(e.sign_off, window_end)
        if s <= f:
            clipped.append((s, f))
    clipped.sort()
    merged: list[tuple[date, date]] = []
    for s, f in clipped:
        if merged and s <= merged[-1][1]:
            if f > merged[-1][1]:
                merged[-1] = (merged[-1][0], f)
        else:
            merged.append((s, f))
    return merged


def days_in_window(entries, window_start: date, window_end: date, inclusive: bool = True) -> int:
    """Union of [sign_on, sign_off] intervals clipped to the window. Overlaps count once.

    inclusive counts both the sign-on and the sign-off day; exclusive counts end minus start.
    """
    total = 0
    for s, f in merge_intervals(entries, window_start, window_end):
        total += (f - s).days + (1 if inclusive else 0)
    return total


def calendar_months_in_window(entries, window_start: date, window_end: date) -> float:
    """Whole calendar months plus leftover days over 30, per merged interval, endpoints inclusive."""
    total = 0.0
    for s, f in merge_intervals(entries, window_start, window_end):
        end_excl = f + relativedelta(days=1)
        rd = relativedelta(end_excl, s)
        total += rd.years * 12 + rd.months + rd.days / 30.0
    return total
