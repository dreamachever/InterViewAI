from datetime import datetime

from pydantic import BaseModel, Field


class QuestionCategoryItem(BaseModel):
    category: str
    frequency: str = "medium"
    questions: list[str] = Field(default_factory=list)


class RealQuestionItem(BaseModel):
    question: str
    category: str | None = None
    difficulty: str | None = None
    source_context: str | None = None


class RiskPointItem(BaseModel):
    level: str = "medium"
    point: str
    suggestion: str | None = None


class TimelineItem(BaseModel):
    step: str
    estimated_minutes: int | None = None
    notes: str | None = None


class ExperienceInsightResult(BaseModel):
    summary: str = ""
    interview_process: list[str] = Field(default_factory=list)
    question_categories: list[QuestionCategoryItem] = Field(default_factory=list)
    real_questions: list[RealQuestionItem] = Field(default_factory=list)
    focus_points: list[str] = Field(default_factory=list)
    risk_points: list[RiskPointItem] = Field(default_factory=list)
    suggested_strategy: list[str] = Field(default_factory=list)
    timeline: list[TimelineItem] = Field(default_factory=list)


class ExperienceImportTextRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    source_url: str | None = Field(default=None, max_length=1024)
    target_school: str | None = Field(default=None, max_length=255)
    target_major: str | None = Field(default=None, max_length=255)
    target_lab: str | None = Field(default=None, max_length=255)
    target_teacher: str | None = Field(default=None, max_length=255)
    interview_type: str | None = Field(default=None, max_length=100)
    year: int | None = Field(default=None, ge=2000, le=2100)
    raw_content: str = Field(min_length=20)
    llm_config_id: str | None = None


class ExperienceUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    source_url: str | None = Field(default=None, max_length=1024)
    target_school: str | None = Field(default=None, max_length=255)
    target_major: str | None = Field(default=None, max_length=255)
    target_lab: str | None = Field(default=None, max_length=255)
    target_teacher: str | None = Field(default=None, max_length=255)
    interview_type: str | None = Field(default=None, max_length=100)
    year: int | None = Field(default=None, ge=2000, le=2100)
    raw_content: str | None = Field(default=None, min_length=20)


class ExperienceExtractRequest(BaseModel):
    llm_config_id: str | None = None


class ExperienceSearchWebRequest(BaseModel):
    keyword: str | None = Field(default=None, min_length=2, max_length=100)
    target_school: str | None = Field(default=None, max_length=255)
    target_major: str | None = Field(default=None, max_length=255)
    target_lab: str | None = Field(default=None, max_length=255)
    target_teacher: str | None = Field(default=None, max_length=255)
    interview_type: str | None = Field(default=None, max_length=100)
    year: int | None = Field(default=None, ge=2000, le=2100)
    max_results: int = Field(default=5, ge=1, le=10)


class ExperienceSearchResultItem(BaseModel):
    title: str
    url: str
    source_site: str | None = None
    snippet: str = ""
    raw_content: str = ""
    published_date: str | None = None
    score: float | None = None


class ExperienceImportWebRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    source_url: str = Field(min_length=8, max_length=1024)
    source_site: str | None = Field(default=None, max_length=255)
    snippet: str | None = None
    raw_content: str = Field(min_length=20)
    target_school: str | None = Field(default=None, max_length=255)
    target_major: str | None = Field(default=None, max_length=255)
    target_lab: str | None = Field(default=None, max_length=255)
    target_teacher: str | None = Field(default=None, max_length=255)
    interview_type: str | None = Field(default=None, max_length=100)
    year: int | None = Field(default=None, ge=2000, le=2100)
    llm_config_id: str | None = None


class ExperienceInsightOut(BaseModel):
    id: str
    experience_id: str
    user_id: str
    provider: str
    model: str | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None
    interview_process_json: list = Field(default_factory=list)
    question_categories_json: list = Field(default_factory=list)
    real_questions_json: list = Field(default_factory=list)
    focus_points_json: list = Field(default_factory=list)
    risk_points_json: list = Field(default_factory=list)
    suggested_strategy_json: list = Field(default_factory=list)
    timeline_json: list = Field(default_factory=list)
    raw_result_json: dict = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class ExperienceListItem(BaseModel):
    id: str
    title: str
    source_type: str
    source_url: str | None = None
    source_site: str | None = None
    target_school: str | None = None
    target_major: str | None = None
    target_lab: str | None = None
    target_teacher: str | None = None
    interview_type: str | None = None
    year: int | None = None
    summary: str | None = None
    extract_status: str
    extract_error: str | None = None
    real_question_count: int = 0
    focus_preview: list[str] = Field(default_factory=list)
    high_risk_preview: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExperienceDetail(ExperienceListItem):
    raw_content: str
    latest_insight: ExperienceInsightOut | None = None


class ExperienceImportResponse(BaseModel):
    experience_id: str
    extract_status: str


class ExperienceSearchWebResponse(BaseModel):
    provider: str
    query_used: str
    message: str | None = None
    results: list[ExperienceSearchResultItem] = Field(default_factory=list)


class InterviewExperienceReference(BaseModel):
    id: str
    title: str
    target_school: str | None = None
    target_major: str | None = None
    interview_type: str | None = None
    year: int | None = None
    summary: str | None = None
    real_question_count: int = 0
    focus_preview: list[str] = Field(default_factory=list)
    high_risk_preview: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
