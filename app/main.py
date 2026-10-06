from fastapi import FastAPI

from app.schemas.ticket import (
    TicketRequest,
    TicketResponse,
    ClassificationHistory
    )

from app.services.persistence import save_classification, get_classifications
from app.services.llm_classifier import classify_ticket_with_llm, PROMPT_VERSION

app = FastAPI()


@app.post("/classify", response_model=TicketResponse)
def classify(ticket: TicketRequest):

    result = classify_ticket_with_llm(ticket.text)

    save_classification(
        ticket.text,
        result["category"],
        result["priority"],
        result["summary"],
        result["entities"],
        PROMPT_VERSION
    )

    return result


@app.get("/history/{ticket_id}", response_model=list[ClassificationHistory])
def history(ticket_id: int):
    return get_classifications(ticket_id)
