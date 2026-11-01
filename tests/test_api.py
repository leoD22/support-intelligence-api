from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.schemas.ticket import TicketResponse
from app.schemas.llm import LLMClassificationResult
from openai import APIConnectionError
import httpx2
from app.services.llm_classifier import InvalidLLMResponseError
from types import SimpleNamespace
from unittest.mock import Mock


fake_response = SimpleNamespace(
    output_text="Ticket 42 has one technical classification."
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")
    return {"X-API-Key": "test_secret"}


def test_classify_normal(client, monkeypatch, auth_headers):
    def fake_classify(text):
        return LLMClassificationResult(
            classification=TicketResponse(
                category="technical",
                priority=1,
                summary="The user got an error during login",
                entities=[
                    "error",
                    "login"
                ]
            ),
            model_name="test-model",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            latency_ms=100
        )

    monkeypatch.setattr("app.main.classify_ticket_with_llm", fake_classify)

    response = client.post(
        "/classify",
        json={
            "text": "The user got an error during login"
        },
        headers=auth_headers
    )

    expected_response = {
        "category": "technical",
        "priority": 1,
        "summary": "The user got an error during login",
        "entities": [
            "error",
            "login"
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected_response


def test_classify_missing_text(client, auth_headers):
    response = client.post(
        "/classify",
        json={},
        headers=auth_headers
    )

    assert response.status_code == 422


def test_classify_empty_text(client, auth_headers):
    response = client.post(
        "/classify",
        json={"text": ""},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_classify_whitespace_only_text(client, monkeypatch, auth_headers):
    mock_classifier = Mock()
    mock_save = Mock()
    monkeypatch.setattr("app.main.classify_ticket_with_llm", mock_classifier)
    monkeypatch.setattr("app.main.save_classification", mock_save)

    response = client.post(
        "/classify",
        json={"text": "   "},
        headers=auth_headers
    )

    assert response.status_code == 422
    mock_classifier.assert_not_called()
    mock_save.assert_not_called()


def test_classify_fallback(client, monkeypatch, auth_headers):
    request = httpx2.Request("POST", "https://api.openai.com/v1/responses")
    values = {}

    def fake_classify(text):
        raise APIConnectionError(
            message="Simulated connection error",
            request=request
        )

    def fake_save_classification(**kwargs):
        values.update(kwargs)

    monkeypatch.setattr("app.main.classify_ticket_with_llm", fake_classify)
    monkeypatch.setattr(
        "app.main.save_classification",
        fake_save_classification
    )

    response = client.post(
        "/classify",
        json={
            "text": "The user got an error during login"
        },
        headers=auth_headers
    )

    expected_response = {
        "category": "technical",
        "priority": 1,
        "summary": "The user got an error during login",
        "entities": [
            "error",
            "login"
        ]
    }

    assert response.status_code == 200
    assert response.json() == expected_response
    assert values["prompt_version"] == 0
    assert values["model_name"] is None
    assert values["cost_usd"] is None
    assert values["input_tokens"] is None
    assert values["output_tokens"] is None
    assert values["total_tokens"] is None
    assert values["latency_ms"] is None


def test_classify_invalid_llm_response(client, monkeypatch, auth_headers):
    values = {}

    def fake_classify(text):
        raise InvalidLLMResponseError(
            "OpenAI returned no parsed classification"
        )

    def fake_save_classification(**kwargs):
        values.update(kwargs)

    monkeypatch.setattr("app.main.classify_ticket_with_llm", fake_classify)
    monkeypatch.setattr(
        "app.main.save_classification",
        fake_save_classification
    )

    response = client.post(
        "/classify",
        json={
            "text": "The user got an error during login"
        },
        headers=auth_headers
    )

    expected_response = {
        "category": "technical",
        "priority": 1,
        "summary": "The user got an error during login",
        "entities": [
            "error",
            "login"
        ]
    }

    assert response.status_code == 200
    assert response.json() == expected_response
    assert values["prompt_version"] == 0
    assert values["model_name"] is None
    assert values["cost_usd"] is None
    assert values["input_tokens"] is None
    assert values["output_tokens"] is None
    assert values["total_tokens"] is None
    assert values["latency_ms"] is None


def test_ask_assistant_success(client, monkeypatch, auth_headers):

    monkeypatch.setattr(
        'app.main.ask_about_ticket',
        lambda question: fake_response
    )

    response = client.post(
        "/assistant/ask",
        json={
            "question": "What is the history of ticket 42?"
        },
        headers=auth_headers
    )

    expected_response = {
        "answer": "Ticket 42 has one technical classification."
        }

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "payload",
    [
        {"question": ""},
        {},
        {"question": "   "}
    ]
)
def test_ask_assistant_invalid_question(
    client, monkeypatch, auth_headers, payload
):
    fake_ask_about_ticket = Mock()
    monkeypatch.setattr(
        'app.main.ask_about_ticket',
        fake_ask_about_ticket
    )

    response = client.post(
        "/assistant/ask",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code == 422
    fake_ask_about_ticket.assert_not_called()


def test_ask_assistant_connection_error(client, monkeypatch, auth_headers):
    request = httpx2.Request("POST", "https://api.openai.com/v1/responses")

    def fake_ask_about_ticket(text):
        raise APIConnectionError(
            message="Assistant temporarily unavailable",
            request=request
        )

    monkeypatch.setattr(
        "app.main.ask_about_ticket",
        fake_ask_about_ticket
    )

    response = client.post(
        "/assistant/ask",
        json={
            "question": "Describe the ticket 12"
        },
        headers=auth_headers
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Assistant temporarily unavailable"
    }


def test_classify_rejects_missing_api_key(client, monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")

    response = client.post(
        "/classify",
        json={
            "text": "The user got an error during login"
        }
    )

    assert response.status_code == 403


def test_classify_rejects_invalid_api_key(client, monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")

    response = client.post(
        "/classify",
        json={
            "text": "The user got an error during login"
        },
        headers={"X-API-Key": "wrong_secret"}
    )

    assert response.status_code == 403


def test_history_rejects_missing_api_key(client, monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")
    mock_get_classifications = Mock()
    monkeypatch.setattr("app.main.get_classifications", mock_get_classifications)

    response = client.get("/history/42")

    assert response.status_code == 403
    mock_get_classifications.assert_not_called()


def test_history_accepts_valid_api_key(client, monkeypatch, auth_headers):
    mock_get_classifications = Mock(return_value=[])
    monkeypatch.setattr("app.main.get_classifications", mock_get_classifications)

    response = client.get(
        "/history/42",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == []
    mock_get_classifications.assert_called_once_with(42)


def test_ask_assistant_rejects_missing_api_key(client, monkeypatch):
    monkeypatch.setattr("app.security.API_ACCESS_KEY", "test_secret")
    mock_ask_about_ticket = Mock()
    monkeypatch.setattr("app.main.ask_about_ticket", mock_ask_about_ticket)

    response = client.post(
        "/assistant/ask",
        json={
            "question": "Describe the ticket 12"
        }
    )

    assert response.status_code == 403
    mock_ask_about_ticket.assert_not_called()
