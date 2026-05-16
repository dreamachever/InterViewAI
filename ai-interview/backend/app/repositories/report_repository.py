from sqlalchemy.orm import Session

from app.models.report import Report


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update(self, report: Report) -> Report:
        existing = self.get_by_interview(report.interview_id)
        if existing:
            existing.total_score = report.total_score
            existing.provider = report.provider
            existing.model = report.model
            existing.dimension_scores = report.dimension_scores
            existing.overall_comment = report.overall_comment
            existing.strengths = report.strengths
            existing.weaknesses = report.weaknesses
            existing.resume_risks = report.resume_risks
            existing.question_reviews = report.question_reviews
            existing.next_training_plan = report.next_training_plan
            existing.full_report = report.full_report
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_interview(self, interview_id: str) -> Report | None:
        return self.db.query(Report).filter(Report.interview_id == interview_id).first()
