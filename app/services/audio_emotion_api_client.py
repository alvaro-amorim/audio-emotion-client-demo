from __future__ import annotations

import json

import httpx

from app.core.config import Settings


class AudioEmotionApiError(Exception):
    def __init__(self, detail: str, status_code: int = 502) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class AudioEmotionApiAuthError(AudioEmotionApiError):
    pass


class AudioEmotionApiUnavailableError(AudioEmotionApiError):
    pass


class AudioEmotionApiClient:
    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self.transport = transport

    async def analyze_audio(self, filename: str, content: bytes, content_type: str | None) -> dict:
        url = f"{self.settings.audio_emotion_api_base_url}/v1/analyze-audio"
        headers = {
            self.settings.audio_emotion_api_key_header_name: self.settings.audio_emotion_api_key,
        }
        files = {
            "file": (
                filename,
                content,
                content_type or "application/octet-stream",
            )
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.audio_emotion_api_timeout_seconds,
                transport=self.transport,
            ) as client:
                response = await client.post(url, headers=headers, files=files)
        except (httpx.ConnectError, httpx.NetworkError, httpx.RemoteProtocolError):
            raise AudioEmotionApiUnavailableError(
                "Audio Emotion API is unavailable. Make sure it is running at "
                f"{self.settings.audio_emotion_api_base_url}.",
                status_code=503,
            ) from None
        except httpx.TimeoutException:
            raise AudioEmotionApiUnavailableError(
                "Audio Emotion API request timed out. Make sure it is running at "
                f"{self.settings.audio_emotion_api_base_url} and try again.",
                status_code=504,
            ) from None
        except httpx.HTTPError as exc:
            raise AudioEmotionApiUnavailableError(
                "Audio Emotion API is unavailable. Make sure it is running at "
                f"{self.settings.audio_emotion_api_base_url}.",
                status_code=503,
            ) from exc

        if response.status_code == 401:
            raise AudioEmotionApiAuthError(
                "Audio Emotion API rejected the API key.",
                status_code=401,
            )

        if response.status_code >= 400:
            raise AudioEmotionApiError(
                f"Audio Emotion API returned HTTP {response.status_code}.",
                status_code=502,
            )

        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise AudioEmotionApiError(
                "Audio Emotion API returned an invalid JSON response.",
                status_code=502,
            ) from exc
