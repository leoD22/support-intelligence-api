from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.schemas.ticket import TicketResponse
from app.schemas.llm import LLMClassificationResult

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
