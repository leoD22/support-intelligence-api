from pydantic import BaseModel


class TicketRequest(BaseModel):
    text: str


class TicketResponse(BaseModel):
    category: str
    priority: int
    summary: str
    entities: list[str]
