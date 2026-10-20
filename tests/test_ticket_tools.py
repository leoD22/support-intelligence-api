from types import MappingProxyType

from app.services.ticket_tools import get_ticket_history


def test_get_ticket_history_empty(monkeypatch):
    def fake_get_classifications(ticket_id):
        return []

    monkeypatch.setattr(
        'app.services.ticket_tools.get_classifications',
        fake_get_classifications
    )

    expected_output = {
        "ticket_id": 999999,
        "classifications": [],
        "message": "No classification history found for this ticket"
    }

    result = get_ticket_history(ticket_id=999999)

    assert result == expected_output


def test_get_ticket_history_with_results(monkeypatch):
    def fake_get_classifications(ticket_id):
        record = MappingProxyType({
            "text": "The user cannot login",
            "category": "technical",
            "priority": 3,
            "summary": "User cannot access their account",
            "entities": ["login"],
            "prompt_version": 2
        })

        return [record]

    monkeypatch.setattr(
        'app.services.ticket_tools.get_classifications',
        fake_get_classifications
    )

    result = get_ticket_history(ticket_id=42)

    assert result["ticket_id"] == 42
    assert len(result["classifications"]) == 1
    assert result["message"] == "Classification history retrieved"
    assert isinstance(result["classifications"][0], dict)
