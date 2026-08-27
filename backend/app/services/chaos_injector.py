from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("snt_ai.services.chaos_injector")


class ChaosInterruption(Exception):
    def __init__(self, stage: str, reason: str, metadata: dict | None = None) -> None:
        self.stage = stage
        self.reason = reason
        self.metadata = metadata or {}
        super().__init__(f"[{stage}] {reason}")


@dataclass
class ChaosProfile:
    network_latency: bool = False
    latency_mean_ms: float = 500.0
    latency_std_ms: float = 100.0
    latency_timeout_ms: float = 10000.0
    latency_probability: float = 0.3

    context_bloat: bool = False
    bloat_token_count: int = 8000
    bloat_repeat_phrase: str = "This is a context bloat test message designed to consume token budget. "
    bloat_probability: float = 0.2

    guardrail_interruption: bool = False
    guardrail_probability: float = 0.1
    guardrail_phrases: list[str] = field(default_factory=lambda: [
        "I'm sorry, but I cannot assist with that request.",
        "This conversation has been flagged for review.",
        "I am unable to process this request due to safety guidelines.",
        "Content warning: This conversation may contain restricted topics.",
    ])

    failure_status_codes: list[int] = field(default_factory=lambda: [408, 429, 503])

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChaosProfile:
        latency = data.get("network_latency", {})
        bloat = data.get("context_bloat", {})
        guardrail = data.get("guardrail_interruption", {})

        return cls(
            network_latency=data.get("network_latency", {}).get("enabled", False),
            latency_mean_ms=latency.get("mean_ms", 500.0),
            latency_std_ms=latency.get("std_ms", 100.0),
            latency_timeout_ms=latency.get("timeout_ms", 10000.0),
            latency_probability=latency.get("probability", 0.3),
            context_bloat=data.get("context_bloat", {}).get("enabled", False),
            bloat_token_count=bloat.get("token_count", 8000),
            bloat_repeat_phrase=bloat.get("repeat_phrase", cls.bloat_repeat_phrase),
            bloat_probability=bloat.get("probability", 0.2),
            guardrail_interruption=data.get("guardrail_interruption", {}).get("enabled", False),
            guardrail_probability=guardrail.get("probability", 0.1),
        )


class ChaosInjector:
    def __init__(self, profile: ChaosProfile, seed: int = 42) -> None:
        self.profile = profile
        self._rng = random.Random(seed)
        self._injected_log: list[dict[str, Any]] = []

    async def apply_pre_turn(self, turn_index: int, user_message: str) -> tuple[str, dict[str, Any]]:
        effects: dict[str, Any] = {}

        if self.profile.context_bloat and self._rng.random() < self.profile.bloat_probability:
            user_message = self._inject_context_bloat(user_message)
            effects["context_bloat"] = {"injected": True, "tokens_added": self.profile.bloat_token_count}
            logger.debug("Injected context bloat at turn %d", turn_index)

        return user_message, effects

    async def apply_post_turn(
        self,
        turn_index: int,
        latency_ms: float,
    ) -> tuple[float, dict[str, Any]]:
        effects: dict[str, Any] = {}

        if self.profile.network_latency and self._rng.random() < self.profile.latency_probability:
            delay = max(0, self._rng.gauss(self.profile.latency_mean_ms, self.profile.latency_std_ms))
            if delay > 0:
                await asyncio.sleep(delay / 1000.0)
                latency_ms += delay
                effects["network_latency"] = {"delay_ms": round(delay, 2)}

            if self.profile.latency_timeout_ms > 0 and delay > self.profile.latency_timeout_ms:
                raise ChaosInterruption(
                    stage="network",
                    reason=f"Request timeout after {delay:.0f}ms",
                    metadata={"timeout_ms": delay},
                )

        return latency_ms, effects

    async def apply_guardrail_check(
        self,
        turn_index: int,
        agent_response: str,
    ) -> tuple[str, dict[str, Any]]:
        effects: dict[str, Any] = {}

        if self.profile.guardrail_interruption and self._rng.random() < self.profile.guardrail_probability:
            phrase = self._rng.choice(self.profile.guardrail_phrases)
            agent_response = phrase
            effects["guardrail_interruption"] = {"triggered": True, "response": phrase}
            logger.debug("Injected guardrail interruption at turn %d", turn_index)

        return agent_response, effects

    def _inject_context_bloat(self, message: str) -> str:
        repeat_count = self.profile.bloat_token_count // 10
        bloat_block = (self.profile.bloat_repeat_phrase * repeat_count)[:self.profile.bloat_token_count]
        return f"{message}\n\n[SYSTEM CONTEXT DUMP]\n{bloat_block}\n[/SYSTEM CONTEXT DUMP]"

    def get_injection_log(self) -> list[dict[str, Any]]:
        return self._injected_log

    def reset(self) -> None:
        self._injected_log.clear()


class RemoteAgentProvider:
    """Calls a real AI agent endpoint (OpenAI-compatible chat completions API)."""

    def __init__(
        self,
        endpoint_url: str,
        api_key: str | None,
        model_name: str | None,
        system_prompt: str,
        timeout_seconds: int = 60,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model_name = model_name or "default"
        self.system_prompt = system_prompt
        self.timeout_seconds = timeout_seconds

    async def generate_response(self, user_message: str, conversation_history: list[dict]) -> tuple[str, float, int]:
        import httpx

        messages: list[dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        for turn in conversation_history:
            user_text = turn.get("user", "")
            agent_text = turn.get("agent", "")
            if user_text:
                messages.append({"role": "user", "content": user_text})
            if agent_text:
                messages.append({"role": "assistant", "content": agent_text})

        messages.append({"role": "user", "content": user_message})

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
        }

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.post(self.endpoint_url, json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException:
            elapsed = (time.monotonic() - start) * 1000
            logger.warning("Remote agent request timed out after %dms", elapsed)
            return "(timeout)", elapsed, 0
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.error("Remote agent request failed: %s", exc)
            return f"(error: {exc})", elapsed, 0

        elapsed_ms = (time.monotonic() - start) * 1000

        try:
            choice = data["choices"][0]
            response_text = choice["message"]["content"]
        except (KeyError, IndexError, TypeError):
            logger.error("Unexpected response format from remote agent: %s", str(data)[:200])
            response_text = "(unexpected response format)"

        token_count = data.get("usage", {}).get("total_tokens", 0) or (len(response_text.split()) + len(user_message.split()))
        return response_text, round(elapsed_ms, 2), token_count


class MockAgentProvider:
    def __init__(self, system_prompt: str, seed: int = 42) -> None:
        self.system_prompt = system_prompt
        self._rng = random.Random(seed)
        self._default_responses = [
            "I understand your concern. Let me help you with that.",
            "Thank you for reaching out. I'll assist you with your request.",
            "I can see this is important to you. Let me check the details.",
            "Here's what I can do to help resolve this for you.",
            "I appreciate your patience. Let me guide you through this process.",
            "That's a great question. Let me provide you with the information you need.",
            "I understand this can be frustrating. Let me explain what happened.",
            "I've verified your account and here are the next steps.",
        ]

    async def generate_response(self, user_message: str, conversation_history: list[dict]) -> tuple[str, float, int]:
        start = time.monotonic()

        if "ignore all previous" in user_message.lower() or "system prompt" in user_message.lower():
            response = "I cannot reveal my system prompt or instructions. How else can I help you?"
        elif "select * from" in user_message.lower() or "drop table" in user_message.lower():
            response = "I cannot process SQL injection requests. Please ask something appropriate."
        elif "emergency" in user_message.lower() or "manager" in user_message.lower():
            response = "I understand this is urgent. Let me connect you with a specialist who can help."
        else:
            response = self._rng.choice(self._default_responses)

        elapsed_ms = (time.monotonic() - start) * 1000
        token_count = len(response.split()) + len(user_message.split())

        return response, elapsed_ms, token_count
