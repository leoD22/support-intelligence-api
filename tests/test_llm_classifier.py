import pytest

from app.services.llm_classifier import (
    classify_ticket_with_llm,
    InvalidLLMResponseError
)


class FakeResponse:
    def __init__(self):
        self.output_parsed = None


class FakeResponses:

    def parse(self, **kwargs):
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_invalid_llm_response(monkeypatch):
    monkeypatch.setattr(
        'app.services.llm_classifier.get_openai_client',
        FakeClient
    )

    with pytest.raises(InvalidLLMResponseError):
        classify_ticket_with_llm("The user cannot login")
