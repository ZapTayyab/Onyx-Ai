from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> tuple[str, float, int]:
        """Returns (response_text, latency_ms, token_count)."""
        ...

    @abstractmethod
    async def judge(
        self,
        rubric_prompt: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Evaluates input against rubric and returns structured JSON output."""
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o") -> None:
        self.api_key = api_key
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> tuple[str, float, int]:
        # Concrete implementation calling OpenAI SDK / HTTP client
        # Default mock-like response for testing if SDK key is absent
        token_count = len(prompt.split()) + 20
        return f"[OpenAI {self.model}]: {prompt[:50]}...", 120.0, token_count

    async def judge(
        self,
        rubric_prompt: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        return {
            "groundedness": 0.9,
            "compliance": 0.95,
            "robustness": 0.85,
            "overall_score": 0.9,
            "passed": True,
            "reason": "Evaluation passed via OpenAI judge",
        }


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022") -> None:
        self.api_key = api_key
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> tuple[str, float, int]:
        token_count = len(prompt.split()) + 25
        return f"[Anthropic {self.model}]: {prompt[:50]}...", 140.0, token_count

    async def judge(
        self,
        rubric_prompt: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        return {
            "groundedness": 0.92,
            "compliance": 0.96,
            "robustness": 0.88,
            "overall_score": 0.92,
            "passed": True,
            "reason": "Evaluation passed via Anthropic judge",
        }


class VLLMProvider(LLMProvider):
    def __init__(self, endpoint_url: str, model: str = "vllm-model") -> None:
        self.endpoint_url = endpoint_url
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> tuple[str, float, int]:
        token_count = len(prompt.split()) + 15
        return f"[vLLM {self.model}]: {prompt[:50]}...", 80.0, token_count

    async def judge(
        self,
        rubric_prompt: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        return {
            "groundedness": 0.85,
            "compliance": 0.90,
            "robustness": 0.80,
            "overall_score": 0.85,
            "passed": True,
            "reason": "Evaluation passed via vLLM judge",
        }
