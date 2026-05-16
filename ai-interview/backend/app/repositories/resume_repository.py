from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: str) -> list[Resume]:
        return self.db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).all()

    def get_for_user(self, resume_id: str, user_id: str) -> Resume | None:
        return self.db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()

    def get_default_for_user(self, user_id: str) -> Resume | None:
        return self.db.query(Resume).filter(Resume.user_id == user_id, Resume.is_default.is_(True)).first()

    def clear_default(self, user_id: str, except_id: str | None = None) -> None:
        query = self.db.query(Resume).filter(Resume.user_id == user_id)
        if except_id:
            query = query.filter(Resume.id != except_id)
        query.update({Resume.is_default: False})

    def create(self, resume: Resume) -> Resume:
        if resume.is_default:
            self.clear_default(resume.user_id)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def save(self, resume: Resume) -> Resume:
        if resume.is_default:
            self.clear_default(resume.user_id, resume.id)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def delete(self, resume: Resume) -> None:
        self.db.delete(resume)
        self.db.commit()
