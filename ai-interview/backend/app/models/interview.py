import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.experience import interview_experience_links


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    resume_id: Mapped[str | None] = mapped_column(String, ForeignKey("resumes.id"), nullable=True, index=True)
    llm_config_id: Mapped[str | None] = mapped_column(String, ForeignKey("user_llm_configs.id"), nullable=True, index=True)
    llm_provider_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    llm_model_used: Mapped[str | None] = mapped_column(String(255), nullable=True)
    voice_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    interviewer_style: Mapped[str] = mapped_column(String(50), nullable=False)
    target_school: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_major: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    resume_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    interview_plan: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS")
    current_stage: Mapped[str] = mapped_column(String(50), default="SELF_INTRODUCTION")
    total_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="interviews")
    messages = relationship("Message", back_populates="interview", cascade="all, delete-orphan", order_by="Message.created_at")
    report = relationship("Report", back_populates="interview", cascade="all, delete-orphan", uselist=False)
    experiences = relationship("InterviewExperience", secondary=interview_experience_links, back_populates="interviews")
