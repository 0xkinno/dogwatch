import pytest


@pytest.fixture(autouse=True)
def _isolate_receipts(tmp_path, monkeypatch):
    """Tests use fake model clients; their receipts must never land in the repository evidence folder."""
    monkeypatch.setenv("DOGWATCH_RECEIPTS", str(tmp_path / "receipts.jsonl"))
