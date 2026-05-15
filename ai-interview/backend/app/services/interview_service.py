from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.models.message import Message
from app.repositories.interview_repository import InterviewRepository
from app.repositories.message_repository import MessageRepository
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

    async def create_interview(self, payload: InterviewCreate, user_id: str) -> tuple[Interview, Message]:
        analysis = await self.resume_service.analyze(payload.resume_text)
        interview = Interview(
            **payload.model_dump(),
            user_id=user_id,
            resume_analysis=analysis.model_dump(),
            interview_plan={"source": "resume_analysis"},
        )
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

        ai_result = await self.llm.generate_next_question(
            self._interview_payload(interview),
            interview.resume_analysis or {},
            [self._message_payload(m) for m in messages],
            answer,
            stage_for_answer,
        )
        controlled_stage, action = resolve_stage(stage_for_answer, messages, ai_result.action)
        if action != "end_interview" and controlled_stage != stage_for_answer:
            ai_result = await self.llm.generate_next_question(
                self._interview_payload(interview),
                interview.resume_analysis or {},
                [self._message_payload(m) for m in messages],
                answer,
                controlled_stage,
            )
            ai_result.stage = controlled_stage
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
        }

    @staticmethod
    def _message_payload(message: Message) -> dict:
        return {
            "role": message.role,
            "content": message.content,
            "stage": message.stage,
            "created_at": message.created_at.isoformat(),
        }
