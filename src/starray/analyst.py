from __future__ import annotations

from dataclasses import dataclass

from .config import AppConfig
from .providers import ChatMessage, ProviderError, ProviderFactory


ANALYST_SYSTEM_PROMPT = (
    "You are the Analyst agent in StarRay. Be concise, practical, and action-oriented. "
    "When uncertain, ask a short clarifying question."
)


@dataclass(slots=True)
class AnalystResponse:
    content: str
    provider: str
    model: str
    fallback_used: bool


class AnalystRuntime:
    def __init__(self, cfg: AppConfig, provider_factory: ProviderFactory | None = None) -> None:
        self._cfg = cfg
        self._providers = provider_factory or ProviderFactory()

    def _provider_order(self) -> list[str]:
        ordered: list[str] = []
        for candidate in [self._cfg.provider, *self._cfg.provider_fallbacks, "local"]:
            if candidate and candidate not in ordered:
                ordered.append(candidate)
        return ordered

    def _model_order(self, role: str) -> list[str]:
        primary = self._cfg.role_models.get(role, self._cfg.default_model)
        ordered: list[str] = []
        for candidate in [primary, *self._cfg.role_fallback_models.get(role, []), self._cfg.default_model]:
            if candidate and candidate not in ordered:
                ordered.append(candidate)
        return ordered

    def respond(self, user_text: str) -> AnalystResponse:
        messages = [
            ChatMessage(role="system", content=ANALYST_SYSTEM_PROMPT),
            ChatMessage(role="user", content=user_text),
        ]

        provider_errors: list[str] = []
        models = self._model_order("analyst")

        for provider_name in self._provider_order():
            for model in models:
                try:
                    provider = self._providers.get(provider_name)
                    content = provider.chat(
                        messages,
                        model=model,
                        temperature=self._cfg.temperature,
                        timeout_seconds=self._cfg.request_timeout_seconds,
                    )
                    return AnalystResponse(
                        content=content.strip(),
                        provider=provider_name,
                        model=model,
                        fallback_used=provider_name != self._cfg.provider or model != models[0],
                    )
                except ProviderError as exc:
                    provider_errors.append(f"{provider_name}:{model}: {exc}")

        # Should never happen because local fallback exists, but keep a hard fallback message.
        return AnalystResponse(
            content=(
                "Analyst: I could not reach any configured providers. "
                "Run '/provider' to inspect routes and verify credentials."
            ),
            provider="none",
            model="none",
            fallback_used=True,
        )

    def provider_summary(self) -> str:
        providers = " -> ".join(self._provider_order())
        models = " -> ".join(self._model_order("analyst"))
        return f"Provider route: {providers}\nAnalyst model route: {models}"
