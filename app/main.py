from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import Settings, get_settings
from app.services.audio_emotion_api_client import (
    AudioEmotionApiAuthError,
    AudioEmotionApiClient,
    AudioEmotionApiError,
)
from app.services.llm_service import LlmService
from app.services.prompt_builder import build_llm_prompt


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="Audio Emotion Client Demo", version="0.1.0")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


def _settings() -> Settings:
    return get_settings()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html", media_type="text/html")


@app.get("/health")
async def health() -> dict:
    settings = _settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/demo/config")
async def demo_config() -> dict:
    return _settings().safe_frontend_config()


@app.get("/demo/status")
async def demo_status() -> dict:
    settings = _settings()
    return {
        "status": "ok",
        "audio_emotion_api_base_url": settings.audio_emotion_api_base_url,
        "audio_emotion_api_key_configured": settings.audio_emotion_api_key_configured,
        "llm_enabled": settings.use_llm,
        "llm_provider": settings.llm_provider,
        "cohere_configured": settings.cohere_configured,
    }


def _validate_upload(file: UploadFile, content: bytes, settings: Settings) -> None:
    filename = file.filename or ""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in settings.allowed_audio_extension_set:
        allowed = ", ".join(sorted(settings.allowed_audio_extension_set))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio file extension. Allowed extensions: {allowed}.",
        )

    if not content:
        raise HTTPException(status_code=400, detail="Audio file is empty.")

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds the {settings.max_upload_size_mb} MB limit.",
        )


@app.post("/demo/analyze-and-respond")
async def analyze_and_respond(
    file: Annotated[UploadFile, File(...)],
    assistant_profile: Annotated[str | None, Form()] = None,
    user_instruction: Annotated[str | None, Form()] = None,
) -> dict:
    settings = _settings()
    content = await file.read()
    _validate_upload(file, content, settings)

    client = AudioEmotionApiClient(settings)
    try:
        audio_emotion_result = await client.analyze_audio(
            filename=file.filename or "audio",
            content=content,
            content_type=file.content_type,
        )
    except AudioEmotionApiAuthError as exc:
        raise HTTPException(status_code=401, detail=exc.detail) from exc
    except AudioEmotionApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    profile = assistant_profile or settings.default_assistant_profile
    prompt = build_llm_prompt(audio_emotion_result, profile, user_instruction)
    llm_result = await LlmService(settings).generate_response(prompt, audio_emotion_result)
    warnings = list(llm_result.get("warnings") or [])

    return {
        "status": "ok",
        "audio_emotion_result": audio_emotion_result,
        "llm_prompt": prompt,
        "llm_response": {
            "status": llm_result.get("status"),
            "text": llm_result.get("text", ""),
        },
        "llm_status": llm_result.get("status"),
        "warnings": warnings,
    }
