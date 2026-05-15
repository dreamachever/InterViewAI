from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.report import Report
from app.repositories.interview_repository import InterviewRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.ai import ReportResult
from app.services.ai.llm_service import LLMService


class ReportService:
    def __init__(self, db: Session, llm: LLMService):
        self.db = db
        self.llm = llm
        self.interviews = InterviewRepository(db)
        self.messages = MessageRepository(db)
        self.reports = ReportRepository(db)

    async def generate_for_interview(self, interview_id: str) -> Report:
        interview = self.interviews.get(interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        messages = self.messages.list_by_interview(interview_id)
        result = await self.llm.generate_report(
            self._interview_payload(interview),
            interview.resume_analysis or {},
            [self._message_payload(m) for m in messages],
        )
        report = self._to_report(interview_id, result)
        saved = self.reports.create_or_update(report)
        interview.status = "FINISHED"
        interview.total_score = saved.total_score
        self.interviews.save(interview)
        return saved

    def get_report(self, interview_id: str) -> Report:
        report = self.reports.get_by_interview(interview_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report

    @staticmethod
    def _to_report(interview_id: str, result: ReportResult) -> Report:
        data = result.model_dump()
        return Report(interview_id=interview_id, full_report=data, **data)

    @staticmethod
    def _interview_payload(interview) -> dict:
        return {
            "type": interview.type,
            "interviewer_style": interview.interviewer_style,
            "target_school": interview.target_school,
            "target_company": interview.target_company,
            "target_major": interview.target_major,
            "target_position": interview.target_position,
            "current_stage": interview.current_stage,
        }

    @staticmethod
    def _message_payload(message) -> dict:
        return {
            "role": message.role,
            "content": message.content,
            "stage": message.stage,
            "answer_quality": message.answer_quality,
            "brief_feedback": message.brief_feedback,
        }
