from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeDetail, ResumeDiagnoseRequest, ResumeDiagnosticOut, ResumeOut, ResumeUpdate
from app.services.ai.llm_service import LLMService
from app.services.resume_management_service import ResumeManagementService

router = APIRouter(prefix="/resumes", tags=["resumes"])


def get_llm_service() -> LLMService:
    return LLMService()


@router.post("/upload", response_model=ResumeDetail)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return await ResumeManagementService(db, llm).upload(file, current_user.id)


@router.get("", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ResumeManagementService(db).list_for_user(current_user.id)


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(resume_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ResumeManagementService(db).get_detail(resume_id, current_user.id)


@router.patch("/{resume_id}", response_model=ResumeDetail)
def update_resume(
    resume_id: str,
    payload: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ResumeManagementService(db).update(resume_id, payload, current_user.id)


@router.post("/{resume_id}/reparse", response_model=ResumeDetail)
def reparse_resume(resume_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ResumeManagementService(db).reparse(resume_id, current_user.id)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ResumeManagementService(db).delete(resume_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{resume_id}/diagnose", response_model=ResumeDiagnosticOut)
async def diagnose_resume(
    resume_id: str,
    payload: ResumeDiagnoseRequest,
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service),
    current_user: User = Depends(get_current_user),
):
    return await ResumeManagementService(db, llm).diagnose(resume_id, current_user.id, payload.llm_config_id)


@router.get("/{resume_id}/diagnostics", response_model=list[ResumeDiagnosticOut])
def list_resume_diagnostics(resume_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ResumeManagementService(db).list_diagnostics(resume_id, current_user.id)
