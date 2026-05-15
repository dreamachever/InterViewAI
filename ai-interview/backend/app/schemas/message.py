from datetime import datetime

from pydantic import BaseModel


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    stage: str | None = None
    answer_quality: str | None = None
    detected_issues: list[str] | None = None
    brief_feedback: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnswerCreate(BaseModel):
    answer: str


class AnswerResponse(BaseModel):
    reply: str
    stage: str
    action: str
