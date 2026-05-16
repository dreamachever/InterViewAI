from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Interview MVP"
    api_prefix: str = "/api"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_interview"
    llm_provider: str = "mock"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    deepseek_api_key: str | None = None
    deepseek_base_url: str | None = None
    deepseek_model: str = "deepseek-chat"
    tongyi_api_key: str | None = None
    tongyi_base_url: str | None = None
    tongyi_model: str = "qwen-plus"
    doubao_api_key: str | None = None
    doubao_base_url: str | None = None
    doubao_model: str = ""
    search_provider: str = "duckduckgo_html"
    duckduckgo_html_url: str = "https://html.duckduckgo.com/html/"
    search_max_results: int = 5
    llm_config_encryption_key: str | None = None
    resume_upload_max_mb: int = 10
    resume_storage_dir: str = "storage/resumes"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
