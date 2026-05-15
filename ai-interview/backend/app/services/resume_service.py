from app.schemas.ai import ResumeAnalysis
from app.services.ai.llm_service import LLMService


class ResumeService:
    def __init__(self, llm: LLMService):
        self.llm = llm

    async def analyze(self, resume_text: str) -> ResumeAnalysis:
        return await self.llm.analyze_resume(resume_text)
