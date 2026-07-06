from __future__ import annotations

import asyncio
import json
from typing import Any

from app.core.config import Settings


def _extract_emotion_summary(audio_emotion_result: dict) -> dict:
    summary = audio_emotion_result.get("emotion_summary")
    return summary if isinstance(summary, dict) else {}


def _format_context(value) -> str:
    if value in (None, "", []):
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        preferred_keys = ["response_strategy", "emotional_alignment", "key_phrases_to_use"]
        keys = [
            *[key for key in preferred_keys if key in value],
            *[key for key in value if key not in preferred_keys],
        ]
        return "; ".join(
            f"{key}: {json.dumps(value[key], ensure_ascii=False)}"
            for key in keys
            if value.get(key) not in (None, "", [])
        )
    return json.dumps(value, ensure_ascii=False)


def build_local_fallback_response(audio_emotion_result: dict) -> str:
    summary = _extract_emotion_summary(audio_emotion_result)
    primary_emotion = summary.get("primary_emotion") or "um estado emocional nao informado"
    intention = summary.get("intention") or "uma intencao nao informada"
    urgency = summary.get("urgency_level") or summary.get("urgency") or "urgencia nao informada"
    calmness = summary.get("calmness_level") or summary.get("calmness") or "calma nao informada"
    recommended_context = _format_context(
        audio_emotion_result.get("recommended_context_for_ai_agent")
    )

    base = (
        "Com base na analise emocional, o usuario parece demonstrar "
        f"{primary_emotion}, com intencao de {intention}, nivel de urgencia "
        f"{urgency} e nivel de calma {calmness}. "
    )

    if recommended_context:
        return (
            base
            + "Uma resposta adequada deve seguir este contexto: "
            + str(recommended_context)
        )

    return (
        base
        + "Uma resposta adequada deve ser clara, proporcional ao tom emocional e orientada a proximos passos."
    )


class LlmService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_response(self, prompt: str, audio_emotion_result: dict) -> dict:
        if not self.settings.use_llm:
            return {
                "status": "llm_disabled",
                "text": build_local_fallback_response(audio_emotion_result),
                "warnings": ["LLM is disabled. Using local fallback."],
            }

        if self.settings.llm_provider.lower() != "cohere":
            return {
                "status": "fallback_local",
                "text": build_local_fallback_response(audio_emotion_result),
                "warnings": [
                    f"Unsupported LLM provider '{self.settings.llm_provider}'. Using local fallback."
                ],
            }

        if not self.settings.cohere_api_key.strip():
            return {
                "status": "fallback_local",
                "text": build_local_fallback_response(audio_emotion_result),
                "warnings": ["Cohere API key is not configured. Using local fallback."],
            }

        try:
            text = await self._call_cohere(prompt)
            return {
                "status": "cohere",
                "text": text,
                "warnings": [],
            }
        except Exception:
            return {
                "status": "llm_error",
                "text": build_local_fallback_response(audio_emotion_result),
                "warnings": ["Cohere request failed. Using local fallback."],
            }

    async def _call_cohere(self, prompt: str) -> str:
        import cohere

        if hasattr(cohere, "AsyncClientV2"):
            client = cohere.AsyncClientV2(api_key=self.settings.cohere_api_key)
            response = await client.chat(
                model=self.settings.cohere_chat_model,
                messages=[{"role": "user", "content": prompt}],
            )
        elif hasattr(cohere, "ClientV2"):
            client = cohere.ClientV2(api_key=self.settings.cohere_api_key)
            response = await asyncio.to_thread(
                client.chat,
                model=self.settings.cohere_chat_model,
                messages=[{"role": "user", "content": prompt}],
            )
        else:
            client = cohere.Client(api_key=self.settings.cohere_api_key)
            response = await asyncio.to_thread(
                client.chat,
                model=self.settings.cohere_chat_model,
                message=prompt,
            )

        return self._extract_cohere_text(response)

    def _extract_cohere_text(self, response: Any) -> str:
        message = getattr(response, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, list):
            parts = []
            for item in content:
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
                elif isinstance(item, dict) and item.get("text"):
                    parts.append(item["text"])
            if parts:
                return "\n".join(parts).strip()

        text = getattr(response, "text", None)
        if text:
            return str(text).strip()

        if isinstance(response, dict):
            if response.get("text"):
                return str(response["text"]).strip()
            if response.get("message", {}).get("content"):
                content = response["message"]["content"]
                if isinstance(content, list):
                    return "\n".join(
                        str(item.get("text", item)) if isinstance(item, dict) else str(item)
                        for item in content
                    ).strip()

        return str(response).strip()
