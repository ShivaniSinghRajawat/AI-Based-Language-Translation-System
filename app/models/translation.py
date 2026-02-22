"""Pydantic models for translation requests and responses."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class TranslationRequest(BaseModel):
    """Incoming payload for a translation operation."""

    text: str = Field(..., min_length=1, max_length=5000)
    source_language: str = Field(..., min_length=2, max_length=5)
    target_language: str = Field(..., min_length=2, max_length=5)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        """Ensure the provided text contains meaningful characters."""

        if not value.strip():
            raise ValueError("Text cannot be blank.")
        return value


class TranslationResponse(BaseModel):
    """API response model for translated text."""

    translated_text: str
    provider: str
    source_language: str
    target_language: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
