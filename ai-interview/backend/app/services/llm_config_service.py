from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.encryption import decrypt_secret, encrypt_secret
from app.models.user_llm_config import UserLLMConfig
from app.repositories.llm_config_repository import LLMConfigRepository
from app.schemas.llm_config import LLMConfigCreate, LLMConfigOut, LLMConfigTestResult, LLMConfigUpdate
from app.services.ai.llm_service import LLMService


SUPPORTED_PROVIDERS = {"mock", "openai", "deepseek", "tongyi", "doubao", "custom_openai_compatible"}


class LLMConfigService:
    def __init__(self, db: Session):
        self.db = db
        self.configs = LLMConfigRepository(db)

    def list_for_user(self, user_id: str) -> list[LLMConfigOut]:
        return [self._to_out(config) for config in self.configs.list_for_user(user_id)]

    def create(self, payload: LLMConfigCreate, user_id: str) -> LLMConfigOut:
        self._validate_provider(payload.provider)
        config = UserLLMConfig(
            user_id=user_id,
            display_name=payload.display_name,
            provider=payload.provider,
            base_url=payload.base_url,
            model=payload.model,
            encrypted_api_key=encrypt_secret(payload.api_key) if payload.api_key else None,
            is_active=payload.is_active,
            is_default=payload.is_default,
        )
        return self._to_out(self.configs.create(config))

    def update(self, config_id: str, payload: LLMConfigUpdate, user_id: str) -> LLMConfigOut:
        config = self._get(config_id, user_id)
        data = payload.model_dump(exclude_unset=True)
        provider = data.pop("provider", None)
        if provider is not None:
            self._validate_provider(provider)
            config.provider = provider
        api_key = data.pop("api_key", None)
        if api_key:
            config.encrypted_api_key = encrypt_secret(api_key)
        for key, value in data.items():
            setattr(config, key, value)
        if config.is_default and not config.is_active:
            raise HTTPException(status_code=422, detail="Default LLM config must be active")
        return self._to_out(self.configs.save(config))

    def delete(self, config_id: str, user_id: str) -> None:
        config = self._get(config_id, user_id)
        was_default = config.is_default
        self.configs.delete(config)
        if was_default:
            next_config = next((item for item in self.configs.list_for_user(user_id) if item.is_active), None)
            if next_config:
                next_config.is_default = True
                self.configs.save(next_config)

    def set_default(self, config_id: str, user_id: str) -> LLMConfigOut:
        config = self._get(config_id, user_id)
        if not config.is_active:
            raise HTTPException(status_code=422, detail="Cannot set inactive LLM config as default")
        config.is_default = True
        return self._to_out(self.configs.save(config))

    async def test(self, config_id: str, user_id: str) -> LLMConfigTestResult:
        config = self._get(config_id, user_id)
        try:
            provider = LLMService().build_provider_from_config(config, decrypt_secret(config.encrypted_api_key))
            if provider is None:
                message = "Mock provider is available"
            else:
                await provider.complete_json('{"task":"Return JSON exactly as requested","schema":{"ok":true}}')
                message = "Connection succeeded"
            config.last_test_status = "success"
            config.last_test_message = message
        except Exception as exc:
            message = str(exc)[:500]
            config.last_test_status = "failed"
            config.last_test_message = message
        config.last_tested_at = datetime.utcnow()
        self.configs.save(config)
        return LLMConfigTestResult(status=config.last_test_status or "failed", message=config.last_test_message or "")

    def _get(self, config_id: str, user_id: str) -> UserLLMConfig:
        config = self.configs.get_for_user(config_id, user_id)
        if not config:
            raise HTTPException(status_code=404, detail="LLM config not found")
        return config

    @staticmethod
    def _validate_provider(provider: str) -> None:
        if provider not in SUPPORTED_PROVIDERS:
            raise HTTPException(status_code=422, detail="Unsupported LLM provider")

    @staticmethod
    def _to_out(config: UserLLMConfig) -> LLMConfigOut:
        return LLMConfigOut(
            id=config.id,
            display_name=config.display_name,
            provider=config.provider,
            base_url=config.base_url,
            model=config.model,
            is_active=config.is_active,
            is_default=config.is_default,
            has_api_key=bool(config.encrypted_api_key),
            last_test_status=config.last_test_status,
            last_test_message=config.last_test_message,
            last_tested_at=config.last_tested_at,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
