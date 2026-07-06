import asyncio

from app.core.config import Settings
from app.services.llm_service import LlmService


def sample_audio_result() -> dict:
    return {
        "emotion_summary": {
            "primary_emotion": "calma",
            "intention": "entender o problema",
            "urgency_level": "baixa",
            "calmness_level": "alta",
        },
        "recommended_context_for_ai_agent": "Responder em tom tranquilo e direto.",
    }


def test_llm_service_uses_fallback_when_llm_disabled():
    service = LlmService(Settings(use_llm=False, cohere_api_key="secret"))

    result = asyncio.run(service.generate_response("prompt", sample_audio_result()))

    assert result["status"] == "llm_disabled"
    assert "calma" in result["text"]
    assert result["warnings"] == ["LLM is disabled. Using local fallback."]


def test_llm_service_uses_fallback_when_cohere_key_is_empty():
    service = LlmService(Settings(use_llm=True, cohere_api_key=""))

    result = asyncio.run(service.generate_response("prompt", sample_audio_result()))

    assert result["status"] == "fallback_local"
    assert "calma" in result["text"]
    assert result["warnings"] == ["Cohere API key is not configured. Using local fallback."]
