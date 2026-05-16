from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.experience import ExperienceInsight, InterviewExperience
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import (
    ExperienceDetail,
    ExperienceExtractRequest,
    ExperienceImportResponse,
    ExperienceImportTextRequest,
    ExperienceImportWebRequest,
    ExperienceInsightResult,
    ExperienceListItem,
    ExperienceSearchWebRequest,
    ExperienceSearchWebResponse,
    ExperienceUpdateRequest,
)
from app.services.ai.llm_service import LLMService
from app.services.experience_search_service import ExperienceSearchService
from app.core.config import get_settings


class ExperienceService:
    def __init__(self, db: Session, llm: LLMService):
        self.db = db
        self.llm = llm
        self.repo = ExperienceRepository(db)
        self.search = ExperienceSearchService(get_settings())

    def list_for_user(
        self,
        user_id: str,
        target_school: str | None = None,
        target_major: str | None = None,
        interview_type: str | None = None,
        source_type: str | None = None,
    ) -> list[InterviewExperience]:
        return self.repo.list_for_user(user_id, target_school, target_major, interview_type, source_type)

    def get_detail(self, experience_id: str, user_id: str) -> InterviewExperience:
        experience = self.repo.get_for_user(experience_id, user_id)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")
        return experience

    async def import_text(
        self,
        payload: ExperienceImportTextRequest,
        user_id: str,
    ) -> ExperienceImportResponse:
        experience = InterviewExperience(
            user_id=user_id,
            title=payload.title,
            source_type="manual",
            source_url=payload.source_url,
            source_site=self._extract_source_site(payload.source_url),
            target_school=payload.target_school,
            target_major=payload.target_major,
            target_lab=payload.target_lab,
            target_teacher=payload.target_teacher,
            interview_type=payload.interview_type,
            year=payload.year,
            raw_content=payload.raw_content,
            extract_status="pending",
            extract_error=None,
        )
        experience = self.repo.create(experience)
        await self.extract(experience.id, user_id, ExperienceExtractRequest(llm_config_id=payload.llm_config_id))
        refreshed = self.get_detail(experience.id, user_id)
        return ExperienceImportResponse(experience_id=refreshed.id, extract_status=refreshed.extract_status)

    async def import_web(
        self,
        payload: ExperienceImportWebRequest,
        user_id: str,
    ) -> ExperienceImportResponse:
        raw_content = (payload.raw_content or "").strip()
        if len(raw_content) < 20:
            raise HTTPException(status_code=422, detail="Imported web content is too short")
        experience = InterviewExperience(
            user_id=user_id,
            title=payload.title,
            source_type="web",
            source_url=payload.source_url,
            source_site=payload.source_site or self._extract_source_site(payload.source_url),
            target_school=payload.target_school,
            target_major=payload.target_major,
            target_lab=payload.target_lab,
            target_teacher=payload.target_teacher,
            interview_type=payload.interview_type,
            year=payload.year,
            raw_content=raw_content,
            summary=(payload.snippet or "").strip()[:500] or None,
            extract_status="pending",
            extract_error=None,
        )
        experience = self.repo.create(experience)
        await self.extract(experience.id, user_id, ExperienceExtractRequest(llm_config_id=payload.llm_config_id))
        refreshed = self.get_detail(experience.id, user_id)
        return ExperienceImportResponse(experience_id=refreshed.id, extract_status=refreshed.extract_status)

    def update(self, experience_id: str, user_id: str, payload: ExperienceUpdateRequest) -> InterviewExperience:
        experience = self.get_detail(experience_id, user_id)
        data = payload.model_dump(exclude_unset=True)
        if "source_url" in data:
            data["source_site"] = self._extract_source_site(data["source_url"])
        raw_content_changed = "raw_content" in data and data["raw_content"] != experience.raw_content
        for field, value in data.items():
            setattr(experience, field, value)
        if raw_content_changed:
            experience.extract_status = "pending"
            experience.extract_error = None
            experience.summary = None
        return self.repo.save(experience)

    def delete(self, experience_id: str, user_id: str) -> None:
        experience = self.get_detail(experience_id, user_id)
        self.repo.clear_links_for_experience(experience.id)
        self.repo.delete(experience)

    async def extract(self, experience_id: str, user_id: str, payload: ExperienceExtractRequest) -> InterviewExperience:
        experience = self.get_detail(experience_id, user_id)
        experience.extract_status = "pending"
        experience.extract_error = None
        self.repo.save(experience)
        try:
            result = await self.llm.extract_experience_insights(
                raw_content=experience.raw_content,
                metadata={
                    "title": experience.title,
                    "source_type": experience.source_type,
                    "source_url": experience.source_url,
                    "source_site": experience.source_site,
                    "target_school": experience.target_school,
                    "target_major": experience.target_major,
                    "target_lab": experience.target_lab,
                    "target_teacher": experience.target_teacher,
                    "interview_type": experience.interview_type,
                    "year": experience.year,
                },
                db=self.db,
                user_id=user_id,
                llm_config_id=payload.llm_config_id,
            )
            provider, model = self.llm.provider_meta()
            fallback_used, fallback_reason = self.llm.fallback_meta()
            insight = ExperienceInsight(
                experience_id=experience.id,
                user_id=user_id,
                provider=provider,
                model=model,
                fallback_used=fallback_used,
                fallback_reason=fallback_reason,
                interview_process_json=result.interview_process,
                question_categories_json=[item.model_dump() for item in result.question_categories],
                real_questions_json=[item.model_dump() for item in result.real_questions],
                focus_points_json=result.focus_points,
                risk_points_json=[item.model_dump() for item in result.risk_points],
                suggested_strategy_json=result.suggested_strategy,
                timeline_json=[item.model_dump() for item in result.timeline],
                raw_result_json=result.model_dump(),
            )
            self.repo.create_insight(insight)
            experience.summary = result.summary
            experience.extract_status = "success"
            experience.extract_error = None
        except Exception as exc:
            experience.extract_status = "failed"
            experience.extract_error = str(exc)[:500]
        return self.repo.save(experience)

    async def search_web(self, payload: ExperienceSearchWebRequest) -> ExperienceSearchWebResponse:
        return await self.search.search(payload)

    @staticmethod
    def _extract_source_site(source_url: str | None) -> str | None:
        if not source_url:
            return None
        try:
            parsed = urlparse(source_url)
            return parsed.netloc or None
        except Exception:
            return None
