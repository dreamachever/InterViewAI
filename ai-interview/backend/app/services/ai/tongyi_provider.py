from app.core.config import Settings
from app.services.ai.openai_compatible_provider import OpenAICompatibleProvider, ProviderOptions


class TongyiProvider(OpenAICompatibleProvider):
    def __init__(self, settings: Settings):
        super().__init__(
            ProviderOptions(
                name="tongyi",
                api_key=settings.tongyi_api_key,
                base_url=settings.tongyi_base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
                model=settings.tongyi_model,
                api_key_env="TONGYI_API_KEY",
            )
        )
