from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.ai import NextQuestionResult, ReportResult, ResumeAnalysis
from app.services.ai.deepseek_provider import DeepSeekProvider
from app.services.ai.doubao_provider import DoubaoProvider
from app.services.ai.mock_provider import MockProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.prompts import build_next_question_prompt, build_report_prompt, build_resume_analysis_prompt
from app.services.ai.tongyi_provider import TongyiProvider


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockProvider()
        self.provider_name = self.settings.llm_provider.lower()
        self.provider = self._build_provider()

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

    async def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        if self.provider_name == "mock" or self.provider is None:
            return self.mock.analyze_resume(resume_text)
        prompt = build_resume_analysis_prompt(resume_text)
        try:
            data = await self.provider.complete_json(prompt)  # type: ignore[union-attr]
            return ResumeAnalysis.model_validate(data)
        except (ValidationError, Exception):
            return self.mock.analyze_resume(resume_text)

    async def generate_next_question(
        self,
        interview: dict,
        resume_analysis: dict,
        messages: list[dict],
        latest_answer: str,
        stage: str,
    ) -> NextQuestionResult:
        if self.provider_name == "mock" or self.provider is None:
            return self.mock.generate_next_question(len([m for m in messages if m["role"] == "candidate"]), stage, latest_answer)
        prompt = build_next_question_prompt(interview, resume_analysis, messages, latest_answer, stage)
        try:
            data = await self.provider.complete_json(prompt)  # type: ignore[union-attr]
            result = NextQuestionResult.model_validate(data)
            result.stage = stage
            return result
        except (ValidationError, Exception):
            return self.mock.generate_next_question(len([m for m in messages if m["role"] == "candidate"]), stage, latest_answer)

    async def generate_report(self, interview: dict, resume_analysis: dict, messages: list[dict]) -> ReportResult:
        if self.provider_name == "mock" or self.provider is None:
            return self.mock.generate_report()
        prompt = build_report_prompt(interview, resume_analysis, messages)
        try:
            data = await self.provider.complete_json(prompt)  # type: ignore[union-attr]
            return ReportResult.model_validate(data)
        except (ValidationError, Exception):
            return self.mock.generate_report()
