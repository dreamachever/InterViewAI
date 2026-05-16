from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.interview import FinishInterviewResponse, InterviewCreate, InterviewCreateResponse, InterviewDetail, InterviewListItem
from app.schemas.message import AnswerCreate, AnswerResponse
from app.schemas.report import ReportOut
from app.services.ai.llm_service import LLMService
from app.services.interview_service import InterviewService
from app.services.report_service import ReportService

router = APIRouter(prefix="/interviews", tags=["interviews"])


def get_llm_service() -> LLMService:
    return LLMService()


@router.post("", response_model=InterviewCreateResponse)
async def create_interview(
    payload: InterviewCreate,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    interview, first_message = await InterviewService(db, llm).create_interview(payload, current_user.id)
    return InterviewCreateResponse(
        interview_id=interview.id,
        first_question=first_message.content,
        current_stage=interview.current_stage,
    )


@router.get("", response_model=list[InterviewListItem])
def list_interviews(
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return InterviewService(db, llm).list_for_user(current_user.id)


@router.get("/{interview_id}", response_model=InterviewDetail)
def get_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return InterviewService(db, llm).get_detail(interview_id, current_user.id)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    InterviewService(db, llm).delete_interview(interview_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{interview_id}/messages", response_model=AnswerResponse)
async def send_answer(
    interview_id: str,
    payload: AnswerCreate,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return await InterviewService(db, llm).answer(interview_id, payload.answer, current_user.id)


@router.post("/{interview_id}/finish", response_model=FinishInterviewResponse)
async def finish_interview(
    interview_id: str,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    report = await ReportService(db, llm).generate_for_interview(interview_id, current_user.id)
    return FinishInterviewResponse(report_id=report.id, total_score=report.total_score)


@router.get("/{interview_id}/report", response_model=ReportOut)
def get_report(
    interview_id: str,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return ReportService(db, llm).get_report(interview_id, current_user.id)
