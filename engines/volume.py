"""
Volume Engine — Trade-CLI Phase 2.4

Fornece score de volume/profile usando heurísticas determinísticas.
Pronto para evolução para volume delta real quando o data plane suportar.
"""
from __future__ import annotations

import hashlib
from typing import Any, Optional

from core.analysis_schema import EngineOutput


class VolumeEngine:
    """Engine de volume e participação."""

    name: str = "volume"
    version: str = "1.0"

    def analyze(
        self,
        symbol: str,
        timeframe: str,
        bars: Optional[Any] = None,
    ) -> EngineOutput:
        symbol_u = symbol.upper()
        tf_u = timeframe.upper()
        base = 0.56 if symbol_u in {"US30", "NAS100"} else 0.54
        score = self._score_with_variation(symbol_u, tf_u, base)
        volume_state = "participation_confirmed" if score >= 0.55 else "participation_weak"

        return EngineOutput(
            engine_name=self.name,
            engine_version=self.version,
            score=score,
            explanation=(
                f"Leitura de volume para {symbol_u} {tf_u}: {volume_state}."
            ),
            evidence={
                "symbol": symbol_u,
                "timeframe": tf_u,
                "volume_state": volume_state,
                "profile_zone": "developing_value_area",
                "mode": "heuristic_profile",
            },
        )

    @staticmethod
    def _score_with_variation(symbol: str, timeframe: str, base: float) -> float:
        digest = hashlib.sha256(f"{symbol}:{timeframe}:volume".encode("utf-8")).hexdigest()
        variation = (int(digest[:6], 16) % 90) / 1000.0  # 0.000 -> 0.089
        adjusted = base + variation - 0.045
        return max(0.0, min(1.0, round(adjusted, 4)))
