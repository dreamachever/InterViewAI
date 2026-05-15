import json
import re
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class ProviderOptions:
    name: str
    api_key: str | None
    base_url: str
    model: str
    api_key_env: str


class OpenAICompatibleProvider:
    def __init__(self, options: ProviderOptions):
        if not options.api_key:
            raise ValueError(f"{options.api_key_env} is required when LLM_PROVIDER={options.name}")
        if not options.model:
            raise ValueError(f"{options.name.upper()}_MODEL is required when LLM_PROVIDER={options.name}")
        self.name = options.name
        self.api_key = options.api_key
        self.base_url = options.base_url.rstrip("/")
        self.model = options.model

    async def complete_json(self, prompt: str) -> dict:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You only output valid JSON. Do not output markdown or extra explanation."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.S)
            if not match:
                raise
            return json.loads(match.group(0))
