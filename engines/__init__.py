"""
Analytical Engines - Stubs for Phase 1 / Phase 2

These engines are designed to be swapped out easily. Each returns EngineOutput.
In Phase 1, they return mock outputs. In Phase 2.3+, they implement real analysis.

Phase 1: Interface defined, stubs implemented (symbol-agnostic mocks)
Phase 2: Real data integration via bars parameter
Date: 2026-05-01
"""

from core.analysis_schema import (
    EngineOutput, AnalysisOutput, BiaType,
    AnalysisType
)
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import pandas as pd
from engines.intermarket import IntermarketEngine
from engines.sentiment import SentimentEngine
from engines.volume import VolumeEngine


# ============================================================================
# BASE ENGINE CLASS
# ============================================================================

class AnalyticalEngine(ABC):
    """Base class for all analytical engines."""
    
    name: str = "base_engine"
    version: str = "1.0"
    
    @abstractmethod
    def analyze(
        self,
        symbol: str,
        timeframe: str,
        bars: Optional[Any] = None,  # pd.DataFrame when available, None in mock
    ) -> EngineOutput:
        """
        Analyze and return a score.
        
        Args:
            symbol: "EURUSD", etc.
            timeframe: "M5", "M15", "H1", "H4"
            bars: Optional DataFrame with OHLCV data. Phase 1: ignored (uses mock).
                  Phase 2.3+ will use real bars from MT5.
        
        Returns:
            EngineOutput with score (0.0-1.0) and explanation
        """
        pass

    def _mock_score_for_symbol(self, symbol: str, timeframe: str, base: float) -> float:
        """Generate deterministic but varied mock score based on symbol+timeframe."""
        import hashlib
        seed = int(hashlib.md5(f"{symbol}{timeframe}".encode()).hexdigest()[:8], 16)
        variation = (seed % 100) / 1000  # ±0.1 max variation
        return min(1.0, max(0.0, base + variation - 0.05))


# ============================================================================
# TECHNICAL ENGINE
# ============================================================================

class TechnicalEngine(AnalyticalEngine):
    """
    Technical analysis engine.
    
    Phase 1: Mock output (symbol-agnostic)
    Phase 2.3: Real indicators (MA, RSI, MACD, etc.) using bars DataFrame
    """
    
    name = "technical"
    version = "1.0"
    
    def analyze(
        self,
        symbol: str,
        timeframe: str,
        bars: Optional[Any] = None,
    ) -> EngineOutput:
        """
        Analyze technical setup.
        
        Args:
            symbol: Currency pair
            timeframe: Trading timeframe
            bars: Optional OHLCV DataFrame (ignored in Phase 1 mock)
            
        Returns:
            EngineOutput with technical score
        """
        
        # Phase 1: Symbol-agnostic mock data
        # Phase 2.3: Will use bars for real RSI/MA/MACD calculation
        score = self._mock_score_for_symbol(symbol, timeframe, 0.70)
        explanation = f"Trend analysis for {symbol} on {timeframe} — mock Phase 1"
        evidence = {
            "trend": "bullish",
            "ma_cross": "bullish",
            "momentum": "positive",
            "note": f"Phase 1 mock — real implementation in Phase 2.3 for {symbol}",
        }
        
        return EngineOutput(
            engine_name=self.name,
            engine_version=self.version,
            score=score,
            explanation=explanation,
            evidence=evidence,
        )


# ============================================================================
# PRICE ACTION ENGINE
# ============================================================================

class PriceActionEngine(AnalyticalEngine):
    """
    Price action engine.
    
    Phase 1: Mock output (symbol-agnostic)
    Phase 2.3: Real candle pattern analysis using bars DataFrame
    """
    
    name = "price_action"
    version = "1.0"
    
    def analyze(
        self,
        symbol: str,
        timeframe: str,
        bars: Optional[Any] = None,
    ) -> EngineOutput:
        """
        Analyze price action patterns.
        
        Args:
            symbol: Currency pair
            timeframe: Trading timeframe
            bars: Optional OHLCV DataFrame (ignored in Phase 1 mock)
            
        Returns:
            EngineOutput with price action score
        """
        
        # Phase 1: Symbol-agnostic mock data
        score = self._mock_score_for_symbol(symbol, timeframe, 0.55)
        explanation = f"Price action setup for {symbol} on {timeframe} — awaiting real data"
        evidence = {
            "pattern": "indecision",
            "last_candle": "doji",
            "volume": "medium",
            "displacement": "weak",
            "note": f"Phase 1 mock for {symbol} {timeframe}",
        }
        
        return EngineOutput(
            engine_name=self.name,
            engine_version=self.version,
            score=score,
            explanation=explanation,
            evidence=evidence,
        )


# ============================================================================
# FUNDAMENTAL ENGINE
# ============================================================================

class FundamentalEngine(AnalyticalEngine):
    """
    Fundamental/macro engine.
    
    Phase 1: Mock output (symbol-agnostic, no central bank specific data)
    Phase 2.4: Real economic data integration
    """
    
    name = "fundamental"
    version = "1.0"
    
    def analyze(
        self,
        symbol: str,
        timeframe: str,
        bars: Optional[Any] = None,
    ) -> EngineOutput:
        """
        Analyze macro/fundamental context.
        
        Args:
            symbol: Currency pair
            timeframe: Trading timeframe
            bars: Optional OHLCV DataFrame (not used in fundamental engine)
            
        Returns:
            EngineOutput with fundamental score
        """
        
        # Phase 1: Neutral mock — no symbol-specific central bank data
        # Phase 2.4: Real macro integration (central banks, events, rates)
        score = self._mock_score_for_symbol(symbol, timeframe, 0.65)
        explanation = f"Macro context for {symbol} on {timeframe} — neutral mock (Phase 1)"
        evidence = {
            "symbol": symbol,
            "macro_bias": "neutral",
            "note": "Real macro integration in Phase 2.4",
        }
        
        return EngineOutput(
            engine_name=self.name,
            engine_version=self.version,
            score=score,
            explanation=explanation,
            evidence=evidence,
        )


# ============================================================================
# THESIS ENGINE (Synthesizer)
# ============================================================================

class ThesisEngine:
    """
    Synthesizes outputs from individual engines into a complete analysis.
    
    This is the "wisdom layer" that combines signals.
    Accepts externally-provided engine outputs (from Orchestrator)
    or runs internal engines if none provided.
    """
    
    def __init__(self):
        self.technical_engine = TechnicalEngine()
        self.price_action_engine = PriceActionEngine()
        self.fundamental_engine = FundamentalEngine()
        self.sentiment_engine = SentimentEngine()
        self.intermarket_engine = IntermarketEngine()
        self.volume_engine = VolumeEngine()
    
    def synthesize(
        self,
        symbol: str,
        timeframe: str,
        analyst_notes: str = "",
        engine_outputs: Optional[List] = None,   # List[EngineOutput] from Orchestrator
        llm_synthesis: Optional[str] = None,      # LLM synthesis string from Orchestrator
    ) -> AnalysisOutput:
        """
        Synthesize analysis from all engines.
        
        Args:
            symbol: "EURUSD", etc.
            timeframe: "M5", "M15", "H1", "H4"
            analyst_notes: Optional analyst notes
            engine_outputs: Optional list of EngineOutput (from Orchestrator).
                          If None, runs internal engines.
            llm_synthesis: Optional LLM synthesis string. If provided, appended to analyst_notes.
        
        Returns:
            AnalysisOutput with complete analysis
        """
        
        # If engine_outputs provided externally (by Orchestrator), use them directly
        if engine_outputs is not None:
            tech_output = next(
                (e for e in engine_outputs if e.engine_name == "technical"), None
            )
            pa_output = next(
                (e for e in engine_outputs if e.engine_name == "price_action"), None
            )
            fund_output = next(
                (e for e in engine_outputs if e.engine_name == "fundamental"), None
            )
            sentiment_output = next(
                (e for e in engine_outputs if e.engine_name == "sentiment"), None
            )
            intermarket_output = next(
                (e for e in engine_outputs if e.engine_name == "intermarket"), None
            )
            volume_output = next(
                (e for e in engine_outputs if e.engine_name == "volume"), None
            )
            # Fallback to internal engines if any is missing
            if not tech_output:
                tech_output = self.technical_engine.analyze(symbol, timeframe)
            if not pa_output:
                pa_output = self.price_action_engine.analyze(symbol, timeframe)
            if not fund_output:
                fund_output = self.fundamental_engine.analyze(symbol, timeframe)
        else:
            # Run internal engines
            tech_output = self.technical_engine.analyze(symbol, timeframe)
            pa_output = self.price_action_engine.analyze(symbol, timeframe)
            fund_output = self.fundamental_engine.analyze(symbol, timeframe)
            sentiment_output = self.sentiment_engine.analyze(symbol, timeframe)
            intermarket_output = self.intermarket_engine.analyze(symbol, timeframe)
            volume_output = self.volume_engine.analyze(symbol, timeframe)
        
        # If LLM synthesis provided, append to analyst_notes
        if llm_synthesis:
            analyst_notes = f"{analyst_notes}\n\nLLM Synthesis: {llm_synthesis}".strip()
        
        # Aggregate scores
        technical_score = tech_output.score
        price_action_score = pa_output.score
        fundamental_score = fund_output.score
        sentiment_score = sentiment_output.score if sentiment_output else None
        intermarket_score = intermarket_output.score if intermarket_output else None
        volume_score = volume_output.score if volume_output else None
        
        # Calculate confidence and alignment
        scores = [technical_score, price_action_score, fundamental_score]
        for extra_score in (sentiment_score, intermarket_score, volume_score):
            if extra_score is not None:
                scores.append(extra_score)
        avg_score = sum(scores) / len(scores)
        
        # Alignment = low variance between engines (consensus)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        alignment_score = max(0.0, 1.0 - (variance * 2))  # Heuristic
        
        # Confidence = how strong is the consensus
        confidence_score = avg_score
        
        # Determine bias (simple heuristic)
        if avg_score > 0.65:
            bias = BiaType.BULLISH
        elif avg_score < 0.35:
            bias = BiaType.BEARISH
        else:
            bias = BiaType.NEUTRAL
        
        # Dynamic setup_type based on score
        if avg_score > 0.65:
            setup_type = "momentum_continuation"
        elif avg_score < 0.35:
            setup_type = "counter_trend_setup"
        else:
            setup_type = "mean_reversion"
        
        # Dynamic invalidations (no hardcoded prices)
        invalidations = [
            f"{timeframe} structure break — closes below recent swing low",
            f"Macro event within 30 minutes — news risk",
            f"Spread > 3 pips — execution risk for {symbol}",
        ]
        
        # Create analysis
        analysis = AnalysisOutput(
            symbol=symbol,
            timeframe=timeframe,
            analysis_type=AnalysisType.THESIS,
            bias=bias,
            setup_type=setup_type,
            confidence_score=confidence_score,
            alignment_score=alignment_score,
            technical_score=technical_score,
            price_action_score=price_action_score,
            fundamental_score=fundamental_score,
            invalidations=invalidations,
            risk_notes=[
                "Spread check recommended before entry",
                f"Monitor {symbol} correlated assets",
            ],
            analyst_notes=analyst_notes,
        )
        
        return analysis


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("=" * 60)
    print("ENGINES TEST (PHASE 1 STUBS)")
    print("=" * 60)
    
    thesis_engine = ThesisEngine()
    analysis = thesis_engine.synthesize(
        symbol="EURUSD",
        timeframe="H1",
        analyst_notes="Testing Phase 2 setup"
    )
    
    print(f"\nAnalysis for {analysis.symbol} {analysis.timeframe}")
    print(f"Bias: {analysis.bias.value}")
    print(f"Setup: {analysis.setup_type}")
    print(f"Confidence: {analysis.confidence_score:.1%}")
    print(f"Alignment: {analysis.alignment_score:.1%}")
    print(f"Technical: {analysis.technical_score:.1%}")
    print(f"Price Action: {analysis.price_action_score:.1%}")
    print(f"Fundamental: {analysis.fundamental_score:.1%}")
    print(f"\nJSON Output:\n{analysis.to_json()}")
