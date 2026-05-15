from sqlalchemy.orm import Session

from app.models.message import Message


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message: Message) -> Message:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def list_by_interview(self, interview_id: str) -> list[Message]:
        return (
            self.db.query(Message)
            .filter(Message.interview_id == interview_id)
            .order_by(Message.created_at.asc())
            .all()
        )
