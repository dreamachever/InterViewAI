from datetime import datetime

from pydantic import BaseModel, Field


class LLMConfigBase(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    provider: str
    base_url: str | None = None
    model: str | None = None
    is_active: bool = True
    is_default: bool = False


class LLMConfigCreate(LLMConfigBase):
    api_key: str | None = None


class LLMConfigUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    provider: str | None = None
    base_url: str | None = None
    model: str | None = None
    api_key: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None


class LLMConfigOut(LLMConfigBase):
    id: str
    has_api_key: bool
    last_test_status: str | None = None
    last_test_message: str | None = None
    last_tested_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LLMConfigTestResult(BaseModel):
    status: str
    message: str
