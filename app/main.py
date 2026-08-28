from fastapi import FastAPI
from app.schemas.ticket import TicketRequest 
from app.services.classifier import classify_ticket


app = FastAPI()



@app.post("/classify")
def classify(ticket: TicketRequest):
    return classify_ticket(ticket.text)

