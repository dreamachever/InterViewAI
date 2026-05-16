from sqlalchemy.orm import Session

from app.models.resume_diagnostic import ResumeDiagnostic


class ResumeDiagnosticRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_resume(self, resume_id: str, user_id: str) -> list[ResumeDiagnostic]:
        return (
            self.db.query(ResumeDiagnostic)
            .filter(ResumeDiagnostic.resume_id == resume_id, ResumeDiagnostic.user_id == user_id)
            .order_by(ResumeDiagnostic.created_at.desc())
            .all()
        )

    def create(self, diagnostic: ResumeDiagnostic) -> ResumeDiagnostic:
        self.db.add(diagnostic)
        self.db.commit()
        self.db.refresh(diagnostic)
        return diagnostic
