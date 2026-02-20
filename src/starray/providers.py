from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class ProviderError(RuntimeError):
    """Raised when a model provider cannot satisfy a request."""


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


class ModelProvider(ABC):
    """Interface for pluggable LLM providers."""

    name: str

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        temperature: float,
        timeout_seconds: float,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def structured_output(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        schema: dict[str, Any],
        temperature: float,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        raise NotImplementedError


class LocalEchoProvider(ModelProvider):
    """Deterministic local fallback for development/offline usage."""

    name = "local"

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        temperature: float,
        timeout_seconds: float,
    ) -> str:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return (
            "Analyst: received. Live provider call unavailable, using local fallback. "
            f"Next step captured for Phase 1: {last_user}"
        )

    def structured_output(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        schema: dict[str, Any],
        temperature: float,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        properties = schema.get("properties", {})
        return {k: None for k in properties}


class LiteLLMProvider(ModelProvider):
    """Adapter for providers exposed through LiteLLM."""

    def __init__(self, provider_name: str) -> None:
        self.name = provider_name
        try:
            import litellm  # type: ignore
        except ImportError as exc:
            raise ProviderError(
                "LiteLLM is not installed. Install optional dependencies to use remote providers."
            ) from exc
        self._litellm = litellm

    def _qualified_model(self, model: str) -> str:
        # litellm expects e.g. openai/gpt-4.1, anthropic/claude-3-7-sonnet, gemini/gemini-2.0-flash
        if "/" in model:
            return model
        return f"{self.name}/{model}"

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        temperature: float,
        timeout_seconds: float,
    ) -> str:
        try:
            response = self._litellm.completion(
                model=self._qualified_model(model),
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                timeout=timeout_seconds,
            )
        except Exception as exc:  # pragma: no cover - depends on external client/runtime
            raise ProviderError(f"{self.name} provider request failed: {exc}") from exc

        try:
            return response["choices"][0]["message"]["content"]
        except Exception as exc:  # pragma: no cover - defensive parse path
            raise ProviderError(f"{self.name} provider returned an invalid response payload") from exc

    def structured_output(
        self,
        messages: list[ChatMessage],
        *,
        model: str,
        schema: dict[str, Any],
        temperature: float,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        try:
            response = self._litellm.completion(
                model=self._qualified_model(model),
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                timeout=timeout_seconds,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # pragma: no cover
            raise ProviderError(f"{self.name} provider request failed: {exc}") from exc

        try:
            import json

            content = response["choices"][0]["message"]["content"]
            payload = json.loads(content)
            if not isinstance(payload, dict):
                raise ProviderError(f"{self.name} provider returned non-object JSON")
            return payload
        except ProviderError:
            raise
        except Exception as exc:  # pragma: no cover
            raise ProviderError(f"{self.name} provider returned invalid JSON structured output") from exc


class ProviderFactory:
    """Constructs provider adapters from provider names."""

    def __init__(self) -> None:
        self._cache: dict[str, ModelProvider] = {}

    def get(self, provider_name: str) -> ModelProvider:
        if provider_name in self._cache:
            return self._cache[provider_name]

        if provider_name == "local":
            provider: ModelProvider = LocalEchoProvider()
        elif provider_name in {"openai", "anthropic", "gemini"}:
            provider = LiteLLMProvider(provider_name)
        else:
            raise ProviderError(f"Unsupported provider: {provider_name}")

        self._cache[provider_name] = provider
        return provider
