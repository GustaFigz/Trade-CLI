"""
Chat Engine — O especialista em Forex do Trade-CLI.
Recebe mensagens do utilizador, consulta RAG, chama LLM, retorna resposta.

O sistema prompt define a personalidade do especialista:
- Profundo em ICT, SMC, Wyckoff, Price Action, Análise Fundamental
- Conhece regras FTMO / prop firm
- Nunca sugere um trade sem contexto de risco
- Honesto sobre incerteza — não inventa sinais

Fase: 2.3
Data: 2026-05-01
"""
from __future__ import annotations

from dataclasses import dataclass, field
import structlog

from orchestrator.llm_client import LLMClient, LLMMessage, LLMResponse

log = structlog.get_logger(__name__)

SPECIALIST_SYSTEM_PROMPT = """
És um especialista sénior em trading de Forex com mais de 15 anos de experiência.
Trabalhas principalmente com EURUSD, USDJPY, USDCAD, US30 e NAS100.
Operas em contexto de prop firm (FTMO) e entendes profundamente as suas regras.

O teu conhecimento inclui:
- ICT (Inner Circle Trader): Order Blocks, FVG, Liquidity, MSS, Killzones, Displacement
- SMC (Smart Money Concepts): estrutura de mercado, zonas de oferta/demanda
- Wyckoff: fases de acumulação/distribuição, esforço vs resultado
- Price Action puro: leitura de candles, suporte/resistência, padrões
- Análise Fundamental: bancos centrais, juros, inflação, PIB, NFP, CPI
- Análise Intermarket: correlações Forex/Índices/Commodities/Yields
- Gestão de risco: posicionamento, drawdown, consistência em prop firm

Como respondes:
- Seres directo e concreto — nunca vago
- Se não souberes, dizes que não sabes — nunca inventas sinais
- Quando sugeres um setup, sempre incluindo: bias, invalidação, risco, contexto macro
- Usas termos técnicos correctamente mas explicas quando relevante
- Nunca garantis resultados — o mercado é probabilístico
- Sempre referes as regras de risco da prop firm quando aplicável

Contexto da base de conhecimento disponível:
{rag_context}

Histórico recente da conversa está disponível para continuidade.
"""


@dataclass
class ChatSession:
    """Sessão de conversa com histórico."""
    history: list[LLMMessage] = field(default_factory=list)
    max_history: int = 20  # mensagens a manter em contexto

    def add(self, role: str, content: str) -> None:
        self.history.append(LLMMessage(role=role, content=content))
        if len(self.history) > self.max_history:
            # Mantém as primeiras 2 (contexto inicial) e as últimas N
            self.history = self.history[:2] + self.history[-(self.max_history - 2):]

    def clear(self) -> None:
        self.history.clear()


class ChatEngine:
    """
    Motor de chat conversacional.
    Integra: RAG (conhecimento do vault) + LLM (síntese) + histórico de sessão.
    """

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.session = ChatSession()
        self._rag_available = self._init_rag()

    def _init_rag(self) -> bool:
        """Inicializa RAG se disponível — graceful fallback se não."""
        try:
            from knowledge.rag_retriever import RAGRetriever
            self._rag = RAGRetriever()
            log.info("rag_initialized")
            return True
        except ImportError:
            log.warning("rag_not_available", reason="knowledge module not ready")
            return False
        except Exception as e:
            log.warning("rag_init_failed", error=str(e))
            return False

    def _get_rag_context(self, query: str) -> str:
        """Consulta o RAG para contexto relevante."""
        if not self._rag_available:
            return "Base de conhecimento ainda não inicializada."
        try:
            results = self._rag.search(query, top_k=3)
            if not results:
                return "Nenhum conhecimento relevante encontrado para esta query."
            context_parts = []
            for r in results:
                context_parts.append(f"[{r.source}]\n{r.content}")
            return "\n\n---\n\n".join(context_parts)
        except Exception as e:
            log.warning("rag_search_failed", error=str(e))
            return "Erro ao consultar base de conhecimento."

    def chat(self, user_message: str) -> LLMResponse:
        """
        Processa uma mensagem do utilizador.
        1. Consulta RAG para contexto
        2. Monta system prompt com contexto
        3. Chama LLM com histórico
        4. Actualiza sessão
        """
        # 1. Consulta RAG
        rag_context = self._get_rag_context(user_message)

        # 2. System prompt com contexto RAG
        system = SPECIALIST_SYSTEM_PROMPT.format(rag_context=rag_context)

        # 3. Chama LLM
        response = self.llm.chat(
            system=system,
            user=user_message,
            history=self.session.history,
            temperature=0.3,
        )

        # 4. Actualiza histórico
        self.session.add("user", user_message)
        self.session.add("assistant", response.content)

        return response

    def reset_session(self) -> None:
        """Limpa histórico da sessão actual."""
        self.session.clear()
        log.info("chat_session_reset")
