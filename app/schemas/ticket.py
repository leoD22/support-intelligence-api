from pydantic import BaseModel, Field, ConfigDict


class TicketRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(min_length=1)


class TicketResponse(BaseModel):
    category: str
    priority: int
    summary: str
    entities: list[str]


class ClassificationHistory(BaseModel):
    text: str
    category: str
    priority: int
    summary: str
    entities: list[str]
