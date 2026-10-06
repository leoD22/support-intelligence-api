from fastapi.testclient import TestClient
from app.main import app
import pytest


@pytest.fixture
def client():
    return TestClient(app)


def test_classify_normal(client, monkeypatch):
    def fake_classify(text):
        return {
            "category": "technical",
            "priority": 1,
            "summary": "The user got an error during login",
            "entities": [
                "error",
                "login"
            ]
        }

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
