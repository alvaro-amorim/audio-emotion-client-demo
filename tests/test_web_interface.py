from fastapi.testclient import TestClient

from app.main import app
from app.services.audio_emotion_api_client import AudioEmotionApiClient
from app.services.llm_service import LlmService


def test_index_returns_html():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Audio Emotion Client Demo" in response.text


def test_demo_config_does_not_expose_keys(monkeypatch):
    monkeypatch.setenv("AUDIO_EMOTION_API_KEY", "super-secret-audio-key")
    monkeypatch.setenv("COHERE_API_KEY", "super-secret-cohere-key")

    from app.core.config import get_settings

    get_settings.cache_clear()
    client = TestClient(app)

    response = client.get("/demo/config")
    payload_text = response.text

    assert response.status_code == 200
    assert "super-secret-audio-key" not in payload_text
    assert "super-secret-cohere-key" not in payload_text
    assert "AUDIO_EMOTION_API_KEY" not in payload_text
    assert "COHERE_API_KEY" not in payload_text


def test_demo_status_does_not_expose_key_values(monkeypatch):
    monkeypatch.setenv("AUDIO_EMOTION_API_KEY", "super-secret-audio-key")
    monkeypatch.setenv("COHERE_API_KEY", "super-secret-cohere-key")

    from app.core.config import get_settings

    get_settings.cache_clear()
    client = TestClient(app)

    response = client.get("/demo/status")
    payload_text = response.text

    assert response.status_code == 200
    assert response.json()["audio_emotion_api_key_configured"] is True
    assert response.json()["cohere_configured"] is True
    assert "super-secret-audio-key" not in payload_text
    assert "super-secret-cohere-key" not in payload_text


def test_analyze_and_respond_returns_expected_structure(monkeypatch):
    audio_result = {
        "analysis_id": "analysis-1",
        "status": {
            "transcription_status": "real",
            "emotion_status": "real",
        },
        "transcription": {"text": "Preciso de ajuda com minha conta."},
        "annotated_transcription": "[preocupado] Preciso de ajuda com minha conta.",
        "emotion_summary": {
            "primary_emotion": "preocupacao",
            "secondary_emotions": ["urgencia"],
            "emotional_tone": "tenso",
            "intention": "resolver problema",
            "urgency_level": "alta",
            "calmness_level": "media",
            "confidence_score": 0.82,
        },
        "important_observations": ["Usuario quer solucao rapida."],
        "recommended_context_for_ai_agent": "Responder com clareza e passos objetivos.",
        "acoustic_metrics": {},
    }

    async def fake_analyze_audio(self, filename, content, content_type):
        assert filename == "sample.m4a"
        assert content == b"audio-bytes"
        assert content_type == "audio/mp4"
        return audio_result

    async def fake_generate_response(self, prompt, result):
        assert "Preciso de ajuda com minha conta." in prompt
        assert result == audio_result
        return {
            "status": "fallback_local",
            "text": "Resposta final local.",
            "warnings": ["Cohere API key is not configured. Using local fallback."],
        }

    monkeypatch.setattr(AudioEmotionApiClient, "analyze_audio", fake_analyze_audio)
    monkeypatch.setattr(LlmService, "generate_response", fake_generate_response)

    client = TestClient(app)
    response = client.post(
        "/demo/analyze-and-respond",
        files={"file": ("sample.m4a", b"audio-bytes", "audio/mp4")},
        data={
            "assistant_profile": "support",
            "user_instruction": "Seja breve.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["audio_emotion_result"] == audio_result
    assert "Preciso de ajuda com minha conta." in payload["llm_prompt"]
    assert payload["llm_response"]["status"] == "fallback_local"
    assert payload["llm_response"]["text"] == "Resposta final local."
    assert payload["llm_status"] == "fallback_local"
    assert payload["warnings"]


def test_analyze_and_respond_accepts_structured_annotated_transcription(monkeypatch):
    audio_result = {
        "status": {"transcription_status": "real", "emotion_status": "real"},
        "transcription": {"text": "Pode me ajudar com isso?"},
        "annotated_transcription": {
            "text": "[inseguro] Pode me ajudar com isso?",
            "segments": [{"text": "Pode me ajudar", "emotion": "inseguranca"}],
        },
        "emotion_summary": {"primary_emotion": "inseguranca"},
        "important_observations": [],
        "recommended_context_for_ai_agent": "Responder com calma.",
    }

    async def fake_analyze_audio(self, filename, content, content_type):
        return audio_result

    async def fake_generate_response(self, prompt, result):
        assert "[object Object]" not in prompt
        assert "[inseguro] Pode me ajudar com isso?" in prompt
        return {"status": "fallback_local", "text": "Resposta local.", "warnings": []}

    monkeypatch.setattr(AudioEmotionApiClient, "analyze_audio", fake_analyze_audio)
    monkeypatch.setattr(LlmService, "generate_response", fake_generate_response)

    client = TestClient(app)
    response = client.post(
        "/demo/analyze-and-respond",
        files={"file": ("sample.webm", b"audio-bytes", "audio/webm")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "[object Object]" not in payload["llm_prompt"]
    assert "[inseguro] Pode me ajudar com isso?" in payload["llm_prompt"]


def test_analyze_and_respond_accepts_structured_recommended_context(monkeypatch):
    audio_result = {
        "status": {"transcription_status": "real", "emotion_status": "real"},
        "transcription": {"text": "Estou com pressa para resolver."},
        "annotated_transcription": "[urgente] Estou com pressa para resolver.",
        "emotion_summary": {
            "primary_emotion": "urgencia",
            "urgency_level": "alta",
        },
        "important_observations": [{"text": "Priorizar resposta direta."}],
        "recommended_context_for_ai_agent": {
            "response_strategy": "Dar uma resposta direta com proximos passos.",
            "emotional_alignment": "Reconhecer a urgencia sem alarmismo.",
            "key_phrases_to_use": ["Vamos resolver pelo caminho mais curto."],
        },
    }

    async def fake_analyze_audio(self, filename, content, content_type):
        return audio_result

    async def fake_generate_response(self, prompt, result):
        assert "[object Object]" not in prompt
        assert "response_strategy: Dar uma resposta direta com proximos passos." in prompt
        assert "Priorizar resposta direta." in prompt
        return {"status": "fallback_local", "text": "Resposta local.", "warnings": []}

    monkeypatch.setattr(AudioEmotionApiClient, "analyze_audio", fake_analyze_audio)
    monkeypatch.setattr(LlmService, "generate_response", fake_generate_response)

    client = TestClient(app)
    response = client.post(
        "/demo/analyze-and-respond",
        files={"file": ("sample.webm", b"audio-bytes", "audio/webm")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "[object Object]" not in payload["llm_prompt"]
    assert "response_strategy: Dar uma resposta direta com proximos passos." in payload["llm_prompt"]
