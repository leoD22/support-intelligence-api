from fastapi import FastAPI

from app.schemas.ticket import TicketRequest, TicketResponse

from app.services.classifier import classify_ticket
from app.services.persistence import save_classification


app = FastAPI()


@app.post("/classify", response_model=TicketResponse)
def classify(ticket: TicketRequest):

    result = classify_ticket(ticket.text)

    save_classification(
        ticket.text,
        result["category"],
        result["priority"],
        result["summary"],
        result["entities"]
    )

    return result
