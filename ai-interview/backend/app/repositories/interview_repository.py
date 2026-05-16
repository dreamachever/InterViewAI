from sqlalchemy.orm import Session

from app.models.interview import Interview


class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, interview: Interview) -> Interview:
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def get(self, interview_id: str) -> Interview | None:
        return self.db.get(Interview, interview_id)

    def get_for_user(self, interview_id: str, user_id: str) -> Interview | None:
        return self.db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user_id).first()

    def list_for_user(self, user_id: str) -> list[Interview]:
        return (
            self.db.query(Interview)
            .filter(Interview.user_id == user_id)
            .order_by(Interview.created_at.desc())
            .all()
        )

    def save(self, interview: Interview) -> Interview:
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def delete(self, interview: Interview) -> None:
        self.db.delete(interview)
        self.db.commit()
