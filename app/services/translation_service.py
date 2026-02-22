"""Translation service layer.

This module follows a provider strategy so we can swap translation backends without
changing API or UI behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging

import httpx

from app.core.config import Settings
from app.models.translation import TranslationRequest, TranslationResponse
from app.services.language_support import SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


class TranslationError(RuntimeError):
    """Raised when translation providers fail."""


@dataclass(slots=True)
class ProviderResult:
    """Internal DTO describing a successful provider response."""

    text: str
    provider_name: str


class TranslationProvider:
    """Abstract provider interface."""

    def translate(self, payload: TranslationRequest) -> ProviderResult:
        """Translate source text and return provider result."""

        raise NotImplementedError


class LibreTranslateProvider(TranslationProvider):
    """Provider that calls the LibreTranslate HTTP API."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def translate(self, payload: TranslationRequest) -> ProviderResult:
        request_body = {
            "q": payload.text,
            "source": payload.source_language,
            "target": payload.target_language,
            "format": "text",
        }

        try:
            response = httpx.post(
                self._settings.libretranslate_url,
                json=request_body,
                timeout=self._settings.request_timeout_seconds,
            )
            response.raise_for_status()
            translated_text = response.json().get("translatedText", "").strip()
        except httpx.HTTPError as error:
            raise TranslationError("LibreTranslate request failed.") from error

        if not translated_text:
            raise TranslationError("Provider returned an empty translation.")

        return ProviderResult(text=translated_text, provider_name="libretranslate")


class LocalFallbackProvider(TranslationProvider):
    """Fallback provider used when external APIs are unavailable.

    This provider preserves user flow and demonstrates graceful degradation.
    """

    def translate(self, payload: TranslationRequest) -> ProviderResult:
        marker = f"[{payload.target_language.upper()}]"
        return ProviderResult(
            text=f"{marker} {payload.text}",
            provider_name="local-fallback",
        )


class TranslationService:
    """Application service orchestrating validation and provider failover."""

    def __init__(self, providers: list[TranslationProvider]):
        self._providers = providers

    def translate(self, payload: TranslationRequest) -> TranslationResponse:
        """Translate text via the first available provider."""

        if payload.source_language not in SUPPORTED_LANGUAGES:
            raise TranslationError("Unsupported source language.")
        if payload.target_language not in SUPPORTED_LANGUAGES:
            raise TranslationError("Unsupported target language.")
        if payload.source_language == payload.target_language:
            raise TranslationError("Source and target languages must be different.")

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                result = provider.translate(payload)
                return TranslationResponse(
                    translated_text=result.text,
                    provider=result.provider_name,
                    source_language=payload.source_language,
                    target_language=payload.target_language,
                )
            except TranslationError as error:
                last_error = error
                logger.warning("Provider failed: %s", error)

        raise TranslationError("All translation providers failed.") from last_error
