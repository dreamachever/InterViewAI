from datetime import datetime

from pydantic import BaseModel, Field


class ResumeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    parsed_text: str | None = Field(default=None, min_length=10)
    is_default: bool | None = None


class ResumeOut(BaseModel):
    id: str
    title: str
    original_filename: str
    file_size: int
    content_type: str | None = None
    parse_status: str
    parse_error: str | None = None
    analysis_status: str = "none"
    latest_overall_score: int | None = None
    high_risks: list[str] = Field(default_factory=list)
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeDetail(ResumeOut):
    parsed_text: str


class ResumeDiagnosticOut(BaseModel):
    id: str
    resume_id: str
    provider: str
    model: str | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None
    overall_score: int
    summary: str
    strengths_json: list
    weaknesses_json: list
    suggestions_json: list
    section_reviews_json: list
    follow_up_questions_json: list
    raw_result_json: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeDiagnoseRequest(BaseModel):
    llm_config_id: str | None = None
