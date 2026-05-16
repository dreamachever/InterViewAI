import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResumeDiagnostic(Base):
    __tablename__ = "resume_diagnostics"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    resume_id: Mapped[str] = mapped_column(String, ForeignKey("resumes.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    strengths_json: Mapped[list] = mapped_column(JSON, default=list)
    weaknesses_json: Mapped[list] = mapped_column(JSON, default=list)
    suggestions_json: Mapped[list] = mapped_column(JSON, default=list)
    section_reviews_json: Mapped[list] = mapped_column(JSON, default=list)
    follow_up_questions_json: Mapped[list] = mapped_column(JSON, default=list)
    raw_result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="diagnostics")
