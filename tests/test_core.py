"""
Unit Tests for Phase 1

Tests for RiskGuardian, dataclasses, and critical functionality.

Phase 1: Core tests (70%+ coverage of core/)
Date: 2025-04-30
"""

import unittest
from core.analysis_schema import (
    AnalysisOutput, EngineOutput, ProposalVerdictOutput,
    BiaType, VerdictType, AnalysisType
)
from core.risk_guardian import RiskGuardian
from engines import ThesisEngine
import json


# ============================================================================
# TEST DATACLASSES
# ============================================================================

class TestAnalysisOutput(unittest.TestCase):
    """Test AnalysisOutput dataclass"""
    
    def test_creation(self):
        """Test basic AnalysisOutput creation"""
        analysis = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            bias=BiaType.BULLISH,
            setup_type="liquidity_sweep",
            confidence_score=0.70,
            alignment_score=0.65,
        )
        
        self.assertEqual(analysis.symbol, "NZDUSD")
        self.assertEqual(analysis.timeframe, "M15")
        self.assertEqual(analysis.bias, BiaType.BULLISH)
        self.assertGreater(len(analysis.id), 0)  # Has UUID
    
    def test_validation_confidence(self):
        """Test that invalid confidence score raises error"""
        with self.assertRaises(ValueError):
            AnalysisOutput(
                symbol="NZDUSD",
                timeframe="M15",
                confidence_score=1.5,  # > 1.0
            )
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization"""
        original = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            bias=BiaType.BEARISH,
            confidence_score=0.75,
            alignment_score=0.60,
        )
        
        # Serialize
        json_str = original.to_json()
        self.assertIsInstance(json_str, str)
        
        # Verify JSON is valid
        data = json.loads(json_str)
        self.assertEqual(data['symbol'], 'NZDUSD')
        self.assertEqual(data['bias'], 'bearish')
        
        # Deserialize
        restored = AnalysisOutput.from_json(json_str)
        self.assertEqual(restored.symbol, original.symbol)
        self.assertEqual(restored.bias, original.bias)
        self.assertEqual(restored.confidence_score, original.confidence_score)


class TestEngineOutput(unittest.TestCase):
    """Test EngineOutput dataclass"""
    
    def test_creation(self):
        """Test basic EngineOutput creation"""
        output = EngineOutput(
            engine_name="technical",
            score=0.75,
            explanation="Trend confirmed",
        )
        
        self.assertEqual(output.engine_name, "technical")
        self.assertEqual(output.score, 0.75)
        self.assertGreater(len(output.id), 0)
    
    def test_validation_score(self):
        """Test that invalid score raises error"""
        with self.assertRaises(ValueError):
            EngineOutput(
                engine_name="technical",
                score=1.5,  # > 1.0
            )
    
    def test_with_evidence(self):
        """Test EngineOutput with evidence dict"""
        output = EngineOutput(
            engine_name="technical",
            score=0.70,
            explanation="MA crossover",
            evidence={"ma_20": 0.5850, "ma_50": 0.5820}
        )
        
        self.assertEqual(output.evidence['ma_20'], 0.5850)


# ============================================================================
# TEST RISK GUARDIAN
# ============================================================================

class TestRiskGuardian(unittest.TestCase):
    """Test RiskGuardian veto logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.guardian = RiskGuardian()
    
    def test_good_analysis_allowed(self):
        """Test that high-quality analysis is allowed"""
        analysis = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            bias=BiaType.BULLISH,
            setup_type="liquidity_sweep",
            confidence_score=0.75,      # > 0.50
            alignment_score=0.70,       # > 0.50
            technical_score=0.75,
            price_action_score=0.70,
            fundamental_score=0.65,
        )
        
        verdict = self.guardian.should_block(analysis)
        
        self.assertEqual(verdict.verdict, VerdictType.ALLOWED)
        self.assertEqual(verdict.reason, "All checks passed, good confluence")
    
    def test_low_confidence_watch_only(self):
        """Test that low confidence → watch_only"""
        analysis = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            confidence_score=0.45,      # < 0.50
            alignment_score=0.65,
        )
        
        verdict = self.guardian.should_block(analysis)
        
        self.assertEqual(verdict.verdict, VerdictType.WATCH_ONLY)
        self.assertIn("quality", verdict.reason.lower())
    
    def test_low_alignment_watch_only(self):
        """Test that low alignment → watch_only"""
        analysis = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            confidence_score=0.65,
            alignment_score=0.40,       # < 0.50
        )
        
        verdict = self.guardian.should_block(analysis)
        
        self.assertEqual(verdict.verdict, VerdictType.WATCH_ONLY)
    
    def test_drawdown_blocked(self):
        """Test that drawdown limit blocks"""
        self.guardian.current_daily_loss_pct = 5.5  # > 5.0 limit
        
        analysis = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            confidence_score=0.99,      # Even high confidence won't help
            alignment_score=0.99,
        )
        
        verdict = self.guardian.should_block(analysis)
        
        self.assertEqual(verdict.verdict, VerdictType.BLOCKED)
        self.assertIn("drawdown", verdict.reason.lower())
    
    def test_trade_count_blocked(self):
        """Test that max trades per day blocks"""
        self.guardian.trades_today = 8  # == max
        
        analysis = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            confidence_score=0.99,
            alignment_score=0.99,
        )
        
        verdict = self.guardian.should_block(analysis)
        
        self.assertEqual(verdict.verdict, VerdictType.BLOCKED)
        self.assertIn("limit", verdict.reason.lower())


# ============================================================================
# TEST ENGINES
# ============================================================================

class TestThesisEngine(unittest.TestCase):
    """Test ThesisEngine synthesis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = ThesisEngine()
    
    def test_synthesis(self):
        """Test that thesis synthesis works"""
        analysis = self.engine.synthesize(
            symbol="NZDUSD",
            timeframe="M15",
            analyst_notes="Test analysis",
        )
        
        self.assertEqual(analysis.symbol, "NZDUSD")
        self.assertEqual(analysis.timeframe, "M15")
        self.assertGreater(analysis.confidence_score, 0.0)
        self.assertGreater(analysis.alignment_score, 0.0)
        self.assertIsNotNone(analysis.bias)
    
    def test_scores_in_range(self):
        """Test that all scores are in valid range"""
        analysis = self.engine.synthesize("NZDUSD", "M15")
        
        self.assertGreaterEqual(analysis.confidence_score, 0.0)
        self.assertLessEqual(analysis.confidence_score, 1.0)
        self.assertGreaterEqual(analysis.alignment_score, 0.0)
        self.assertLessEqual(analysis.alignment_score, 1.0)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestFullPipeline(unittest.TestCase):
    """Test full analysis pipeline"""
    
    def test_analysis_to_verdict(self):
        """Test full pipeline: analysis → guardian verdict"""
        # Generate analysis
        thesis_engine = ThesisEngine()
        analysis = thesis_engine.synthesize("NZDUSD", "M15")
        
        # Get verdict
        guardian = RiskGuardian()
        verdict = guardian.should_block(analysis)
        
        # Check verdict is valid
        self.assertIn(verdict.verdict, [VerdictType.ALLOWED, VerdictType.WATCH_ONLY, VerdictType.BLOCKED])
        self.assertGreater(len(verdict.reason), 0)
    
    def test_json_roundtrip(self):
        """Test JSON serialization roundtrip"""
        original = AnalysisOutput(
            symbol="NZDUSD",
            timeframe="M15",
            bias=BiaType.BULLISH,
            setup_type="test_setup",
            confidence_score=0.70,
            alignment_score=0.65,
            technical_score=0.70,
            price_action_score=0.60,
            fundamental_score=0.65,
            invalidations=["condition 1", "condition 2"],
            risk_notes=["risk 1"],
        )
        
        # Roundtrip
        json_str = original.to_json()
        restored = AnalysisOutput.from_json(json_str)
        
        # Verify
        self.assertEqual(restored.symbol, original.symbol)
        self.assertEqual(restored.timeframe, original.timeframe)
        self.assertEqual(restored.confidence_score, original.confidence_score)
        self.assertEqual(restored.invalidations, original.invalidations)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
