from pydantic import BaseModel, Field, ConfigDict


class AssistantRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1)


class AssistantResponse(BaseModel):
    answer: str
