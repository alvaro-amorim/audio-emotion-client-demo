from app.services.prompt_builder import build_llm_prompt


def test_prompt_builder_includes_transcription_and_emotion():
    result = {
        "transcription": {"text": "Estou preocupado com o prazo."},
        "annotated_transcription": "[preocupado] Estou preocupado com o prazo.",
        "emotion_summary": {
            "primary_emotion": "preocupacao",
            "secondary_emotions": ["ansiedade"],
            "emotional_tone": "tenso",
            "intention": "pedir ajuda",
            "urgency_level": "alta",
            "calmness_level": "baixa",
            "confidence_score": 0.9,
        },
        "important_observations": ["Ha sinal de urgencia."],
        "recommended_context_for_ai_agent": "Responder com objetividade e acolhimento.",
    }

    prompt = build_llm_prompt(result, "support", "Responda em portugues.")

    assert "Estou preocupado com o prazo." in prompt
    assert "preocupacao" in prompt
    assert "ansiedade" in prompt
    assert "Responder com objetividade e acolhimento." in prompt
    assert "Responda em portugues." in prompt


def test_prompt_builder_formats_complex_objects_without_object_object():
    result = {
        "transcription": {"text": "Nao sei o que fazer agora."},
        "annotated_transcription": {
            "text": "[inseguro] Nao sei o que fazer agora.",
            "notes": {"tone": "hesitante"},
        },
        "emotion_summary": {
            "primary_emotion": "inseguranca",
            "secondary_emotions": [{"emotion": "preocupacao", "intensity": "media"}],
            "emotional_tone": {"label": "hesitante"},
            "intention": "pedir orientacao",
            "urgency_level": "media",
            "calmness_level": "baixa",
            "confidence_score": 0.74,
        },
        "important_observations": [
            {"type": "tom", "text": "Usuario parece inseguro."},
            "Evitar resposta fria.",
        ],
        "recommended_context_for_ai_agent": {
            "response_strategy": "Explicar em passos curtos.",
            "emotional_alignment": "Acolher a inseguranca sem exagerar.",
            "key_phrases_to_use": ["Vamos por partes.", "Eu te ajudo com isso."],
        },
    }

    prompt = build_llm_prompt(result, "teacher", None)

    assert "[object Object]" not in prompt
    assert "[inseguro] Nao sei o que fazer agora." in prompt
    assert "response_strategy: Explicar em passos curtos." in prompt
    assert "emotional_alignment: Acolher a inseguranca sem exagerar." in prompt
    assert "key_phrases_to_use" in prompt
    assert "Usuario parece inseguro." in prompt
