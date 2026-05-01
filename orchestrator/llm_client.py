"""
LLM Client — Trade-CLI Fase 2
Backend: Ollama (Gemma local) como primário.
Fallback: OpenAI-compatible endpoint via LLM_API_BASE env var.
NUNCA usa cloud APIs como default — privacidade e zero custo.

Fase: 2.3
Data: 2026-05-01
"""
from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    model: str
    backend: str  # "ollama" | "openai_compatible"
    tokens_used: int = 0


class LLMClient:
    """
    Abstracção sobre backends LLM locais.
    Prioridade: Ollama → fallback OpenAI-compatible (se configurado via env).
    """

    def __init__(self) -> None:
        self.ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma:7b")
        self.fallback_base = os.getenv("LLM_API_BASE", "")
        self.fallback_model = os.getenv("LLM_MODEL", "")
        self.fallback_key = os.getenv("LLM_API_KEY", "")
        self.timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))

    def is_ollama_available(self) -> bool:
        """Check if Ollama server is running and reachable."""
        try:
            response = httpx.get(f"{self.ollama_base}/api/tags", timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if any LLM backend is available."""
        if self.is_ollama_available():
            return True
        if self.fallback_base:
            return True
        return False

    def chat(
        self,
        system: str,
        user: str,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Send a chat request to the best available LLM backend.

        Args:
            system: System prompt
            user: User message
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with content and metadata

        Raises:
            RuntimeError: If no backend is available
        """
        if self.is_ollama_available():
            return self._chat_ollama(system, user, max_tokens)
        elif self.fallback_base:
            logger.warning("Ollama indisponível — usando fallback OpenAI-compatible")
            return self._chat_openai_compatible(system, user, max_tokens)
        else:
            raise RuntimeError(
                "Nenhum backend LLM disponível. "
                "Inicia o Ollama: 'ollama serve' e garante que o modelo está instalado: "
                f"'ollama pull {self.ollama_model}'"
            )

    def _chat_ollama(
        self, system: str, user: str, max_tokens: int
    ) -> LLMResponse:
        """Chat via Ollama local API."""
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        response = httpx.post(
            f"{self.ollama_base}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return LLMResponse(
            content=data["message"]["content"],
            model=self.ollama_model,
            backend="ollama",
        )

    def _chat_openai_compatible(
        self, system: str, user: str, max_tokens: int
    ) -> LLMResponse:
        """Chat via OpenAI-compatible API endpoint."""
        headers = {"Content-Type": "application/json"}
        if self.fallback_key:
            headers["Authorization"] = f"Bearer {self.fallback_key}"
        payload = {
            "model": self.fallback_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
        }
        response = httpx.post(
            f"{self.fallback_base}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=self.fallback_model,
            backend="openai_compatible",
        )

    # ── Convenience methods for orchestrator ──────────────────────────

    def generate_thesis(self, context: str) -> Optional[str]:
        """
        Generate trading thesis from analysis context.

        Args:
            context: Full analysis context string

        Returns:
            LLM-generated thesis text, or None if failed
        """
        try:
            response = self.chat(
                system=(
                    "You are a professional forex trading analyst. "
                    "Provide concise, structured analysis based on the data provided. "
                    "Be direct and professional."
                ),
                user=context,
            )
            return response.content
        except Exception as e:
            logger.warning(f"LLM thesis generation failed: {e}")
            return None

    def synthesize_engines(self, engines_text: str) -> Optional[str]:
        """
        Synthesize multiple engine outputs into consensus.

        Args:
            engines_text: Formatted engine outputs

        Returns:
            LLM synthesis text, or None if failed
        """
        try:
            response = self.chat(
                system=(
                    "You are a trading analysis synthesizer. "
                    "Combine multiple engine outputs into a coherent analysis. "
                    "Note conflicts between engines. "
                    "Give a consensus bias and confidence. "
                    "Keep response concise (5-7 sentences)."
                ),
                user=engines_text,
            )
            return response.content
        except Exception as e:
            logger.warning(f"LLM synthesis failed: {e}")
            return None

    def explain_verdict(self, analysis_summary: str) -> Optional[str]:
        """
        Generate explanation for analysis verdict.

        Args:
            analysis_summary: Summary of the analysis with verdict

        Returns:
            LLM explanation, or None if failed
        """
        try:
            response = self.chat(
                system=(
                    "You are a risk management assistant. "
                    "Provide a brief (2-3 sentences) explanation of why "
                    "this verdict was given. Be concise and professional."
                ),
                user=analysis_summary,
                max_tokens=256,
            )
            return response.content
        except Exception as e:
            logger.warning(f"LLM verdict explanation failed: {e}")
            return None
