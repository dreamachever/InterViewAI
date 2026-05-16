from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.encryption import decrypt_secret
from app.models.user_llm_config import UserLLMConfig
from app.repositories.llm_config_repository import LLMConfigRepository
from app.schemas.ai import ExperienceInsightResult, NextQuestionResult, ReportResult, ResumeAnalysis, ResumeDiagnosticResult
from app.services.ai.deepseek_provider import DeepSeekProvider
from app.services.ai.doubao_provider import DoubaoProvider
from app.services.ai.mock_provider import MockProvider
from app.services.ai.openai_compatible_provider import OpenAICompatibleProvider, ProviderOptions
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.prompts import (
    build_experience_extract_prompt,
    build_next_question_prompt,
    build_report_prompt,
    build_resume_analysis_prompt,
    build_resume_diagnostic_prompt,
)
from app.services.ai.tongyi_provider import TongyiProvider


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockProvider()
        self.provider_name = self.settings.llm_provider.lower()
        self.provider = self._build_provider()
        self.last_provider_used = self.provider_name if self.provider_name == "mock" or self.provider is not None else "mock"
        self.last_model_used = self._system_model_name(self.last_provider_used)
        self.last_fallback_used = False
        self.last_fallback_reason: str | None = None

    def _build_provider(self):
        providers = {
            "openai": OpenAIProvider,
            "deepseek": DeepSeekProvider,
            "tongyi": TongyiProvider,
            "doubao": DoubaoProvider,
        }
        provider_cls = providers.get(self.provider_name)
        if not provider_cls:
            return None
        try:
            return provider_cls(self.settings)
        except ValueError:
            return None

    def resolve_runtime(self, db: Session | None, user_id: str | None, llm_config_id: str | None = None):
        if not db or not user_id:
            self.last_provider_used = self.provider_name if self.provider_name == "mock" or self.provider is not None else "mock"
            self.last_model_used = self._system_model_name(self.last_provider_used)
            return self.provider
        configs = LLMConfigRepository(db)
        config = configs.get_for_user(llm_config_id, user_id) if llm_config_id else configs.get_default_for_user(user_id)
        if not config:
            self.last_provider_used = self.provider_name if self.provider_name == "mock" or self.provider is not None else "mock"
            self.last_model_used = self._system_model_name(self.last_provider_used)
            return self.provider
        try:
            provider = self.build_provider_from_config(config, decrypt_secret(config.encrypted_api_key))
        except Exception:
            provider = None
        self.last_provider_used = config.provider if provider is not None or config.provider == "mock" else "mock"
        self.last_model_used = config.model
        return provider

    def build_provider_from_config(self, config: UserLLMConfig, api_key: str | None):
        provider_name = config.provider.lower()
        if provider_name == "mock":
            return None
        base_urls = {
            "openai": config.base_url or "https://api.openai.com/v1",
            "deepseek": config.base_url or "https://api.deepseek.com",
            "tongyi": config.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "doubao": config.base_url or "https://ark.cn-beijing.volces.com/api/v3",
            "custom_openai_compatible": config.base_url or "",
        }
        return OpenAICompatibleProvider(
            ProviderOptions(
                name=provider_name,
                api_key=api_key,
                base_url=base_urls.get(provider_name, config.base_url or ""),
                model=config.model or "",
                api_key_env="USER_LLM_API_KEY",
            )
        )

    def provider_meta(self) -> tuple[str, str | None]:
        return self.last_provider_used, self.last_model_used

    def fallback_meta(self) -> tuple[bool, str | None]:
        return self.last_fallback_used, self.last_fallback_reason

    def _mark_success(self, provider_name: str | None = None, model_name: str | None = None) -> None:
        if provider_name is not None:
            self.last_provider_used = provider_name
        if model_name is not None:
            self.last_model_used = model_name
        self.last_fallback_used = False
        self.last_fallback_reason = None

    def _mark_mock(self, reason: str | None = None) -> None:
        self.last_provider_used = "mock"
        self.last_model_used = None
        self.last_fallback_used = bool(reason)
        self.last_fallback_reason = reason

    @staticmethod
    def _safe_error_message(exc: Exception) -> str:
        return str(exc).replace("\n", " ")[:300] or exc.__class__.__name__

    async def analyze_resume(
        self,
        resume_text: str,
        db: Session | None = None,
        user_id: str | None = None,
        llm_config_id: str | None = None,
    ) -> ResumeAnalysis:
        provider = self.resolve_runtime(db, user_id, llm_config_id)
        if provider is None:
            self._mark_mock(None if self.last_provider_used == "mock" else "No usable LLM provider configured")
            return self.mock.analyze_resume(resume_text)
        prompt = build_resume_analysis_prompt(resume_text)
        try:
            data = await provider.complete_json(prompt)
            result = ResumeAnalysis.model_validate(data)
            self._mark_success()
            return result
        except (ValidationError, Exception) as exc:
            attempted_provider = self.last_provider_used
            self._mark_mock(f"{attempted_provider} resume analysis failed: {self._safe_error_message(exc)}")
            return self.mock.analyze_resume(resume_text)

    async def generate_next_question(
        self,
        interview: dict,
        resume_analysis: dict,
        messages: list[dict],
        latest_answer: str,
        stage: str,
        experience_context: list[dict] | None = None,
        db: Session | None = None,
        user_id: str | None = None,
        llm_config_id: str | None = None,
    ) -> NextQuestionResult:
        provider = self.resolve_runtime(db, user_id, llm_config_id)
        candidate_turns = len([m for m in messages if m["role"] == "candidate"])
        if provider is None:
            self._mark_mock(None if self.last_provider_used == "mock" else "No usable LLM provider configured")
            return self.mock.generate_next_question(candidate_turns, stage, latest_answer, experience_context)
        prompt = build_next_question_prompt(interview, resume_analysis, messages, latest_answer, stage, experience_context)
        try:
            data = await provider.complete_json(prompt)
            result = NextQuestionResult.model_validate(data)
            result.stage = stage
            self._mark_success()
            return result
        except (ValidationError, Exception) as exc:
            attempted_provider = self.last_provider_used
            self._mark_mock(f"{attempted_provider} next question failed: {self._safe_error_message(exc)}")
            return self.mock.generate_next_question(candidate_turns, stage, latest_answer, experience_context)

    async def generate_report(
        self,
        interview: dict,
        resume_analysis: dict,
        messages: list[dict],
        db: Session | None = None,
        user_id: str | None = None,
        llm_config_id: str | None = None,
    ) -> ReportResult:
        provider = self.resolve_runtime(db, user_id, llm_config_id)
        if provider is None:
            self._mark_mock(None if self.last_provider_used == "mock" else "No usable LLM provider configured")
            return self.mock.generate_report()
        prompt = build_report_prompt(interview, resume_analysis, messages)
        try:
            data = await provider.complete_json(prompt)
            result = ReportResult.model_validate(data)
            self._mark_success()
            return result
        except (ValidationError, Exception) as exc:
            attempted_provider = self.last_provider_used
            self._mark_mock(f"{attempted_provider} report failed: {self._safe_error_message(exc)}")
            return self.mock.generate_report()

    async def diagnose_resume(
        self,
        resume_text: str,
        db: Session | None = None,
        user_id: str | None = None,
        llm_config_id: str | None = None,
    ) -> ResumeDiagnosticResult:
        provider = self.resolve_runtime(db, user_id, llm_config_id)
        if provider is None:
            self._mark_mock(None if self.last_provider_used == "mock" else "No usable LLM provider configured")
            return self.mock.diagnose_resume()
        prompt = build_resume_diagnostic_prompt(resume_text)
        try:
            data = await provider.complete_json(prompt)
            result = ResumeDiagnosticResult.model_validate(data)
            self._mark_success()
            return result
        except (ValidationError, Exception) as exc:
            attempted_provider = self.last_provider_used
            self._mark_mock(f"{attempted_provider} resume diagnosis failed: {self._safe_error_message(exc)}")
            return self.mock.diagnose_resume()

    async def extract_experience_insights(
        self,
        raw_content: str,
        metadata: dict,
        db: Session | None = None,
        user_id: str | None = None,
        llm_config_id: str | None = None,
    ) -> ExperienceInsightResult:
        provider = self.resolve_runtime(db, user_id, llm_config_id)
        if provider is None:
            self._mark_mock(None if self.last_provider_used == "mock" else "No usable LLM provider configured")
            return self.mock.extract_experience_insights(raw_content, metadata)
        prompt = build_experience_extract_prompt(raw_content, metadata)
        try:
            data = await provider.complete_json(prompt)
            result = ExperienceInsightResult.model_validate(data)
            self._mark_success()
            return result
        except (ValidationError, Exception) as exc:
            attempted_provider = self.last_provider_used
            self._mark_mock(f"{attempted_provider} experience extract failed: {self._safe_error_message(exc)}")
            return self.mock.extract_experience_insights(raw_content, metadata)

    def _system_model_name(self, provider_name: str) -> str | None:
        return {
            "openai": self.settings.openai_model,
            "deepseek": self.settings.deepseek_model,
            "tongyi": self.settings.tongyi_model,
            "doubao": self.settings.doubao_model,
        }.get(provider_name)
