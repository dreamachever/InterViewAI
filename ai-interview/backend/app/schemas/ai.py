from pydantic import BaseModel, Field


class ResumeProjectAnalysis(BaseModel):
    name: str
    description: str
    possible_questions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    summary: str
    education: str
    projects: list[ResumeProjectAnalysis] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_focus: list[str] = Field(default_factory=list)


class NextQuestionResult(BaseModel):
    answer_quality: str = "medium"
    detected_issues: list[str] = Field(default_factory=list)
    action: str = "next_question"
    stage: str = "RESUME_DEEP_DIVE"
    interviewer_reply: str
    brief_feedback: str = ""


class ExperienceQuestionCategory(BaseModel):
    category: str
    frequency: str = "medium"
    questions: list[str] = Field(default_factory=list)


class ExperienceRealQuestion(BaseModel):
    question: str
    category: str | None = None
    difficulty: str | None = None
    source_context: str | None = None


class ExperienceRiskPoint(BaseModel):
    level: str = "medium"
    point: str
    suggestion: str | None = None


class ExperienceTimelineItem(BaseModel):
    step: str
    estimated_minutes: int | None = None
    notes: str | None = None


class ExperienceInsightResult(BaseModel):
    summary: str = ""
    interview_process: list[str] = Field(default_factory=list)
    question_categories: list[ExperienceQuestionCategory] = Field(default_factory=list)
    real_questions: list[ExperienceRealQuestion] = Field(default_factory=list)
    focus_points: list[str] = Field(default_factory=list)
    risk_points: list[ExperienceRiskPoint] = Field(default_factory=list)
    suggested_strategy: list[str] = Field(default_factory=list)
    timeline: list[ExperienceTimelineItem] = Field(default_factory=list)


class DimensionScore(BaseModel):
    score: int
    max: int
    comment: str


class QuestionReview(BaseModel):
    question: str
    answer_summary: str
    score: int
    comment: str
    improved_answer_suggestion: str


class ReportResult(BaseModel):
    total_score: int
    dimension_scores: dict[str, DimensionScore]
    overall_comment: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    resume_risks: list[str] = Field(default_factory=list)
    question_reviews: list[QuestionReview] = Field(default_factory=list)
    next_training_plan: list[str] = Field(default_factory=list)


class ResumeSuggestion(BaseModel):
    priority: str = "medium"
    problem: str
    advice: str
    example: str | None = None


class ResumeSectionReview(BaseModel):
    section: str
    score: int
    comment: str


class ResumeDiagnosticResult(BaseModel):
    overall_score: int
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[ResumeSuggestion] = Field(default_factory=list)
    section_reviews: list[ResumeSectionReview] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
