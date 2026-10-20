from fastapi import FastAPI, HTTPException

from app.schemas.ticket import (
    TicketRequest,
    TicketResponse,
    ClassificationHistory
)

from app.services.persistence import save_classification, get_classifications
from app.services.llm_classifier import (
    classify_ticket_with_llm,
    PROMPT_VERSION,
    InvalidLLMResponseError
)
from app.services.classifier import classify_ticket
from openai import APIConnectionError, RateLimitError, InternalServerError
from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.services.ticket_assistant import ask_about_ticket


app = FastAPI()


@app.post("/classify", response_model=TicketResponse)
def classify(ticket: TicketRequest):
    classification: TicketResponse
    errors = (
        APIConnectionError,
        RateLimitError,
        InternalServerError,
        InvalidLLMResponseError
    )

    try:
        result = classify_ticket_with_llm(ticket.text)
        classification = result.classification
    except errors:
        result = None
        classification = TicketResponse(**classify_ticket(ticket.text))

    save_classification(
        text=ticket.text,
        category=classification.category,
        priority=classification.priority,
        summary=classification.summary,
        entities=classification.entities,
        prompt_version=PROMPT_VERSION if result is not None else 0,
        model_name=result.model_name if result is not None else None,
        input_tokens=result.input_tokens if result is not None else None,
        output_tokens=result.output_tokens if result is not None else None,
        total_tokens=result.total_tokens if result is not None else None,
        latency_ms=result.latency_ms if result is not None else None,
        cost_usd=result.cost_usd if result is not None else None
    )

    return classification


@app.get("/history/{ticket_id}", response_model=list[ClassificationHistory])
def history(ticket_id: int):
    return get_classifications(ticket_id)


@app.post("/assistant/ask", response_model=AssistantResponse)
def ask_assistant(request: AssistantRequest):
    try:
        response = ask_about_ticket(request.question)
    except (APIConnectionError, RateLimitError, InternalServerError) as e:
        raise HTTPException(
            status_code=503,
            detail="Assistant temporarily unavailable"
        ) from e

    answer = AssistantResponse(answer=response.output_text)
    return answer
