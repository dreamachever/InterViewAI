from sqlalchemy.orm import Session

from app.models.user_llm_config import UserLLMConfig


class LLMConfigRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: str) -> list[UserLLMConfig]:
        return (
            self.db.query(UserLLMConfig)
            .filter(UserLLMConfig.user_id == user_id)
            .order_by(UserLLMConfig.is_default.desc(), UserLLMConfig.created_at.desc())
            .all()
        )

    def get_for_user(self, config_id: str, user_id: str) -> UserLLMConfig | None:
        return self.db.query(UserLLMConfig).filter(UserLLMConfig.id == config_id, UserLLMConfig.user_id == user_id).first()

    def get_default_for_user(self, user_id: str) -> UserLLMConfig | None:
        return (
            self.db.query(UserLLMConfig)
            .filter(UserLLMConfig.user_id == user_id, UserLLMConfig.is_default.is_(True), UserLLMConfig.is_active.is_(True))
            .first()
        )

    def clear_default(self, user_id: str, except_id: str | None = None) -> None:
        query = self.db.query(UserLLMConfig).filter(UserLLMConfig.user_id == user_id)
        if except_id:
            query = query.filter(UserLLMConfig.id != except_id)
        query.update({UserLLMConfig.is_default: False})

    def create(self, config: UserLLMConfig) -> UserLLMConfig:
        if config.is_default:
            self.clear_default(config.user_id)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def save(self, config: UserLLMConfig) -> UserLLMConfig:
        if config.is_default:
            self.clear_default(config.user_id, config.id)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def delete(self, config: UserLLMConfig) -> None:
        self.db.delete(config)
        self.db.commit()
