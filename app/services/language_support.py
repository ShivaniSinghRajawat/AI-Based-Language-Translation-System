"""Utilities for supported language metadata."""

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "hi": "Hindi",
    "ja": "Japanese",
    "zh": "Chinese",
    "ar": "Arabic",
}


def get_language_options() -> list[dict[str, str]]:
    """Return supported languages in a UI-friendly shape."""

    return [
        {"code": code, "name": name}
        for code, name in sorted(SUPPORTED_LANGUAGES.items(), key=lambda item: item[1])
    ]
