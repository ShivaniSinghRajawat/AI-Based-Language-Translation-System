"""Tests for translation business logic."""

import pytest

from app.models.translation import TranslationRequest
from app.services.translation_service import (
    LocalFallbackProvider,
    TranslationError,
    TranslationService,
)


def test_local_fallback_returns_translated_payload() -> None:
    service = TranslationService(providers=[LocalFallbackProvider()])
    response = service.translate(
        TranslationRequest(
            text="Hello world",
            source_language="en",
            target_language="es",
        )
    )

    assert response.translated_text.startswith("[ES]")
    assert response.provider == "local-fallback"


def test_rejects_same_source_and_target_language() -> None:
    service = TranslationService(providers=[LocalFallbackProvider()])
    payload = TranslationRequest(
        text="Hello world",
        source_language="en",
        target_language="en",
    )

    with pytest.raises(TranslationError):
        service.translate(payload)
