from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.schemas.ticket import TicketResponse
from app.schemas.llm import LLMClassificationResult
from openai import APIConnectionError
import httpx2
from app.services.llm_classifier import InvalidLLMResponseError

@pytest.fixture
def client():
    return TestClient(app)


def test_classify_normal(client, monkeypatch):
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
        }
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


def test_classify_missing_text(client):
    response = client.post("/classify", json={})
    assert response.status_code == 422


def test_classify_fallback(client, monkeypatch):
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
        }
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


def test_classify_invalid_llm_response(client, monkeypatch):
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
        }
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