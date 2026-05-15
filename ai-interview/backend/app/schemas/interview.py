from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.message import MessageOut


class InterviewCreate(BaseModel):
    type: str
    interviewer_style: str
    target_school: str | None = None
    target_company: str | None = None
    target_major: str | None = None
    target_position: str | None = None
    resume_text: str = Field(min_length=10)


class InterviewCreateResponse(BaseModel):
    interview_id: str
    first_question: str
    current_stage: str


class InterviewDetail(BaseModel):
    id: str
    type: str
    interviewer_style: str
    target_school: str | None = None
    target_company: str | None = None
    target_major: str | None = None
    target_position: str | None = None
    current_stage: str
    status: str
    total_score: int | None = None
    created_at: datetime
    messages: list[MessageOut] = []

    model_config = {"from_attributes": True}


class FinishInterviewResponse(BaseModel):
    report_id: str
    total_score: int
