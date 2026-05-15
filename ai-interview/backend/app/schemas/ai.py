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
