import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


interview_experience_links = Table(
    "interview_experience_links",
    Base.metadata,
    Column("interview_id", String, ForeignKey("interviews.id"), primary_key=True),
    Column("experience_id", String, ForeignKey("interview_experiences.id"), primary_key=True),
)


class InterviewExperience(Base):
    __tablename__ = "interview_experiences"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="manual")
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_site: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_school: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    target_major: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    target_lab: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_teacher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    interview_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    extract_status: Mapped[str] = mapped_column(String(50), default="pending")
    extract_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    insights = relationship("ExperienceInsight", back_populates="experience", cascade="all, delete-orphan", order_by="desc(ExperienceInsight.created_at)")
    interviews = relationship("Interview", secondary=interview_experience_links, back_populates="experiences")

    @property
    def latest_insight(self):
        return self.insights[0] if self.insights else None

    @property
    def real_question_count(self) -> int:
        latest = self.latest_insight
        return len(latest.real_questions_json) if latest else 0

    @property
    def focus_preview(self) -> list[str]:
        latest = self.latest_insight
        return [str(item) for item in latest.focus_points_json[:3]] if latest else []

    @property
    def high_risk_preview(self) -> list[str]:
        latest = self.latest_insight
        if not latest:
            return []
        return [
            str(item.get("point"))
            for item in latest.risk_points_json
            if isinstance(item, dict) and item.get("level") == "high" and item.get("point")
        ][:3]


class ExperienceInsight(Base):
    __tablename__ = "experience_insights"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experience_id: Mapped[str] = mapped_column(String, ForeignKey("interview_experiences.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fallback_used: Mapped[bool] = mapped_column(default=False)
    fallback_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    interview_process_json: Mapped[list] = mapped_column(JSON, default=list)
    question_categories_json: Mapped[list] = mapped_column(JSON, default=list)
    real_questions_json: Mapped[list] = mapped_column(JSON, default=list)
    focus_points_json: Mapped[list] = mapped_column(JSON, default=list)
    risk_points_json: Mapped[list] = mapped_column(JSON, default=list)
    suggested_strategy_json: Mapped[list] = mapped_column(JSON, default=list)
    timeline_json: Mapped[list] = mapped_column(JSON, default=list)
    raw_result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experience = relationship("InterviewExperience", back_populates="insights")
