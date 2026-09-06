from fastapi import FastAPI

from app.schemas.ticket import TicketRequest, TicketResponse
from app.services.classifier import classify_ticket


app = FastAPI()


@app.post("/classify", response_model=TicketResponse)
def classify(ticket: TicketRequest):
    return classify_ticket(ticket.text)
