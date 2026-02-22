"""FastAPI entrypoint for the AI-Based Language Translation System."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings
from app.models.translation import TranslationRequest
from app.services.language_support import get_language_options
from app.services.translation_service import (
    LibreTranslateProvider,
    LocalFallbackProvider,
    TranslationError,
    TranslationService,
)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.1.0")
app = FastAPI(title=settings.app_name, version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

service = TranslationService(
    providers=[
        LibreTranslateProvider(settings=settings),
        LocalFallbackProvider(),
    ]
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint for probes and local debugging."""

    return {"status": "ok", "environment": settings.app_env}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Render the translation web application."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "languages": get_language_options(),
            "default_source": settings.default_source_language,
            "default_target": settings.default_target_language,
        },
    )


@app.post("/api/v1/translate")
def translate(payload: TranslationRequest) -> dict[str, str]:
    """Translate input text from source language to target language."""

    try:
        response = service.translate(payload)
    except TranslationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return response.model_dump(mode="json")
