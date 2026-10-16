from fastapi import FastAPI

from app.schemas.ticket import (
    TicketRequest,
    TicketResponse,
    ClassificationHistory
    )

from app.services.persistence import save_classification, get_classifications
from app.services.llm_classifier import (
    classify_ticket_with_llm,
    PROMPT_VERSION
    )

app = FastAPI()


@app.post("/classify", response_model=TicketResponse)
def classify(ticket: TicketRequest):

    result = classify_ticket_with_llm(ticket.text)

    save_classification(
        text=ticket.text,
        category=result.classification.category,
        priority=result.classification.priority,
        summary=result.classification.summary,
        entities=result.classification.entities,
        prompt_version=PROMPT_VERSION,
        model_name=result.model_name,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        total_tokens=result.total_tokens,
        latency_ms=result.latency_ms
    )

    return result.classification


@app.get("/history/{ticket_id}", response_model=list[ClassificationHistory])
def history(ticket_id: int):
    return get_classifications(ticket_id)
