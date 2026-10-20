from app.services.persistence import get_classifications


GET_TICKET_HISTORY_TOOL = {
    "type": "function",
    "name": "get_ticket_history",
    "description": "Retrieve classification history for a ticket",
    "parameters": {
        "type": "object",
        "properties": {
            "ticket_id": {
                    "type": "integer",
                    "description": "ID of the ticket to retrieve"
                }
        },
        "required": ["ticket_id"],
        "additionalProperties": False
            },
    "strict": True
}


def get_ticket_history(ticket_id: int) -> dict:
    classifications = get_classifications(ticket_id=ticket_id)

    if classifications:
        list_classifications = []

        for classification in classifications:
            list_classifications.append(dict(classification))

        result = {
            "ticket_id": ticket_id,
            "classifications": list_classifications,
            "message": "Classification history retrieved"
        }
    else:
        result = {
            "ticket_id": ticket_id,
            "classifications": [],
            "message": "No classification history found for this ticket"
        }

    return result
