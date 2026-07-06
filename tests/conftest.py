import pytest

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def deterministic_settings(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Audio Emotion Client Demo")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("APP_VERSION", "0.1.0")
    monkeypatch.setenv("AUDIO_EMOTION_API_BASE_URL", "http://127.0.0.1:8014")
    monkeypatch.setenv("AUDIO_EMOTION_API_KEY", "test-audio-key")
    monkeypatch.setenv("AUDIO_EMOTION_API_KEY_HEADER_NAME", "X-API-Key")
    monkeypatch.setenv("AUDIO_EMOTION_API_TIMEOUT_SECONDS", "300")
    monkeypatch.setenv("USE_LLM", "true")
    monkeypatch.setenv("LLM_PROVIDER", "cohere")
    monkeypatch.setenv("COHERE_API_KEY", "")
    monkeypatch.setenv("COHERE_CHAT_MODEL", "command-a-03-2025")
    monkeypatch.setenv("DEFAULT_ASSISTANT_PROFILE", "support")
    monkeypatch.setenv("SHOW_RAW_JSON", "true")
    monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "100")
    monkeypatch.setenv("ALLOWED_AUDIO_EXTENSIONS", "mp3,wav,m4a,webm,ogg")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
