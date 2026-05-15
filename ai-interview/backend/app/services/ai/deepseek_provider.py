from app.core.config import Settings
from app.services.ai.openai_compatible_provider import OpenAICompatibleProvider, ProviderOptions


class DeepSeekProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            ProviderOptions(
                name="deepseek",
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url or "https://api.deepseek.com",
                model=settings.deepseek_model,
                api_key_env="DEEPSEEK_API_KEY",
            )
        )
