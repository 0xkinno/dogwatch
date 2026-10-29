"""Sea-service totals under every counting convention. No model."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .dates import add_months, calendar_months_in_window, days_in_window

CONVENTIONS = ("days_inclusive", "days_exclusive", "calendar_months", "days_360", "days_365")


def total_under(entries, ws: date, we: date, convention: str) -> tuple[float, str]:
    """Return (value, unit) where unit is 'days' or 'months'."""
    if convention == "days_inclusive":
        return float(days_in_window(entries, ws, we, True)), "days"
    if convention == "days_exclusive":
        return float(days_in_window(entries, ws, we, False)), "days"
    if convention == "calendar_months":
        return calendar_months_in_window(entries, ws, we), "months"
    if convention == "days_360":
        return days_in_window(entries, ws, we, True) / 30.0, "months"
    if convention == "days_365":
        return days_in_window(entries, ws, we, True) * 12.0 / 365.0, "months"
    raise ValueError(f"unknown convention {convention}")


@dataclass
class ConventionResult:
    convention: str
    total: float
    unit: str
    required: float
    meets: bool


@dataclass
class SeaServiceCheck:
    window_start: date
    window_end: date
    results: list[ConventionResult] = field(default_factory=list)
    stated_convention: str = "unstated"
    verdict: str = "ASK_ADMINISTRATION"  # MEETS, SHORT, ASK_ADMINISTRATION
    agree: bool = False
    arithmetic: str = ""


def window_for(params: dict, apply_date: date) -> tuple[date, date]:
    """Window ending the day before the application date, as the rules say 'before you apply'."""
    from datetime import timedelta

    end = apply_date - timedelta(days=1)
    if "window_years" in params:
        start = add_months(apply_date, -12 * int(params["window_years"]))
    else:
        start = add_months(apply_date, -int(params["window_months"]))
    return start, end


def check_requirement(entries, params: dict, apply_date: date) -> SeaServiceCheck:
    """Evaluate a sea-service rule under every convention.

    The administration's stated convention decides if the rule states one. Otherwise every
    convention is computed and a disagreement returns ASK_ADMINISTRATION.
    """
    ws, we = window_for(params, apply_date)
    req_days = params.get("required_days")
    req_months = params.get("required_months")
    if req_days is None and req_months is None:
        raise ValueError("rule has no requirement")
    if req_days is None:
        req_days = req_months * 30
    if req_months is None:
        req_months = req_days / 30.0
    stated = str(params.get("convention", "unstated"))
    res = []
    for conv in CONVENTIONS:
        val, unit = total_under(entries, ws, we, conv)
        required = float(req_days) if unit == "days" else float(req_months)
        res.append(ConventionResult(conv, round(val, 4), unit, required, val >= required))
    chk = SeaServiceCheck(ws, we, res, stated)
    verdicts = {r.meets for r in res}
    chk.agree = len(verdicts) == 1
    if stated in CONVENTIONS:
        pick = next(r for r in res if r.convention == stated)
        chk.verdict = "MEETS" if pick.meets else "SHORT"
    elif chk.agree:
        chk.verdict = "MEETS" if res[0].meets else "SHORT"
    else:
        chk.verdict = "ASK_ADMINISTRATION"
    chk.arithmetic = "; ".join(f"{r.convention}={r.total:g} {r.unit} vs {r.required:g}" for r in res)
    return chk
