import pytest

from app.services.openai_client import get_openai_client
from unittest.mock import Mock


def test_get_openai_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    with pytest.raises(RuntimeError):
        get_openai_client()


def test_get_openai_client_configures_timeout_and_retries(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    mock_client = Mock()
    monkeypatch.setattr("app.services.openai_client.OpenAI", mock_client)

    client = get_openai_client()

    mock_client.assert_called_once_with(
        api_key="test_key",
        timeout=30.0,
        max_retries=1
    )

    assert client is mock_client.return_value
