"""
PRISM Multi-Provider LLM Abstraction.

Supports Mistral, OpenAI, Google Gemini, Anthropic, Ollama, and any OpenAI-compatible API.
Auto-detects the active provider based on which environment variable is set.
"""

from abc import ABC, abstractmethod

import httpx

from prism.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str = "unknown"

    @abstractmethod
    async def chat(self, prompt: str) -> str:
        """Send a prompt and return the raw text response."""


class MistralProvider(LLMProvider):
    name = "mistral"

    async def chat(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                },
                json={
                    "model": "mistral-small-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


class OpenAIProvider(LLMProvider):
    name = "openai"

    async def chat(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


class GeminiProvider(LLMProvider):
    name = "gemini"

    async def chat(self, prompt: str) -> str:
        api_key = settings.GEMINI_API_KEY
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1},
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    async def chat(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]


class OllamaProvider(LLMProvider):
    name = "ollama"

    async def chat(self, prompt: str) -> str:
        base_url = settings.OLLAMA_URL.rstrip("/")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "model": "llama3",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["message"]["content"]


class CustomOpenAIProvider(LLMProvider):
    name = "custom"

    async def chat(self, prompt: str) -> str:
        base_url = settings.CUSTOM_LLM_URL.rstrip("/")
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.CUSTOM_LLM_KEY:
            headers["Authorization"] = f"Bearer {settings.CUSTOM_LLM_KEY}"

        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                headers=headers,
                json={
                    "model": settings.CUSTOM_LLM_MODEL or "default",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


def get_provider() -> LLMProvider | None:
    """Auto-detect and return the configured LLM provider.

    Checks environment variables in priority order.
    Returns None if no provider is configured (deterministic-only mode).
    """
    if settings.OPENAI_API_KEY:
        return OpenAIProvider()
    if settings.ANTHROPIC_API_KEY:
        return AnthropicProvider()
    if settings.GEMINI_API_KEY:
        return GeminiProvider()
    if settings.MISTRAL_API_KEY:
        return MistralProvider()
    if settings.OLLAMA_URL:
        return OllamaProvider()
    if settings.CUSTOM_LLM_URL:
        return CustomOpenAIProvider()
    return None


def get_provider_name() -> str:
    """Return the name of the active LLM provider, or 'none'."""
    provider = get_provider()
    return provider.name if provider else "none"
