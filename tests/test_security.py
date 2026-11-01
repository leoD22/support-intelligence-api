import pytest
from fastapi import HTTPException

from app.security import verify_api_key


def test_verify_api_key_accepts_valid_key(monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")

    assert verify_api_key("test_secret") is None


def test_verify_api_key_rejects_invalid_key(monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key("wrong_secret")

    assert exc_info.value.status_code == 403


def test_verify_api_key_rejects_missing_key(monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(None)

    assert exc_info.value.status_code == 403


def test_verify_api_key_rejects_missing_server_key(monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", None)

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key("test_secret")

    assert exc_info.value.status_code == 503
