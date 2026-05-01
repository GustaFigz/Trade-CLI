"""Testes para ChatEngine — Fase 2.3."""
from pathlib import Path
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import orchestrator.chat_engine as chat_engine_module
from orchestrator.chat_engine import ChatEngine, ChatSession
from orchestrator.llm_client import LLMResponse


class TestChatSession:
    def test_add_messages(self):
        session = ChatSession()
        session.add("user", "hello")
        session.add("assistant", "hi")
        assert len(session.history) == 2

    def test_clear_session(self):
        session = ChatSession()
        session.add("user", "test")
        session.clear()
        assert len(session.history) == 0

    def test_history_roles(self):
        session = ChatSession()
        session.add("user", "msg1")
        session.add("assistant", "msg2")
        assert session.history[0].role == "user"
        assert session.history[1].role == "assistant"

    def test_history_trimming(self):
        session = ChatSession(max_history=4)
        for i in range(10):
            session.add("user", f"msg {i}")
        # After trimming, should keep first 2 + last (max_history - 2)
        assert len(session.history) <= session.max_history + 2


class TestChatEngine:
    def setup_method(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._history_patch = patch.object(
            chat_engine_module,
            "_HISTORY_FILE",
            Path(self._tmp_dir.name) / "chat_history.json",
        )
        self._history_patch.start()
        # ChatEngine init is safe — RAG will gracefully fail if no knowledge
        self.engine = ChatEngine()

    def teardown_method(self):
        self._history_patch.stop()
        self._tmp_dir.cleanup()

    def test_chat_returns_response(self):
        mock_response = LLMResponse(
            content="Bom dia! O EURUSD está...",
            model="gemma3",
            backend="ollama",
        )
        with patch.object(self.engine.llm, "chat", return_value=mock_response):
            response = self.engine.chat("Olá, o que achas do EURUSD?")
        assert response.content == "Bom dia! O EURUSD está..."
        assert isinstance(response, LLMResponse)

    def test_session_updates_after_chat(self):
        mock_response = LLMResponse(content="ok", model="test", backend="ollama")
        with patch.object(self.engine.llm, "chat", return_value=mock_response):
            self.engine.chat("pergunta teste")
        assert len(self.engine.session.history) == 2
        assert self.engine.session.history[0].role == "user"
        assert self.engine.session.history[1].role == "assistant"

    def test_reset_clears_session(self):
        mock_response = LLMResponse(content="ok", model="test", backend="ollama")
        with patch.object(self.engine.llm, "chat", return_value=mock_response):
            self.engine.chat("msg")
        self.engine.reset_session()
        assert len(self.engine.session.history) == 0

    def test_rag_context_returns_string(self):
        """_get_rag_context should always return a string."""
        ctx = self.engine._get_rag_context("test query")
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    def test_multiple_chats_accumulate_history(self):
        mock_response = LLMResponse(content="resp", model="test", backend="ollama")
        with patch.object(self.engine.llm, "chat", return_value=mock_response):
            self.engine.chat("msg1")
            self.engine.chat("msg2")
            self.engine.chat("msg3")
        assert len(self.engine.session.history) == 6  # 3 user + 3 assistant

    def test_stream_updates_session(self):
        with patch.object(
            self.engine.llm,
            "stream_chat",
            return_value=iter(["ola", " mundo"]),
        ):
            chunks = list(self.engine.stream("pergunta"))
        assert "".join(chunks) == "ola mundo"
        assert len(self.engine.session.history) == 2
        assert self.engine.session.history[0].role == "user"
        assert self.engine.session.history[1].content == "ola mundo"

    def test_chat_history_persists_between_instances(self):
        mock_response = LLMResponse(content="persistir", model="test", backend="ollama")
        with patch.object(self.engine.llm, "chat", return_value=mock_response):
            self.engine.chat("primeira")

        new_engine = ChatEngine()
        assert len(new_engine.session.history) == 2
        assert new_engine.session.history[0].content == "primeira"
