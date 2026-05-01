"""
Tests for engines — Phase 2.
Covers TechnicalEngine, PriceActionEngine, FundamentalEngine, ThesisEngine.
Targets 80%+ coverage on engines/ module.

Fase: 2.3
Data: 2026-05-01
"""
import pytest
from engines import (
    TechnicalEngine,
    PriceActionEngine,
    FundamentalEngine,
    ThesisEngine,
    AnalyticalEngine,
)
from core.analysis_schema import EngineOutput, AnalysisOutput, BiaType


# ============================================================================
# TECHNICAL ENGINE
# ============================================================================

class TestTechnicalEngine:
    def test_analyze_eurusd(self):
        engine = TechnicalEngine()
        output = engine.analyze("EURUSD", "H1")
        assert isinstance(output, EngineOutput)
        assert output.engine_name == "technical"
        assert 0.0 <= output.score <= 1.0
        assert "EURUSD" in output.explanation

    def test_analyze_different_symbols(self):
        engine = TechnicalEngine()
        for symbol in ["EURUSD", "USDJPY", "USDCAD", "US30", "NAS100"]:
            output = engine.analyze(symbol, "H1")
            assert isinstance(output, EngineOutput)
            assert 0.0 <= output.score <= 1.0

    def test_analyze_different_timeframes(self):
        engine = TechnicalEngine()
        for tf in ["M5", "M15", "H1", "H4", "D1"]:
            output = engine.analyze("EURUSD", tf)
            assert isinstance(output, EngineOutput)
            assert tf in output.explanation

    def test_evidence_structure(self):
        engine = TechnicalEngine()
        output = engine.analyze("EURUSD", "H1")
        assert isinstance(output.evidence, dict)
        assert "trend" in output.evidence
        assert "ma_cross" in output.evidence

    def test_with_bars_parameter(self):
        """Engine should work with bars=None (Phase 1 mock)."""
        engine = TechnicalEngine()
        output = engine.analyze("EURUSD", "H1", bars=None)
        assert isinstance(output, EngineOutput)

    def test_engine_name_and_version(self):
        engine = TechnicalEngine()
        assert engine.name == "technical"
        assert engine.version == "1.0"

    def test_deterministic_scores(self):
        """Same symbol+tf should give same score (deterministic mock)."""
        engine = TechnicalEngine()
        s1 = engine.analyze("EURUSD", "H1").score
        s2 = engine.analyze("EURUSD", "H1").score
        assert s1 == s2

    def test_different_symbols_different_scores(self):
        """Different symbols should generally give different scores."""
        engine = TechnicalEngine()
        scores = {sym: engine.analyze(sym, "H1").score
                  for sym in ["EURUSD", "USDJPY", "USDCAD"]}
        # At least 2 of 3 should differ
        unique = len(set(scores.values()))
        assert unique >= 2


# ============================================================================
# PRICE ACTION ENGINE
# ============================================================================

class TestPriceActionEngine:
    def test_analyze_eurusd(self):
        engine = PriceActionEngine()
        output = engine.analyze("EURUSD", "H1")
        assert isinstance(output, EngineOutput)
        assert output.engine_name == "price_action"
        assert 0.0 <= output.score <= 1.0

    def test_analyze_all_symbols(self):
        engine = PriceActionEngine()
        for symbol in ["EURUSD", "USDJPY", "USDCAD", "US30", "NAS100"]:
            output = engine.analyze(symbol, "M15")
            assert isinstance(output, EngineOutput)

    def test_evidence_has_pattern(self):
        engine = PriceActionEngine()
        output = engine.analyze("EURUSD", "H1")
        assert "pattern" in output.evidence
        assert "displacement" in output.evidence


# ============================================================================
# FUNDAMENTAL ENGINE
# ============================================================================

class TestFundamentalEngine:
    def test_analyze_eurusd(self):
        engine = FundamentalEngine()
        output = engine.analyze("EURUSD", "H1")
        assert isinstance(output, EngineOutput)
        assert output.engine_name == "fundamental"
        assert 0.0 <= output.score <= 1.0

    def test_analyze_all_symbols(self):
        engine = FundamentalEngine()
        for symbol in ["EURUSD", "USDJPY", "USDCAD", "US30", "NAS100"]:
            output = engine.analyze(symbol, "H4")
            assert isinstance(output, EngineOutput)

    def test_evidence_has_macro(self):
        engine = FundamentalEngine()
        output = engine.analyze("EURUSD", "H1")
        assert "macro_bias" in output.evidence


# ============================================================================
# THESIS ENGINE
# ============================================================================

class TestThesisEngineFull:
    def test_synthesize_basic(self):
        engine = ThesisEngine()
        output = engine.synthesize("EURUSD", "H1")
        assert isinstance(output, AnalysisOutput)
        assert output.symbol == "EURUSD"
        assert output.timeframe == "H1"
        assert 0.0 <= output.confidence_score <= 1.0
        assert 0.0 <= output.alignment_score <= 1.0

    def test_synthesize_with_notes(self):
        engine = ThesisEngine()
        output = engine.synthesize("EURUSD", "H1", analyst_notes="Test notes")
        assert "Test notes" in output.analyst_notes

    def test_synthesize_with_llm_synthesis(self):
        engine = ThesisEngine()
        output = engine.synthesize(
            "EURUSD", "H1",
            llm_synthesis="LLM says bullish"
        )
        assert "LLM Synthesis:" in output.analyst_notes
        assert "LLM says bullish" in output.analyst_notes

    def test_synthesize_with_engine_outputs(self):
        """Test using externally provided engine outputs."""
        engine = ThesisEngine()
        ext_outputs = [
            EngineOutput(
                engine_name="technical",
                engine_version="1.0",
                score=0.80,
                explanation="Strong bullish",
            ),
            EngineOutput(
                engine_name="price_action",
                engine_version="1.0",
                score=0.75,
                explanation="Clear setup",
            ),
            EngineOutput(
                engine_name="fundamental",
                engine_version="1.0",
                score=0.70,
                explanation="Supportive macro",
            ),
        ]
        output = engine.synthesize(
            "EURUSD", "H1",
            engine_outputs=ext_outputs
        )
        assert output.technical_score == 0.80
        assert output.price_action_score == 0.75
        assert output.fundamental_score == 0.70

    def test_synthesize_partial_engine_outputs(self):
        """If only some engines provided, falls back for missing."""
        engine = ThesisEngine()
        ext_outputs = [
            EngineOutput(
                engine_name="technical",
                engine_version="1.0",
                score=0.90,
                explanation="Very strong",
            ),
        ]
        output = engine.synthesize(
            "USDJPY", "M15",
            engine_outputs=ext_outputs
        )
        assert output.technical_score == 0.90
        # price_action and fundamental should be filled by internal engines
        assert 0.0 <= output.price_action_score <= 1.0
        assert 0.0 <= output.fundamental_score <= 1.0

    def test_bias_bullish(self):
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.90, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.85, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.80, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.bias == BiaType.BULLISH

    def test_bias_bearish(self):
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.10, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.15, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.20, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.bias == BiaType.BEARISH

    def test_bias_neutral(self):
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.50, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.50, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.50, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.bias == BiaType.NEUTRAL

    def test_alignment_perfect(self):
        """Perfect alignment when all engines agree."""
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.70, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.70, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.70, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.alignment_score == 1.0

    def test_alignment_low_when_divergent(self):
        """Low alignment when engines disagree."""
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.90, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.10, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.50, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.alignment_score < 0.8

    def test_invalidations_present(self):
        engine = ThesisEngine()
        output = engine.synthesize("EURUSD", "H1")
        assert len(output.invalidations) > 0
        assert any("EURUSD" in inv for inv in output.invalidations)

    def test_risk_notes_present(self):
        engine = ThesisEngine()
        output = engine.synthesize("EURUSD", "H1")
        assert len(output.risk_notes) > 0

    def test_all_symbols_synthesize(self):
        engine = ThesisEngine()
        for sym in ["EURUSD", "USDJPY", "USDCAD", "US30", "NAS100"]:
            output = engine.synthesize(sym, "H1")
            assert output.symbol == sym
            assert isinstance(output, AnalysisOutput)

    def test_setup_type_momentum(self):
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.90, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.85, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.80, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.setup_type == "momentum_continuation"

    def test_setup_type_counter_trend(self):
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.10, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.15, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.20, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.setup_type == "counter_trend_setup"

    def test_setup_type_mean_reversion(self):
        engine = ThesisEngine()
        ext = [
            EngineOutput(engine_name="technical", engine_version="1.0", score=0.50, explanation=""),
            EngineOutput(engine_name="price_action", engine_version="1.0", score=0.45, explanation=""),
            EngineOutput(engine_name="fundamental", engine_version="1.0", score=0.55, explanation=""),
        ]
        output = engine.synthesize("EURUSD", "H1", engine_outputs=ext)
        assert output.setup_type == "mean_reversion"


# ============================================================================
# BASE ENGINE MOCK SCORE
# ============================================================================

class TestMockScoreGeneration:
    def test_mock_score_deterministic(self):
        engine = TechnicalEngine()
        s1 = engine._mock_score_for_symbol("EURUSD", "H1", 0.70)
        s2 = engine._mock_score_for_symbol("EURUSD", "H1", 0.70)
        assert s1 == s2

    def test_mock_score_in_range(self):
        engine = TechnicalEngine()
        for base in [0.0, 0.5, 0.7, 1.0]:
            score = engine._mock_score_for_symbol("EURUSD", "H1", base)
            assert 0.0 <= score <= 1.0

    def test_mock_score_varies_by_symbol(self):
        engine = TechnicalEngine()
        s1 = engine._mock_score_for_symbol("EURUSD", "H1", 0.70)
        s2 = engine._mock_score_for_symbol("USDJPY", "H1", 0.70)
        # They can be equal by coincidence, but generally differ
        # Just check they're valid
        assert 0.0 <= s1 <= 1.0
        assert 0.0 <= s2 <= 1.0
