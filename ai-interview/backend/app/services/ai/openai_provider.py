from app.core.config import Settings
from app.services.ai.openai_compatible_provider import OpenAICompatibleProvider, ProviderOptions


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            ProviderOptions(
                name="openai",
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url or "https://api.openai.com/v1",
                model=settings.openai_model,
                api_key_env="OPENAI_API_KEY",
            )
        )
