from __future__ import annotations

import json
from typing import Any


ASSISTANT_PROFILES = {
    "support": "suporte tecnico objetivo, acolhedor e orientado a solucao",
    "customer_service": "atendimento ao cliente cordial, profissional e claro",
    "teacher": "professor didatico, paciente e bom em explicar conceitos",
    "empathetic": "assistente empatico, cuidadoso e emocionalmente atento",
    "general": "assistente geral equilibrado, claro e util",
    "free": "assistente que segue principalmente a instrucao livre do usuario",
    "custom": "assistente que segue principalmente a instrucao livre do usuario",
}


def _humanize_key(key: str) -> str:
    return str(key).replace("_", " ")


def _get_nested(data: dict, path: tuple[str, ...], default: Any = "Nao informado") -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    if current in (None, ""):
        return default
    return current


def _format_value(value: Any) -> str:
    if value in (None, "", []):
        return "Nao informado"
    if isinstance(value, list):
        return _format_list(value)
    if isinstance(value, dict):
        return _format_object(value)
    return str(value)


def _format_list(value: list) -> str:
    if not value:
        return "Nao informado"
    return "\n".join(f"- {_format_value(item)}" for item in value)


def _format_object(value: dict) -> str:
    if not value:
        return "Nao informado"
    lines = []
    for key, item in value.items():
        if item in (None, "", []):
            continue
        formatted = _format_value(item)
        lines.append(f"- {_humanize_key(key)}: {formatted}")
    return "\n".join(lines) if lines else "Nao informado"


def _format_annotated_transcription(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("text"), str):
        return value["text"]
    return _format_value(value)


def _format_recommended_context(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return _format_value(value)

    preferred_keys = [
        "response_strategy",
        "emotional_alignment",
        "key_phrases_to_use",
    ]
    ordered_keys = [
        *[key for key in preferred_keys if key in value],
        *[key for key in value if key not in preferred_keys],
    ]
    lines = []
    for key in ordered_keys:
        item = value.get(key)
        if item in (None, "", []):
            continue
        lines.append(f"- {key}: {_format_value(item)}")
    return "\n".join(lines) if lines else json.dumps(value, ensure_ascii=False, indent=2)


def build_llm_prompt(
    audio_emotion_result: dict,
    assistant_profile: str = "support",
    user_instruction: str | None = None,
) -> str:
    profile_key = assistant_profile if assistant_profile in ASSISTANT_PROFILES else "support"
    profile_description = ASSISTANT_PROFILES[profile_key]

    transcription = _get_nested(audio_emotion_result, ("transcription", "text"))
    annotated_transcription = _format_annotated_transcription(
        audio_emotion_result.get("annotated_transcription")
    )
    emotion_summary = audio_emotion_result.get("emotion_summary") or {}
    if not isinstance(emotion_summary, dict):
        emotion_summary = {}

    primary_emotion = emotion_summary.get("primary_emotion") or "Nao informado"
    secondary_emotions = emotion_summary.get("secondary_emotions") or []
    emotional_tone = (
        emotion_summary.get("emotional_tone")
        or emotion_summary.get("tone")
        or emotion_summary.get("tom")
        or "Nao informado"
    )
    intention = emotion_summary.get("intention") or emotion_summary.get("intent") or "Nao informado"
    urgency = emotion_summary.get("urgency_level") or emotion_summary.get("urgency") or "Nao informado"
    calmness = emotion_summary.get("calmness_level") or emotion_summary.get("calmness") or "Nao informado"
    confidence = emotion_summary.get("confidence_score") or emotion_summary.get("confidence") or "Nao informado"
    observations = _format_value(audio_emotion_result.get("important_observations") or [])
    recommended_context = _format_recommended_context(
        audio_emotion_result.get("recommended_context_for_ai_agent")
    )
    acoustic_metrics = audio_emotion_result.get("acoustic_metrics") or {}
    extra_instruction = (user_instruction or "").strip() or "Nenhuma instrucao extra fornecida."

    return f"""Voce e um assistente que deve responder ao usuario considerando o texto transcrito e o contexto emocional inferido pela Audio Emotion API.

Perfil escolhido do assistente:
- Chave: {profile_key}
- Orientacao: {profile_description}

Transcricao real:
{_format_value(transcription)}

Transcricao comentada:
{annotated_transcription}

Resumo emocional:
- Emocao primaria: {_format_value(primary_emotion)}
- Emocoes secundarias: {_format_value(secondary_emotions)}
- Tom emocional: {_format_value(emotional_tone)}
- Intencao: {_format_value(intention)}
- Urgencia: {_format_value(urgency)}
- Calma: {_format_value(calmness)}
- Confidence score: {_format_value(confidence)}

Observacoes importantes:
{observations}

Contexto recomendado pela Audio Emotion API para outro agente de IA:
{recommended_context}

Metricas acusticas disponiveis, apenas para contexto interno se forem uteis:
{_format_value(acoustic_metrics)}

Instrucao extra do usuario:
{extra_instruction}

Regras de resposta:
- Responda considerando emocao, tom e intencao.
- Se houver frustracao ou inseguranca, seja acolhedor, objetivo e cuidadoso.
- Se houver urgencia, seja direto e priorize proximos passos claros.
- Se houver inseguranca, explique com calma e evite excesso de jargao.
- Nao afirme que a emocao detectada e uma certeza absoluta.
- Nao mencione detalhes tecnicos da analise emocional ou acustica, a menos que o perfil ou a instrucao extra peca isso.
- Entregue uma resposta final pronta para o usuario."""
