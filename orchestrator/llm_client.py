"""
LLM Client — Trade-CLI
Backend primário: Ollama local via httpx (sem dependência de SDK).
Backend fallback: qualquer OpenAI-compatible endpoint.
NUNCA cloud API como padrão.

Fase: 2.3
Data: 2026-05-01
"""
from __future__ import annotations

from collections.abc import Iterator
import os
import time
from dataclasses import dataclass, field
from typing import Optional
import httpx
import structlog

log = structlog.get_logger(__name__)


@dataclass
class LLMMessage:
    role: str   # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    backend: str       # "ollama" | "openai_compatible" | "unavailable"
    tokens_used: int = 0
    duration_ms: float = 0.0


class LLMClient:
    """
    Abstracção sobre backends LLM locais.
    Usa httpx directo para máxima fiabilidade e zero dependências de SDK.
    """

    def __init__(self) -> None:
        self.ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
        self.fallback_base = os.getenv("LLM_API_BASE", "").rstrip("/")
        self.fallback_model = os.getenv("LLM_MODEL", "")
        self.fallback_key = os.getenv("LLM_API_KEY", "")
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))

    def is_available(self) -> bool:
        """Verifica se algum backend LLM está disponível."""
        return self._is_ollama_up() or bool(self.fallback_base)

    def _is_ollama_up(self) -> bool:
        try:
            r = httpx.get(f"{self.ollama_base}/api/tags", timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    # Keep backward-compatible alias
    is_ollama_available = _is_ollama_up

    def get_available_models(self) -> list[str]:
        """Lista modelos disponíveis no Ollama."""
        try:
            r = httpx.get(f"{self.ollama_base}/api/tags", timeout=5.0)
            if r.status_code == 200:
                return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            pass
        return []

    def chat(
        self,
        system: str,
        user: str,
        history: list[LLMMessage] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """
        Conversa com o LLM.
        Tenta Ollama primeiro; fallback para OpenAI-compatible se configurado.
        Nunca levanta excepção — retorna sempre um LLMResponse.
        """
        t0 = time.monotonic()

        if self._is_ollama_up():
            try:
                result = self._chat_ollama(system, user, history, max_tokens, temperature)
                result.duration_ms = (time.monotonic() - t0) * 1000
                log.info("llm_response", backend="ollama", ms=round(result.duration_ms))
                return result
            except Exception as e:
                log.warning("ollama_failed", error=str(e))

        if self.fallback_base:
            log.warning("using_fallback_llm", base=self.fallback_base)
            try:
                result = self._chat_openai_compat(system, user, history, max_tokens, temperature)
                result.duration_ms = (time.monotonic() - t0) * 1000
                return result
            except Exception as e:
                log.error("fallback_llm_failed", error=str(e))

        return LLMResponse(
            content=(
                "⚠️  Nenhum LLM disponível.\n"
                f"Inicia o Ollama: `ollama serve`\n"
                f"Instala um modelo: `ollama pull {self.ollama_model}`"
            ),
            model="unavailable",
            backend="unavailable",
        )

    def _chat_ollama(
        self,
        system: str,
        user: str,
        history: list[LLMMessage] | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        messages = [{"role": "system", "content": system}]
        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user})

        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        r = httpx.post(
            f"{self.ollama_base}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        return LLMResponse(
            content=data["message"]["content"],
            model=self.ollama_model,
            backend="ollama",
            tokens_used=data.get("eval_count", 0),
        )

    def _chat_openai_compat(
        self,
        system: str,
        user: str,
        history: list[LLMMessage] | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        messages = [{"role": "system", "content": system}]
        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user})

        headers = {"Content-Type": "application/json"}
        if self.fallback_key:
            headers["Authorization"] = f"Bearer {self.fallback_key}"

        payload = {
            "model": self.fallback_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        r = httpx.post(
            f"{self.fallback_base}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            model=self.fallback_model,
            backend="openai_compatible",
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
        )

    def stream_chat(
        self,
        system: str,
        user: str,
        history: list[LLMMessage] | None = None,
        temperature: float = 0.3,
    ) -> Iterator[str]:
        """
        Stream de resposta token a token via Ollama.
        Nunca levanta excepção para o caller; em erro, emite uma mensagem final.
        """
        import json as _json

        if not self._is_ollama_up():
            yield (
                "⚠️  Ollama offline.\n"
                f"Inicia com: `ollama serve`\n"
                f"Instala o modelo: `ollama pull {self.ollama_model}`"
            )
            return

        messages = [{"role": "system", "content": system}]
        if history:
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user})

        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature},
        }

        try:
            with httpx.stream(
                "POST",
                f"{self.ollama_base}/api/chat",
                json=payload,
                timeout=self.timeout,
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        data = _json.loads(line)
                    except _json.JSONDecodeError:
                        continue
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
                    if data.get("done"):
                        break
        except Exception as e:
            log.error("stream_chat_failed", error=str(e))
            yield f"\n⚠️  Erro de streaming: {e}"

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
            if response.backend == "unavailable":
                return None
            return response.content
        except Exception as e:
            log.warning("llm_thesis_failed", error=str(e))
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
            if response.backend == "unavailable":
                return None
            return response.content
        except Exception as e:
            log.warning("llm_synthesis_failed", error=str(e))
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
            if response.backend == "unavailable":
                return None
            return response.content
        except Exception as e:
            log.warning("llm_verdict_failed", error=str(e))
            return None
