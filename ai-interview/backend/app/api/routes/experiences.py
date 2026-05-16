from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.experience import (
    ExperienceDetail,
    ExperienceExtractRequest,
    ExperienceImportResponse,
    ExperienceImportTextRequest,
    ExperienceImportWebRequest,
    ExperienceListItem,
    ExperienceSearchWebRequest,
    ExperienceSearchWebResponse,
    ExperienceUpdateRequest,
)
from app.services.ai.llm_service import LLMService
from app.services.experience_service import ExperienceService

router = APIRouter(prefix="/experiences", tags=["experiences"])


def get_llm_service() -> LLMService:
    return LLMService()


@router.get("", response_model=list[ExperienceListItem])
def list_experiences(
    target_school: str | None = Query(default=None),
    target_major: str | None = Query(default=None),
    interview_type: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return ExperienceService(db, llm).list_for_user(
        current_user.id,
        target_school=target_school,
        target_major=target_major,
        interview_type=interview_type,
        source_type=source_type,
    )


@router.post("/import-text", response_model=ExperienceImportResponse)
async def import_experience_text(
    payload: ExperienceImportTextRequest,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return await ExperienceService(db, llm).import_text(payload, current_user.id)


@router.post("/search-web", response_model=ExperienceSearchWebResponse)
async def search_web(
    payload: ExperienceSearchWebRequest,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return await ExperienceService(db, llm).search_web(payload)


@router.post("/import-web", response_model=ExperienceImportResponse)
async def import_experience_web(
    payload: ExperienceImportWebRequest,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return await ExperienceService(db, llm).import_web(payload, current_user.id)


@router.get("/{experience_id}", response_model=ExperienceDetail)
def get_experience(
    experience_id: str,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return ExperienceService(db, llm).get_detail(experience_id, current_user.id)


@router.patch("/{experience_id}", response_model=ExperienceDetail)
def update_experience(
    experience_id: str,
    payload: ExperienceUpdateRequest,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return ExperienceService(db, llm).update(experience_id, current_user.id, payload)


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    experience_id: str,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    ExperienceService(db, llm).delete(experience_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{experience_id}/extract", response_model=ExperienceDetail)
async def extract_experience(
    experience_id: str,
    payload: ExperienceExtractRequest,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return await ExperienceService(db, llm).extract(experience_id, current_user.id, payload)
