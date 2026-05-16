from pydantic import BaseModel

from app.schemas.ai import DimensionScore, QuestionReview


class ReportOut(BaseModel):
    id: str | None = None
    interview_id: str | None = None
    provider: str | None = None
    model: str | None = None
    total_score: int
    dimension_scores: dict[str, DimensionScore]
    overall_comment: str
    strengths: list[str]
    weaknesses: list[str]
    resume_risks: list[str]
    question_reviews: list[QuestionReview]
    next_training_plan: list[str]

    model_config = {"from_attributes": True}
