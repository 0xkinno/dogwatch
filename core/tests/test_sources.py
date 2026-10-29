import json
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "evidence" / "need" / "sources.json"


def _by_id():
    return {s["id"]: s for s in json.loads(SRC.read_text(encoding="utf-8"))["sources"]}


def test_money_figure_is_read_from_sources():
    wage = _by_id()["ilo-wage-2027"]["value"]
    assert wage == 704
    assert 6 * wage == 4224


def test_every_verified_quote_is_in_its_snapshot():
    base = SRC.parent
    for s in _by_id().values():
        if not s["status"].startswith("VERIFIED"):
            continue
        snap = (base / s["snapshot"]).resolve()
        text = " ".join(snap.read_text(encoding="utf-8").split())
        assert " ".join(s["quote"].split()) in text, s["id"]


def test_unverified_sources_are_labelled():
    for s in _by_id().values():
        assert s["status"] in {"NOT_VERIFIED", "NOT_RUN"} or s["status"].startswith("VERIFIED")
