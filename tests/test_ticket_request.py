import pytest
from pydantic import ValidationError

from app.schemas.ticket import TicketRequest


def test_ticket_request_accepts_valid_text():
    ticket = TicketRequest(text="The printer is not working")

    assert ticket.text == "The printer is not working"


def test_ticket_request_strips_whitespace():
    ticket = TicketRequest(text="   Printer is not working   ")

    assert ticket.text == "Printer is not working"


def test_ticket_request_rejects_empty_text():
    with pytest.raises(ValidationError):
        TicketRequest(text="")


def test_ticket_request_rejects_whitespace_only_text():
    with pytest.raises(ValidationError):
        TicketRequest(text="   ")


def test_ticket_request_rejects_missing_text():
    with pytest.raises(ValidationError):
        TicketRequest()
