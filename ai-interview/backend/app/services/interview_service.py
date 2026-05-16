from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.models.message import Message
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.llm_config_repository import LLMConfigRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.interview import InterviewCreate
from app.schemas.message import AnswerResponse
from app.services.ai.llm_service import LLMService
from app.services.resume_service import ResumeService
from app.services.state_machine import resolve_stage, should_force_finish


FIRST_QUESTION = "请先做一个 1 分钟自我介绍，并重点说明你的核心经历和申请动机。"


class InterviewService:
    def __init__(self, db: Session, llm: LLMService):
        self.db = db
        self.llm = llm
        self.resume_service = ResumeService(llm)
        self.interviews = InterviewRepository(db)
        self.messages = MessageRepository(db)
        self.resumes = ResumeRepository(db)
        self.experiences = ExperienceRepository(db)
        self.llm_configs = LLMConfigRepository(db)

    async def create_interview(self, payload: InterviewCreate, user_id: str) -> tuple[Interview, Message]:
        resume_text = payload.resume_text or ""
        if payload.resume_id:
            resume = self.resumes.get_for_user(payload.resume_id, user_id)
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")
            resume_text = resume.parsed_text
        if payload.llm_config_id and not self.llm_configs.get_for_user(payload.llm_config_id, user_id):
            raise HTTPException(status_code=404, detail="LLM config not found")
        linked_experiences = self._resolve_linked_experiences(payload.experience_ids, user_id)
        analysis = await self.llm.analyze_resume(resume_text, self.db, user_id, payload.llm_config_id)
        provider, model = self.llm.provider_meta()
        interview = Interview(
            **payload.model_dump(exclude={"resume_text", "experience_ids"}),
            user_id=user_id,
            resume_text=resume_text,
            resume_analysis=analysis.model_dump(),
            interview_plan={
                "source": "resume_analysis",
                "resume_source": "uploaded_resume" if payload.resume_id else "pasted_text",
                "experience_ids": [item.id for item in linked_experiences],
                "experience_count": len(linked_experiences),
            },
            llm_provider_used=provider,
            llm_model_used=model,
        )
        interview.experiences = linked_experiences
        interview = self.interviews.create(interview)
        first_message = self.messages.create(
            Message(interview_id=interview.id, role="interviewer", content=FIRST_QUESTION, stage=interview.current_stage)
        )
        return interview, first_message

    def list_for_user(self, user_id: str) -> list[Interview]:
        return self.interviews.list_for_user(user_id)

    def get_detail(self, interview_id: str, user_id: str) -> Interview:
        interview = self.interviews.get_for_user(interview_id, user_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        return interview

    def delete_interview(self, interview_id: str, user_id: str) -> None:
        interview = self.get_detail(interview_id, user_id)
        self.interviews.delete(interview)

    async def answer(self, interview_id: str, answer: str, user_id: str) -> AnswerResponse:
        interview = self.get_detail(interview_id, user_id)
        if interview.status != "IN_PROGRESS":
            raise HTTPException(status_code=400, detail="Interview is not in progress")
        if not answer.strip():
            raise HTTPException(status_code=422, detail="Answer cannot be empty")

        stage_for_answer = interview.current_stage
        self.messages.create(Message(interview_id=interview.id, role="candidate", content=answer.strip(), stage=stage_for_answer))
        messages = self.messages.list_by_interview(interview.id)

        if should_force_finish(messages):
            reply = "本次模拟面试轮次已经达到上限。建议你现在结束面试并生成报告。"
            self.messages.create(Message(interview_id=interview.id, role="interviewer", content=reply, stage=stage_for_answer))
            return AnswerResponse(reply=reply, stage=stage_for_answer, action="end_interview")

        experience_context = self._experience_context(interview)
        ai_result = await self.llm.generate_next_question(
            self._interview_payload(interview),
            interview.resume_analysis or {},
            [self._message_payload(m) for m in messages],
            answer,
            stage_for_answer,
            experience_context,
            self.db,
            user_id,
            interview.llm_config_id,
        )
        provider, model = self.llm.provider_meta()
        interview.llm_provider_used = provider
        interview.llm_model_used = model
        controlled_stage, action = resolve_stage(stage_for_answer, messages, ai_result.action)
        if action != "end_interview" and controlled_stage != stage_for_answer:
            ai_result = await self.llm.generate_next_question(
                self._interview_payload(interview),
                interview.resume_analysis or {},
                [self._message_payload(m) for m in messages],
                answer,
                controlled_stage,
                experience_context,
                self.db,
                user_id,
                interview.llm_config_id,
            )
            ai_result.stage = controlled_stage
            provider, model = self.llm.provider_meta()
            interview.llm_provider_used = provider
            interview.llm_model_used = model
        interview.current_stage = controlled_stage
        self.interviews.save(interview)

        interviewer_message = self.messages.create(
            Message(
                interview_id=interview.id,
                role="interviewer",
                content=ai_result.interviewer_reply,
                stage=controlled_stage,
                answer_quality=ai_result.answer_quality,
                detected_issues=ai_result.detected_issues,
                brief_feedback=ai_result.brief_feedback,
            )
        )
        return AnswerResponse(reply=interviewer_message.content, stage=controlled_stage, action=action)

    @staticmethod
    def _interview_payload(interview: Interview) -> dict:
        return {
            "type": interview.type,
            "interviewer_style": interview.interviewer_style,
            "target_school": interview.target_school,
            "target_major": interview.target_major,
            "current_stage": interview.current_stage,
            "linked_experience_count": len(interview.experiences or []),
        }

    @staticmethod
    def _message_payload(message: Message) -> dict:
        return {
            "role": message.role,
            "content": message.content,
            "stage": message.stage,
            "created_at": message.created_at.isoformat(),
        }

    def _resolve_linked_experiences(self, experience_ids: list[str], user_id: str):
        if not experience_ids:
            return []
        unique_ids = list(dict.fromkeys(experience_ids))
        if len(unique_ids) > 3:
            raise HTTPException(status_code=422, detail="At most 3 experiences can be selected")
        experiences = self.experiences.list_for_user_by_ids(unique_ids, user_id)
        if len(experiences) != len(unique_ids):
            raise HTTPException(status_code=404, detail="One or more experiences not found")
        experiences_by_id = {item.id: item for item in experiences}
        return [experiences_by_id[item_id] for item_id in unique_ids]

    @staticmethod
    def _experience_context(interview: Interview) -> list[dict]:
        context = []
        for experience in interview.experiences or []:
            latest = experience.latest_insight
            if not latest:
                continue
            context.append(
                {
                    "title": experience.title,
                    "target_school": experience.target_school,
                    "target_major": experience.target_major,
                    "interview_type": experience.interview_type,
                    "year": experience.year,
                    "summary": experience.summary,
                    "interview_process": latest.interview_process_json or [],
                    "question_categories": latest.question_categories_json or [],
                    "real_questions": latest.real_questions_json or [],
                    "focus_points": latest.focus_points_json or [],
                    "risk_points": latest.risk_points_json or [],
                    "suggested_strategy": latest.suggested_strategy_json or [],
                    "timeline": latest.timeline_json or [],
                }
            )
        return context
