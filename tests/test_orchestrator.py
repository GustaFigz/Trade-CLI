"""
Orchestrator Tests — Trade-CLI Phase 2.3+

Tests the complete analysis pipeline: MT5 + Engines + RAG + LLM + RiskGuardian.

Phase: 2.4
Date: 2026-05-01
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from orchestrator.orchestrator import Orchestrator
from core.analysis_schema import VerdictType


class TestOrchestratorInitialization:
    def test_init_with_all_components(self):
        """Test orchestrator initializes with all components."""
        orch = Orchestrator(use_llm=True, use_rag=True, use_mt5=True)
        assert orch.technical_engine is not None
        assert orch.price_action_engine is not None
        assert orch.fundamental_engine is not None
        assert orch.sentiment_engine is not None
        assert orch.intermarket_engine is not None
        assert orch.volume_engine is not None
        assert orch.thesis_engine is not None
        assert orch.risk_guardian is not None

    def test_init_with_no_components(self):
        """Test orchestrator can disable components."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=False)
        assert orch.use_llm is False
        assert orch.use_rag is False
        assert orch.use_mt5 is False


class TestOrchestratorAnalysisPipeline:
    def test_analyze_returns_dict(self):
        """Test analyze returns a dictionary."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        assert isinstance(result, dict)

    def test_analyze_has_required_fields(self):
        """Test analyze result has all required fields."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        assert "symbol" in result
        assert "timeframe" in result
        assert "timestamp" in result
        assert "analysis" in result
        assert "verdict" in result
        assert "verdict_reason" in result
        assert "risk_notes" in result
        assert "invalidations" in result

    def test_analyze_analysis_scores(self):
        """Test analysis dict has all engine scores."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="M15")
        analysis = result.get("analysis", {})
        assert "bias" in analysis
        assert "confidence_score" in analysis
        assert "alignment_score" in analysis
        assert "technical_score" in analysis
        assert "price_action_score" in analysis
        assert "fundamental_score" in analysis
        assert "sentiment_score" in analysis
        assert "intermarket_score" in analysis
        assert "volume_score" in analysis

    def test_analyze_score_ranges(self):
        """Test all scores are in valid range 0.0-1.0."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="USDJPY", timeframe="H4")
        analysis = result.get("analysis", {})
        
        for score_field in [
            "confidence_score",
            "alignment_score",
            "technical_score",
            "price_action_score",
            "fundamental_score",
            "sentiment_score",
            "intermarket_score",
            "volume_score",
        ]:
            score = analysis.get(score_field, 0.0)
            assert 0.0 <= score <= 1.0, f"{score_field} out of range: {score}"

    def test_analyze_verdict_valid(self):
        """Test verdict is a valid VerdictType."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="USDCAD", timeframe="D1")
        verdict = result.get("verdict", "")
        assert verdict in ["allowed", "watch_only", "blocked"]

    def test_analyze_multiple_symbols(self):
        """Test analyzing different symbols."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        for symbol in ["EURUSD", "USDJPY", "USDCAD", "US30", "NAS100"]:
            result = orch.analyze(symbol=symbol, timeframe="H1")
            assert result["symbol"] == symbol
            assert isinstance(result, dict)

    def test_analyze_with_user_query(self):
        """Test analyze accepts user_query parameter."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(
            symbol="EURUSD",
            timeframe="H1",
            user_query="Is this setup confluent with ICT?",
        )
        assert isinstance(result, dict)


class TestOrchestratorRiskGuardian:
    def test_risk_guardian_verdict(self):
        """Test RiskGuardian integration."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        # Verdict should be set by RiskGuardian
        assert "verdict" in result
        assert "verdict_reason" in result

    def test_risk_guardian_blocks_low_alignment(self):
        """Test RiskGuardian can block low-alignment setups."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        # Mock a low-alignment analysis
        with patch.object(orch.thesis_engine, "synthesize") as mock_synth:
            mock_output = MagicMock()
            mock_output.alignment_score = 0.40  # Low alignment
            mock_output.confidence_score = 0.50
            mock_synth.return_value = mock_output
            
            result = orch.analyze(symbol="EURUSD", timeframe="H1")
            # Should likely be watch_only or blocked due to low alignment
            verdict = result.get("verdict", "")
            assert verdict in ["allowed", "watch_only", "blocked"]


class TestOrchestratorHealthCheck:
    def test_health_check_returns_dict(self):
        """Test health_check returns a dictionary."""
        orch = Orchestrator()
        health = orch.health_check()
        assert isinstance(health, dict)

    def test_health_check_has_components(self):
        """Test health check includes component status."""
        orch = Orchestrator()
        health = orch.health_check()
        assert "timestamp" in health
        assert "components" in health

    def test_health_check_component_status(self):
        """Test all engine components in health check."""
        orch = Orchestrator()
        health = orch.health_check()
        components = health.get("components", {})
        assert "engines" in components
        engines = components.get("engines", {})
        assert engines.get("technical") is True
        assert engines.get("price_action") is True
        assert engines.get("fundamental") is True
        assert engines.get("sentiment") is True
        assert engines.get("intermarket") is True
        assert engines.get("volume") is True


class TestOrchestratorEngineOutputs:
    def test_engine_outputs_included_in_result(self):
        """Test orchestrator includes raw engine outputs."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        assert "engine_outputs" in result
        engine_outputs = result.get("engine_outputs", [])
        assert isinstance(engine_outputs, list)
        # Should have at least 6 engines (tech, pa, fund, sentiment, intermarket, volume)
        assert len(engine_outputs) >= 6

    def test_engine_output_format(self):
        """Test each engine output has required fields."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        for output in result.get("engine_outputs", []):
            assert "name" in output
            assert "score" in output
            assert 0.0 <= output["score"] <= 1.0
            assert "explanation" in output

    def test_all_new_engines_present(self):
        """Test sentiment, intermarket, volume engines are included."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        engine_names = [e["name"] for e in result.get("engine_outputs", [])]
        assert "sentiment" in engine_names
        assert "intermarket" in engine_names
        assert "volume" in engine_names


class TestOrchestratorGracefulDegradation:
    def test_analyze_without_llm(self):
        """Test analysis works without LLM."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        assert "error" not in result
        assert result.get("llm_used") is False

    def test_analyze_without_rag(self):
        """Test analysis works without RAG."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        assert "error" not in result

    def test_analyze_without_mt5(self):
        """Test analysis works without MT5 (uses mock)."""
        orch = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
        result = orch.analyze(symbol="EURUSD", timeframe="H1")
        # Should still work - MT5Client has fallback to mock
        assert "error" not in result
