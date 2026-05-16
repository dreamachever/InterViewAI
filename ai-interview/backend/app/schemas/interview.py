from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.message import MessageOut


class InterviewCreate(BaseModel):
    type: str
    interviewer_style: str
    target_school: str | None = None
    target_company: str | None = None
    target_major: str | None = None
    target_position: str | None = None
    resume_text: str | None = Field(default=None, min_length=10)
    resume_id: str | None = None
    llm_config_id: str | None = None
    voice_enabled: bool = False

    @model_validator(mode="after")
    def validate_resume_source(self):
        if not self.resume_id and not self.resume_text:
            raise ValueError("Either resume_id or resume_text is required")
        return self


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
    voice_enabled: bool = False
    total_score: int | None = None
    created_at: datetime
    messages: list[MessageOut] = []

    model_config = {"from_attributes": True}


class InterviewListItem(BaseModel):
    id: str
    type: str
    interviewer_style: str
    target_school: str | None = None
    target_major: str | None = None
    status: str
    voice_enabled: bool = False
    total_score: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FinishInterviewResponse(BaseModel):
    report_id: str
    total_score: int
