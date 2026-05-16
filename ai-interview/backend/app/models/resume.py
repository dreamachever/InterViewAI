import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parsed_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    parse_status: Mapped[str] = mapped_column(String(50), default="success")
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    diagnostics = relationship(
        "ResumeDiagnostic",
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="desc(ResumeDiagnostic.created_at)",
    )

    @property
    def latest_diagnostic(self):
        return self.diagnostics[0] if self.diagnostics else None

    @property
    def analysis_status(self) -> str:
        latest = self.latest_diagnostic
        if not latest:
            return "none"
        if self.updated_at and latest.created_at and self.updated_at > latest.created_at:
            return "outdated"
        return "success"

    @property
    def latest_overall_score(self) -> int | None:
        latest = self.latest_diagnostic
        return latest.overall_score if latest else None

    @property
    def high_risks(self) -> list[str]:
        latest = self.latest_diagnostic
        if not latest:
            return []
        high = [
            item.get("problem", "")
            for item in latest.suggestions_json
            if isinstance(item, dict) and item.get("priority") == "high" and item.get("problem")
        ]
        if high:
            return high[:3]
        return [str(item) for item in latest.weaknesses_json[:3]]
