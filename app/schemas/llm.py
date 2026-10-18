from decimal import Decimal

from pydantic import BaseModel

from app.schemas.ticket import TicketResponse


class LLMClassificationResult(BaseModel):
    classification: TicketResponse
    model_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    cost_usd: Decimal | None = None
