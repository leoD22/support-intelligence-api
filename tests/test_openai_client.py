import pytest

from app.services.openai_client import get_openai_client


def test_get_openai_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    with pytest.raises(RuntimeError):
        get_openai_client()
