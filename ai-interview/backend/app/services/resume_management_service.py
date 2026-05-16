from pathlib import Path
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.resume_diagnostic import ResumeDiagnostic
from app.repositories.llm_config_repository import LLMConfigRepository
from app.repositories.resume_diagnostic_repository import ResumeDiagnosticRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeUpdate
from app.services.ai.llm_service import LLMService
from app.services.resume_file_service import ResumeFileService
from app.services.resume_parse_service import ResumeParseService


class ResumeManagementService:
    def __init__(self, db: Session, llm: LLMService | None = None):
        self.db = db
        self.llm = llm or LLMService()
        self.resumes = ResumeRepository(db)
        self.diagnostics = ResumeDiagnosticRepository(db)
        self.files = ResumeFileService()
        self.parser = ResumeParseService()

    async def upload(self, file: UploadFile, user_id: str) -> Resume:
        content = await self.files.read_pdf(file)
        parsed_text = self.parser.parse_pdf(content)
        has_default = self.resumes.get_default_for_user(user_id) is not None
        resume = Resume(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=Path(file.filename or "resume.pdf").stem or "Resume",
            original_filename=file.filename or "resume.pdf",
            file_path="",
            file_size=len(content),
            content_type=file.content_type,
            parsed_text=parsed_text,
            parse_status="success",
            is_default=not has_default,
        )
        resume.file_path = self.files.save(user_id, resume.id, content)
        return self.resumes.create(resume)

    def list_for_user(self, user_id: str) -> list[Resume]:
        return self.resumes.list_for_user(user_id)

    def get_detail(self, resume_id: str, user_id: str) -> Resume:
        resume = self.resumes.get_for_user(resume_id, user_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume

    def update(self, resume_id: str, payload: ResumeUpdate, user_id: str) -> Resume:
        resume = self.get_detail(resume_id, user_id)
        if payload.title is not None:
            resume.title = payload.title
        if payload.parsed_text is not None:
            resume.parsed_text = payload.parsed_text.strip()
        if payload.is_default is not None:
            resume.is_default = payload.is_default
        return self.resumes.save(resume)

    def reparse(self, resume_id: str, user_id: str) -> Resume:
        resume = self.get_detail(resume_id, user_id)
        try:
            content = Path(resume.file_path).read_bytes()
            resume.parsed_text = self.parser.parse_pdf(content)
            resume.parse_status = "success"
            resume.parse_error = None
        except Exception as exc:
            resume.parse_status = "failed"
            resume.parse_error = str(exc)
        return self.resumes.save(resume)

    def delete(self, resume_id: str, user_id: str) -> None:
        resume = self.get_detail(resume_id, user_id)
        was_default = resume.is_default
        file_path = resume.file_path
        self.resumes.delete(resume)
        self.files.delete(file_path)
        if was_default:
            next_resume = next(iter(self.resumes.list_for_user(user_id)), None)
            if next_resume:
                next_resume.is_default = True
                self.resumes.save(next_resume)

    async def diagnose(self, resume_id: str, user_id: str, llm_config_id: str | None = None) -> ResumeDiagnostic:
        resume = self.get_detail(resume_id, user_id)
        if llm_config_id and not LLMConfigRepository(self.db).get_for_user(llm_config_id, user_id):
            raise HTTPException(status_code=404, detail="LLM config not found")
        result = await self.llm.diagnose_resume(resume.parsed_text, self.db, user_id, llm_config_id)
        provider, model = self.llm.provider_meta()
        fallback_used, fallback_reason = self.llm.fallback_meta()
        data = result.model_dump()
        diagnostic = ResumeDiagnostic(
            user_id=user_id,
            resume_id=resume.id,
            provider=provider,
            model=model,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            overall_score=result.overall_score,
            summary=result.summary,
            strengths_json=data["strengths"],
            weaknesses_json=data["weaknesses"],
            suggestions_json=data["suggestions"],
            section_reviews_json=data["section_reviews"],
            follow_up_questions_json=data["follow_up_questions"],
            raw_result_json=data,
        )
        return self.diagnostics.create(diagnostic)

    def list_diagnostics(self, resume_id: str, user_id: str) -> list[ResumeDiagnostic]:
        self.get_detail(resume_id, user_id)
        return self.diagnostics.list_for_resume(resume_id, user_id)
