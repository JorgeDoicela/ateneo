"""
Prueba unitaria para verificar el adaptador agnóstico OpenAI-Compatible en ResilientLLMGateway.
Garantiza que el sistema pueda conectarse con vLLM, Ollama, llama.cpp o modelos fine-tuneados propios
sin alterar ni romper el comportamiento por defecto de Google Gemini.
"""

import json
import pytest
import httpx
from unittest.mock import MagicMock, patch
from core.config import settings
from core.llm_gateway import ResilientLLMGateway, LLMGenerationResult, CircuitStatus


def test_default_provider_is_gemini():
    """Garantiza que por defecto el proveedor siga siendo 'gemini' sin regresiones."""
    assert settings.llm_provider == "gemini"


def test_openai_compatible_generate_success(monkeypatch):
    """Verifica la generación exitosa mediante protocolo OpenAI-Compatible."""
    gateway = ResilientLLMGateway()

    # Forzar temporalmente el proveedor a openai_compatible
    monkeypatch.setattr(settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(settings, "custom_llm_base_url", "http://localhost:8000/v1")
    monkeypatch.setattr(settings, "custom_llm_api_key", "test-key")
    monkeypatch.setattr(settings, "gemini_primary_model", "med-llama-3-8b")
    monkeypatch.setattr(settings, "gemini_fallback_models_raw", "")

    mock_response = httpx.Response(
        status_code=200,
        json={
            "id": "chatcmpl-test",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({"score": 9.5, "aciertos": ["Diagnóstico correcto"]})
                    }
                }
            ]
        },
        request=httpx.Request("POST", "http://localhost:8000/v1/chat/completions")
    )

    with patch.object(httpx.Client, "post", return_value=mock_response) as mock_post:
        result = gateway.generate(
            prompt="Evaluar caso clínico de NAC",
            system_instruction="Eres un evaluador médico",
            response_mime_type="application/json"
        )

        assert isinstance(result, LLMGenerationResult)
        assert result.model_used == "med-llama-3-8b"
        assert not result.fallback_occurred
        data = result.json_dict()
        assert data.get("score") == 9.5

        # Validar que la llamada a la API externa se hizo con el esquema esperado
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        assert payload["model"] == "med-llama-3-8b"
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"
        assert payload["response_format"] == {"type": "json_object"}


def test_openai_compatible_multimodal_base64(monkeypatch):
    """Verifica que las imágenes se codifiquen en base64 para endpoints multimodales."""
    gateway = ResilientLLMGateway()

    monkeypatch.setattr(settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(settings, "custom_llm_base_url", "http://localhost:8000/v1")
    monkeypatch.setattr(settings, "gemini_primary_model", "med-vlm-7b")
    monkeypatch.setattr(settings, "gemini_fallback_models_raw", "")

    mock_response = httpx.Response(
        status_code=200,
        json={
            "choices": [{"message": {"role": "assistant", "content": "Rx interpretada"}}]
        },
        request=httpx.Request("POST", "http://localhost:8000/v1/chat/completions")
    )

    fake_img = (b"\x89PNG\r\n\x1a\nfake", "image/png")

    with patch.object(httpx.Client, "post", return_value=mock_response) as mock_post:
        result = gateway.generate(
            prompt="Interpretar Rx",
            imagenes_list=[fake_img]
        )

        assert result.text == "Rx interpretada"
        payload = mock_post.call_args[1]["json"]
        user_msg = payload["messages"][0]["content"]
        assert isinstance(user_msg, list)
        assert user_msg[0]["type"] == "text"
        assert user_msg[1]["type"] == "image_url"
        assert user_msg[1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_openai_compatible_streaming(monkeypatch):
    """Verifica la transmisión en streaming SSE para modelos locales."""
    gateway = ResilientLLMGateway()

    monkeypatch.setattr(settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(settings, "custom_llm_base_url", "http://localhost:8000/v1")
    monkeypatch.setattr(settings, "gemini_primary_model", "med-llama-3-8b")
    monkeypatch.setattr(settings, "gemini_fallback_models_raw", "")

    sse_lines = [
        b'data: {"choices": [{"delta": {"content": "Hola "}}]}\r\n',
        b'data: {"choices": [{"delta": {"content": "Doctor"}}]}\r\n',
        b'data: [DONE]\r\n'
    ]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_lines.return_value = [l.decode("utf-8") for l in sse_lines]

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__enter__.return_value = mock_resp

    with patch.object(httpx.Client, "stream", return_value=mock_stream_ctx):
        stream_gen = gateway.generate_stream(prompt="Iniciar streaming")
        tokens = list(stream_gen)
        assert "".join(tokens) == "Hola Doctor"
