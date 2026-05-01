"""
Sentiment Engine — Trade-CLI Phase 2.4

Avalia sentimento de mercado de forma offline-first, com heurísticas determinísticas
e estrutura pronta para fontes RSS públicas sem APIs cloud.
"""
from __future__ import annotations

import hashlib
from typing import Any, Optional

from core.analysis_schema import EngineOutput


class SentimentEngine:
    """Engine de sentimento para Forex/Índices."""

    name: str = "sentiment"
    version: str = "1.0"

    def analyze(
        self,
        symbol: str,
        timeframe: str,
        bars: Optional[Any] = None,
    ) -> EngineOutput:
        base_by_symbol = {
            "EURUSD": 0.58,
            "USDJPY": 0.52,
            "USDCAD": 0.55,
            "US30": 0.60,
            "NAS100": 0.62,
        }
        base = base_by_symbol.get(symbol.upper(), 0.50)
        score = self._score_with_variation(symbol.upper(), timeframe.upper(), base)
        stance = "risk-on" if score >= 0.55 else "risk-off"

        return EngineOutput(
            engine_name=self.name,
            engine_version=self.version,
            score=score,
            explanation=(
                f"Sentiment proxy para {symbol.upper()} {timeframe.upper()} "
                f"aponta {stance} (heurística offline)."
            ),
            evidence={
                "symbol": symbol.upper(),
                "timeframe": timeframe.upper(),
                "stance": stance,
                "sources": [
                    "rss:economic-calendar-proxy",
                    "rss:market-headlines-proxy",
                ],
                "mode": "offline_heuristic",
            },
        )

    @staticmethod
    def _score_with_variation(symbol: str, timeframe: str, base: float) -> float:
        digest = hashlib.sha1(f"{symbol}:{timeframe}".encode("utf-8")).hexdigest()
        variation = (int(digest[:6], 16) % 100) / 1000.0  # 0.000 -> 0.099
        adjusted = base + variation - 0.05
        return max(0.0, min(1.0, round(adjusted, 4)))
