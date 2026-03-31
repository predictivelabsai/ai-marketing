"""XAI/Grok integration wrapper."""
import os
from typing import AsyncIterator, Optional

from .base import IntegrationBackend


class XaiIntegration(IntegrationBackend):
    """Wraps the AsyncOpenAI client pointed at x.ai for content generation."""

    name = "xai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY", "")
        self.model = model or os.getenv("XAI_MODEL", "grok-3")
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
                timeout=90.0,
                max_retries=1,
            )
        return self._client

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> str:
        """Generate text using XAI/Grok. Returns the assistant message content."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    async def generate_stream(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> AsyncIterator[str]:
        """Stream tokens from XAI/Grok. Yields text chunks as they arrive."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
