"""Testes para LLMClient — Fase 2.3."""
import pytest
from unittest.mock import patch, MagicMock
from orchestrator.llm_client import LLMClient, LLMMessage, LLMResponse


class TestLLMMessage:
    def test_creation(self):
        msg = LLMMessage(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"

    def test_system_role(self):
        msg = LLMMessage(role="system", content="system prompt")
        assert msg.role == "system"


class TestLLMResponse:
    def test_defaults(self):
        resp = LLMResponse(content="test", model="gemma3", backend="ollama")
        assert resp.content == "test"
        assert resp.tokens_used == 0
        assert resp.duration_ms == 0.0

    def test_with_values(self):
        resp = LLMResponse(
            content="hello", model="gemma3", backend="ollama",
            tokens_used=42, duration_ms=123.5,
        )
        assert resp.tokens_used == 42
        assert resp.duration_ms == 123.5


class TestLLMClient:
    def setup_method(self):
        self.client = LLMClient()

    def test_unavailable_returns_response_not_raises(self):
        """Se LLM offline, retorna mensagem de erro em vez de raise."""
        with patch.object(self.client, "_is_ollama_up", return_value=False):
            self.client.fallback_base = ""
            response = self.client.chat(system="test", user="hello")
        assert isinstance(response, LLMResponse)
        assert response.backend == "unavailable"
        assert len(response.content) > 0

    def test_is_available_false_when_both_offline(self):
        with patch.object(self.client, "_is_ollama_up", return_value=False):
            self.client.fallback_base = ""
            assert self.client.is_available() is False

    def test_is_available_true_with_fallback(self):
        with patch.object(self.client, "_is_ollama_up", return_value=False):
            self.client.fallback_base = "http://localhost:8080"
            assert self.client.is_available() is True

    def test_backward_compatible_alias(self):
        """is_ollama_available should be an alias for _is_ollama_up."""
        assert self.client.is_ollama_available == self.client._is_ollama_up

    def test_generate_thesis_returns_none_when_unavailable(self):
        with patch.object(self.client, "_is_ollama_up", return_value=False):
            self.client.fallback_base = ""
            result = self.client.generate_thesis("test context")
        assert result is None

    def test_synthesize_engines_returns_none_when_unavailable(self):
        with patch.object(self.client, "_is_ollama_up", return_value=False):
            self.client.fallback_base = ""
            result = self.client.synthesize_engines("engine data")
        assert result is None

    def test_explain_verdict_returns_none_when_unavailable(self):
        with patch.object(self.client, "_is_ollama_up", return_value=False):
            self.client.fallback_base = ""
            result = self.client.explain_verdict("verdict data")
        assert result is None

    def test_get_available_models_returns_list(self):
        """get_available_models should return a list (possibly empty)."""
        models = self.client.get_available_models()
        assert isinstance(models, list)

    def test_default_model_is_gemma4(self):
        """Default model should be gemma4:e4b."""
        assert self.client.ollama_model == "gemma4:e4b"
