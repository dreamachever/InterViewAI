from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.interview import FinishInterviewResponse, InterviewCreate, InterviewCreateResponse, InterviewDetail
from app.schemas.message import AnswerCreate, AnswerResponse
from app.schemas.report import ReportOut
from app.services.ai.llm_service import LLMService
from app.services.interview_service import InterviewService
from app.services.report_service import ReportService

router = APIRouter(prefix="/interviews", tags=["interviews"])


def get_llm_service() -> LLMService:
    return LLMService()


@router.post("", response_model=InterviewCreateResponse)
async def create_interview(payload: InterviewCreate, db: Session = Depends(get_db), llm: LLMService = Depends(get_llm_service)):
    interview, first_message = await InterviewService(db, llm).create_interview(payload)
    return InterviewCreateResponse(
        interview_id=interview.id,
        first_question=first_message.content,
        current_stage=interview.current_stage,
    )


@router.get("/{interview_id}", response_model=InterviewDetail)
def get_interview(interview_id: str, db: Session = Depends(get_db), llm: LLMService = Depends(get_llm_service)):
    return InterviewService(db, llm).get_detail(interview_id)


@router.post("/{interview_id}/messages", response_model=AnswerResponse)
async def send_answer(
    interview_id: str,
    payload: AnswerCreate,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
):
    return await InterviewService(db, llm).answer(interview_id, payload.answer)


@router.post("/{interview_id}/finish", response_model=FinishInterviewResponse)
async def finish_interview(interview_id: str, db: Session = Depends(get_db), llm: LLMService = Depends(get_llm_service)):
    report = await ReportService(db, llm).generate_for_interview(interview_id)
    return FinishInterviewResponse(report_id=report.id, total_score=report.total_score)


@router.get("/{interview_id}/report", response_model=ReportOut)
def get_report(interview_id: str, db: Session = Depends(get_db), llm: LLMService = Depends(get_llm_service)):
    return ReportService(db, llm).get_report(interview_id)
