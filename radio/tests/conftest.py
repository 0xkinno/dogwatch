import pytest


@pytest.fixture(autouse=True)
def _isolate_evidence(tmp_path, monkeypatch):
    """Tests use fake transports; their action records must never land in the repository evidence folder."""
    monkeypatch.setenv("DOGWATCH_ACTIONS_DIR", str(tmp_path / "actions"))
