from sqlalchemy import delete
from sqlalchemy.orm import Session, joinedload

from app.models.experience import ExperienceInsight, InterviewExperience, interview_experience_links


class ExperienceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(
        self,
        user_id: str,
        target_school: str | None = None,
        target_major: str | None = None,
        interview_type: str | None = None,
        source_type: str | None = None,
    ) -> list[InterviewExperience]:
        query = self.db.query(InterviewExperience).filter(InterviewExperience.user_id == user_id)
        if target_school:
            query = query.filter(InterviewExperience.target_school.ilike(f"%{target_school}%"))
        if target_major:
            query = query.filter(InterviewExperience.target_major.ilike(f"%{target_major}%"))
        if interview_type:
            query = query.filter(InterviewExperience.interview_type == interview_type)
        if source_type:
            query = query.filter(InterviewExperience.source_type == source_type)
        return query.options(joinedload(InterviewExperience.insights)).order_by(InterviewExperience.created_at.desc()).all()

    def get_for_user(self, experience_id: str, user_id: str) -> InterviewExperience | None:
        return (
            self.db.query(InterviewExperience)
            .options(joinedload(InterviewExperience.insights))
            .filter(InterviewExperience.id == experience_id, InterviewExperience.user_id == user_id)
            .first()
        )

    def list_for_user_by_ids(self, experience_ids: list[str], user_id: str) -> list[InterviewExperience]:
        if not experience_ids:
            return []
        return (
            self.db.query(InterviewExperience)
            .options(joinedload(InterviewExperience.insights))
            .filter(InterviewExperience.user_id == user_id, InterviewExperience.id.in_(experience_ids))
            .all()
        )

    def create(self, experience: InterviewExperience) -> InterviewExperience:
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience

    def save(self, experience: InterviewExperience) -> InterviewExperience:
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience

    def create_insight(self, insight: ExperienceInsight) -> ExperienceInsight:
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def clear_links_for_experience(self, experience_id: str) -> None:
        self.db.execute(delete(interview_experience_links).where(interview_experience_links.c.experience_id == experience_id))
        self.db.commit()

    def delete(self, experience: InterviewExperience) -> None:
        self.db.delete(experience)
        self.db.commit()
