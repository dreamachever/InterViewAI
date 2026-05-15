from app.core.config import Settings
from app.services.ai.openai_compatible_provider import OpenAICompatibleProvider, ProviderOptions


class DoubaoProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            ProviderOptions(
                name="doubao",
                api_key=settings.doubao_api_key,
                base_url=settings.doubao_base_url or "https://ark.cn-beijing.volces.com/api/v3",
                model=settings.doubao_model,
                api_key_env="DOUBAO_API_KEY",
            )
        )
