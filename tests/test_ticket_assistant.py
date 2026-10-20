import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.ticket_assistant import (
    ask_about_ticket,
    InvalidToolArgumentsError
)


def test_ask_about_ticket_without_tool(monkeypatch):
    fake_response = SimpleNamespace(
        output=[],
        output_text="Hello, how can I help you?"
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = fake_response

    monkeypatch.setattr(
        "app.services.ticket_assistant.get_openai_client",
        lambda: fake_client
    )

    response = ask_about_ticket("hello")

    assert response is fake_response
    assert fake_client.responses.create.call_count == 1


def test_ask_about_ticket_with_tool(monkeypatch):

    tool_call = SimpleNamespace(
        type="function_call",
        name="get_ticket_history",
        arguments='{"ticket_id":42}',
        call_id="call_test_123"
    )

    first_response = SimpleNamespace(
        id="resp_test_123",
        output=[tool_call]
    )

    final_response = SimpleNamespace(
        output=[],
        output_text="No classification history found for ticket 42."
    )

    fake_client = Mock()

    fake_client.responses.create.side_effect = [
        first_response,
        final_response
    ]

    fake_history = {
        "ticket_id": 42,
        "classifications": [],
        "message": "No classification history found for this ticket"
    }

    fake_get_ticket_history = Mock(return_value=fake_history)

    monkeypatch.setattr(
        "app.services.ticket_assistant.get_openai_client",
        lambda: fake_client
    )

    monkeypatch.setattr(
        'app.services.ticket_assistant.get_ticket_history',
        fake_get_ticket_history
    )

    response = ask_about_ticket(
        "What is the classification history of ticket 42?"
    )

    second_call = fake_client.responses.create.call_args_list[1]

    assert response is final_response
    assert fake_client.responses.create.call_count == 2
    assert second_call.kwargs["previous_response_id"] == "resp_test_123"
    assert len(second_call.kwargs["input"]) == 1
    assert second_call.kwargs["input"][0]["call_id"] == "call_test_123"
    assert second_call.kwargs["input"][0]["type"] == "function_call_output"

    sent_history = json.loads(second_call.kwargs["input"][0]["output"])

    assert sent_history == fake_history
    fake_get_ticket_history.assert_called_once_with(42)


def test_ask_about_ticket_invalid_function(monkeypatch):

    tool_call = SimpleNamespace(
        type="function_call",
        name="delete_all_tickets",
        arguments='{"ticket_id":42}',
        call_id="call_test_123"
    )

    first_response = SimpleNamespace(
        id="resp_test_123",
        output=[tool_call]
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = first_response

    fake_get_ticket_history = Mock()

    monkeypatch.setattr(
        "app.services.ticket_assistant.get_openai_client",
        lambda: fake_client
    )

    monkeypatch.setattr(
        'app.services.ticket_assistant.get_ticket_history',
        fake_get_ticket_history
    )

    with pytest.raises(ValueError, match="Invalid function name"):
        ask_about_ticket("Delete all tickets")

    assert fake_client.responses.create.call_count == 1
    fake_get_ticket_history.assert_not_called()


@pytest.mark.parametrize(
    "invalid_id",
    [-5, 0, "42", True, 3.5]
)
def test_ask_about_ticket_invalid_ticket_id(monkeypatch, invalid_id):
    tool_call = SimpleNamespace(
        type="function_call",
        name="get_ticket_history",
        arguments=json.dumps({"ticket_id": invalid_id}),
        call_id="call_test_123"
    )

    first_response = SimpleNamespace(
        id="resp_test_123",
        output=[tool_call]
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = first_response

    monkeypatch.setattr(
        "app.services.ticket_assistant.get_openai_client",
        lambda: fake_client
    )

    fake_get_ticket_history = Mock()

    monkeypatch.setattr(
        'app.services.ticket_assistant.get_ticket_history',
        fake_get_ticket_history
    )

    with pytest.raises(InvalidToolArgumentsError, match="Invalid ticket_id"):
        ask_about_ticket(f"Show me the history of ticket {invalid_id}")

    assert fake_client.responses.create.call_count == 1
    fake_get_ticket_history.assert_not_called()


def test_ask_about_ticket_invalid_json(monkeypatch):
    tool_call = SimpleNamespace(
        type="function_call",
        name="get_ticket_history",
        arguments='{"ticket_id":42',
        call_id="call_test_123"
    )

    first_response = SimpleNamespace(
        id="resp_test_123",
        output=[tool_call]
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = first_response

    monkeypatch.setattr(
        "app.services.ticket_assistant.get_openai_client",
        lambda: fake_client
    )

    fake_get_ticket_history = Mock()

    monkeypatch.setattr(
        'app.services.ticket_assistant.get_ticket_history',
        fake_get_ticket_history
    )

    with pytest.raises(
        InvalidToolArgumentsError,
        match="Invalid JSON arguments"
    ) as exc_info:
        ask_about_ticket("Show me the history of ticket 42")

    assert fake_client.responses.create.call_count == 1
    fake_get_ticket_history.assert_not_called()
    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)


def test_ask_about_ticket_missing_ticket_id(monkeypatch):
    tool_call = SimpleNamespace(
        type="function_call",
        name="get_ticket_history",
        arguments="{}",
        call_id="call_test_123"
    )

    first_response = SimpleNamespace(
        id="resp_test_123",
        output=[tool_call]
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = first_response

    monkeypatch.setattr(
        "app.services.ticket_assistant.get_openai_client",
        lambda: fake_client
    )

    fake_get_ticket_history = Mock()

    monkeypatch.setattr(
        'app.services.ticket_assistant.get_ticket_history',
        fake_get_ticket_history
    )

    with pytest.raises(
        InvalidToolArgumentsError,
        match="Missing ticket_id"
    ) as exc_info:
        ask_about_ticket("Show me the history of ticket")

    assert fake_client.responses.create.call_count == 1
    fake_get_ticket_history.assert_not_called()
    assert isinstance(exc_info.value.__cause__, KeyError)


def test_ask_about_ticket_invalid_arguments_type(monkeypatch):
    tool_call = SimpleNamespace(
        type="function_call",
        name="get_ticket_history",
        arguments='["ticket_id", 42]',
        call_id="call_test_123"
    )

    first_response = SimpleNamespace(
        id="resp_test_123",
        output=[tool_call]
    )

    fake_client = Mock()
    fake_client.responses.create.return_value = first_response

    monkeypatch.setattr(
        "app.services.ticket_assistant.get_openai_client",
        lambda: fake_client
    )

    fake_get_ticket_history = Mock()

    monkeypatch.setattr(
        'app.services.ticket_assistant.get_ticket_history',
        fake_get_ticket_history
    )

    with pytest.raises(
        InvalidToolArgumentsError,
        match="Arguments must be an object"
    ):
        ask_about_ticket("Show me the history of ticket 42")

    assert fake_client.responses.create.call_count == 1
    fake_get_ticket_history.assert_not_called()
