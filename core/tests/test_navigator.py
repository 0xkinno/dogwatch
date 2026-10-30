from datetime import date

import pytest

from dogwatch.navigator import engine
from dogwatch.navigator.dates import Entry, calendar_months_in_window, days_in_window, merge_intervals
from dogwatch.navigator.rulepack import load_all, verify_quotes
from dogwatch.navigator.seaservice import check_requirement
from dogwatch.persona import ARJUN, CONTRACT_OFFER, DEMO_TODAY


def E(a, b):
    return Entry(date.fromisoformat(a), date.fromisoformat(b))


def test_overlaps_count_once():
    es = [E("2026-01-01", "2026-01-10"), E("2026-01-05", "2026-01-20")]
    assert days_in_window(es, date(2026, 1, 1), date(2026, 12, 31)) == 20


def test_inclusive_vs_exclusive():
    es = [E("2026-01-01", "2026-01-10")]
    assert days_in_window(es, date(2026, 1, 1), date(2026, 12, 31), True) == 10
    assert days_in_window(es, date(2026, 1, 1), date(2026, 12, 31), False) == 9


def test_clip_to_window():
    es = [E("2025-12-20", "2026-01-10")]
    assert days_in_window(es, date(2026, 1, 1), date(2026, 1, 31)) == 10


def test_leap_day_counted():
    es = [E("2028-02-01", "2028-03-01")]
    assert days_in_window(es, date(2028, 1, 1), date(2028, 12, 31)) == 30  # 29 + 1
    es2 = [E("2027-02-01", "2027-03-01")]
    assert days_in_window(es2, date(2027, 1, 1), date(2027, 12, 31)) == 29


def test_touching_ranges_merge():
    es = [E("2026-01-01", "2026-01-10"), E("2026-01-10", "2026-01-12")]
    assert merge_intervals(es, date(2026, 1, 1), date(2026, 12, 31)) == [(date(2026, 1, 1), date(2026, 1, 12))]


def test_calendar_months_whole():
    es = [E("2026-01-01", "2026-03-31")]
    assert calendar_months_in_window(es, date(2026, 1, 1), date(2026, 12, 31)) == pytest.approx(3.0)


def test_sign_off_before_sign_on_rejected():
    with pytest.raises(ValueError):
        E("2026-02-01", "2026-01-01")


def test_conventions_can_disagree_near_boundary():
    # 360 days inclusive meets a 360 day rule, but is under 12 calendar months and under 365 day years.
    es = [E("2025-01-01", "2025-12-26")]  # 360 days inclusive
    params = {"required_days": 360, "window_years": 5, "convention": "unstated"}
    chk = check_requirement(es, params, date(2026, 3, 1))
    assert chk.agree is False
    assert chk.verdict == "ASK_ADMINISTRATION"


def test_stated_convention_decides():
    es = [E("2025-01-01", "2025-12-26")]
    params = {"required_days": 360, "window_years": 5, "convention": "calendar_months"}
    assert check_requirement(es, params, date(2026, 3, 1)).verdict == "SHORT"


def test_clear_pass_is_agreed():
    es = [E("2024-01-01", "2025-06-30")]
    params = {"required_days": 360, "window_years": 5, "convention": "unstated"}
    chk = check_requirement(es, params, date(2026, 3, 1))
    assert chk.agree and chk.verdict == "MEETS"


def test_arjun_not_ready_day_42_of_181():
    res = engine.run_readiness(ARJUN, CONTRACT_OFFER, date.fromisoformat(DEMO_TODAY))
    assert res["overall"] == "NOT_READY"
    med = next(d for d in res["documents"] if d["document_id"] == "medical")
    assert med["state"] == "LAPSES_DURING"
    assert (med["day_x"], med["day_y"]) == (42, 181)
    assert "day 42 of 181" in res["summary"]
    others = [d for d in res["documents"] if d["document_id"] != "medical"]
    assert all(d["state"] == "VALID_THROUGH" for d in others)


def test_india_renewal_window_is_unsourced_so_ask():
    res = engine.run_readiness(ARJUN, CONTRACT_OFFER, date.fromisoformat(DEMO_TODAY))
    med = next(d for d in res["documents"] if d["document_id"] == "medical")
    assert med["renewal"]["state"] == "ASK_ADMINISTRATION"


def test_unread_never_ready():
    prof = {"documents": [{"id": "m", "doc_type": "medical", "administration": "India", "expiry": None, "unread": True}]}
    res = engine.run_readiness(prof, {"start": "2027-02-01", "end": "2027-07-31"}, date(2026, 10, 28))
    assert res["overall"] == "CANNOT_VERIFY"


def test_missing_required_document_never_ready():
    prof = {"documents": [{"id": "c", "doc_type": "coc", "administration": "India", "expiry": "2030-01-01"}]}
    res = engine.run_readiness(prof, {"start": "2027-02-01", "end": "2027-07-31", "required_types": ["coc", "medical"]}, date(2026, 10, 28))
    assert res["overall"] == "CANNOT_VERIFY"


def test_lapse_dominates_unknown():
    prof = {"documents": [
        {"id": "m", "doc_type": "medical", "administration": "India", "expiry": "2027-03-14"},
        {"id": "c", "doc_type": "coc", "administration": "India", "expiry": None, "unread": True}]}
    res = engine.run_readiness(prof, {"start": "2027-02-01", "end": "2027-07-31"}, date(2026, 10, 28))
    assert res["overall"] == "NOT_READY"


def test_expired_before_start():
    prof = {"documents": [{"id": "m", "doc_type": "medical", "administration": "India", "expiry": "2027-01-15"}]}
    res = engine.run_readiness(prof, {"start": "2027-02-01", "end": "2027-07-31"}, date(2026, 10, 28))
    assert res["documents"][0]["state"] == "EXPIRED_BEFORE_START"
    assert res["overall"] == "NOT_READY"


def test_expiry_on_last_day_is_valid():
    prof = {"documents": [{"id": "m", "doc_type": "medical", "administration": "India", "expiry": "2027-07-31"}]}
    res = engine.run_readiness(prof, {"start": "2027-02-01", "end": "2027-07-31"}, date(2026, 10, 28))
    assert res["overall"] == "READY"


def test_travel_buffer_extends_window():
    prof = {"documents": [{"id": "m", "doc_type": "medical", "administration": "India", "expiry": "2027-07-31"}]}
    res = engine.run_readiness(prof, {"start": "2027-02-01", "end": "2027-07-31", "travel_after": 3}, date(2026, 10, 28))
    assert res["overall"] == "NOT_READY"


def test_australian_window_open_rule_is_used():
    prof = {"documents": [{"id": "c", "doc_type": "coc", "administration": "Australia", "expiry": "2027-03-14"}]}
    res = engine.run_readiness(prof, {"start": "2027-02-01", "end": "2027-07-31"}, date(2026, 10, 28))
    ren = res["documents"][0]["renewal"]
    assert ren["state"] == "WINDOW_NOT_OPEN" and ren["opens_on"] == "2026-09-14" or ren["state"] == "WINDOW_OPEN"
    assert res["documents"][0]["rules"][0]["rule_id"] == "AU-WINDOW-6M"


@pytest.mark.parametrize("name", ["stcw-core", "au-amsa", "uk-mca", "in-dgs", "sg-mpa", "ng-nimasa"])
def test_every_rule_quote_is_in_its_snapshot(name):
    packs = load_all()
    assert verify_quotes(packs[name]) == []


def test_pack_hash_stable_and_present():
    a, b = load_all(), load_all()
    assert all(a[k].sha256 == b[k].sha256 and len(a[k].sha256) == 64 for k in a)


def test_unsourced_packs_ship_no_rules():
    packs = load_all()
    assert packs["ng-nimasa"].rules == [] and packs["ng-nimasa"].status == "unsourced"
    assert {r.id for r in packs["sg-mpa"].rules} >= {"SG-WINDOW-12M", "SG-SS-12M-5Y", "SG-SS-3M-6M"}
    assert {r.id for r in packs["in-dgs"].rules} >= {"IN-SS-1Y-5Y", "IN-REVAL-COURSE"}
