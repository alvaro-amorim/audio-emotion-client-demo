import asyncio

import httpx
import pytest

from app.core.config import Settings
from app.services.audio_emotion_api_client import (
    AudioEmotionApiAuthError,
    AudioEmotionApiClient,
    AudioEmotionApiUnavailableError,
)


def make_settings() -> Settings:
    return Settings(
        audio_emotion_api_base_url="http://audio-api.test",
        audio_emotion_api_key="secret-key",
        audio_emotion_api_key_header_name="X-API-Key",
        audio_emotion_api_timeout_seconds=3,
    )


def test_audio_emotion_client_sends_x_api_key_header():
    captured_headers = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured_headers["x-api-key"] = request.headers.get("X-API-Key")
        captured_headers["content-type"] = request.headers.get("content-type")
        body = await request.aread()
        assert b"audio.wav" in body
        return httpx.Response(201, json={"status": {"emotion_status": "real"}})

    client = AudioEmotionApiClient(make_settings(), transport=httpx.MockTransport(handler))

    result = asyncio.run(client.analyze_audio("audio.wav", b"abc", "audio/wav"))

    assert captured_headers["x-api-key"] == "secret-key"
    assert captured_headers["content-type"].startswith("multipart/form-data")
    assert result == {"status": {"emotion_status": "real"}}


def test_audio_emotion_client_handles_401():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "unauthorized"})

    client = AudioEmotionApiClient(make_settings(), transport=httpx.MockTransport(handler))

    with pytest.raises(AudioEmotionApiAuthError) as exc:
        asyncio.run(client.analyze_audio("audio.wav", b"abc", "audio/wav"))

    assert "Audio Emotion API rejected the API key." == exc.value.detail
    assert exc.value.status_code == 401


def test_audio_emotion_client_handles_api_offline():
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    client = AudioEmotionApiClient(make_settings(), transport=httpx.MockTransport(handler))

    with pytest.raises(AudioEmotionApiUnavailableError) as exc:
        asyncio.run(client.analyze_audio("audio.wav", b"abc", "audio/wav"))

    assert "Audio Emotion API is unavailable." in exc.value.detail
    assert "http://audio-api.test" in exc.value.detail
    assert exc.value.status_code == 503


def test_audio_emotion_client_handles_timeout():
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    client = AudioEmotionApiClient(make_settings(), transport=httpx.MockTransport(handler))

    with pytest.raises(AudioEmotionApiUnavailableError) as exc:
        asyncio.run(client.analyze_audio("audio.wav", b"abc", "audio/wav"))

    assert "timed out" in exc.value.detail
    assert exc.value.status_code == 504
