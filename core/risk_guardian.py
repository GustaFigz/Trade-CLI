"""
RiskGuardian - Deterministic Risk Management Layer

The RiskGuardian applies FTMO rules to analysis and returns a veto or approval.
This is the "NO" layer that prevents bad trades from happening.

Phase 1: Core veto logic (deterministic, no randomness)
Date: 2025-04-30
"""

from core.analysis_schema import AnalysisOutput, ProposalVerdictOutput, VerdictType
from typing import Dict, Any, List
import yaml
from pathlib import Path


class RiskGuardian:
    """
    Deterministic risk management gate. All verdicts are rule-based.
    
    Checks (in order):
    1. Drawdown limits (daily, total)
    2. Risk per trade
    3. News blackout
    4. Correlation with open positions
    5. Trade count limits
    6. Quality filters (confidence, alignment, context)
    
    Returns: allowed / watch_only / blocked
    """
    
    def __init__(self, rules_path: str = "config/ftmo-rules.yaml"):
        """
        Initialize RiskGuardian with rules.
        
        Args:
            rules_path: Path to ftmo-rules.yaml
        """
        self.rules = self._load_rules(rules_path)
        self.current_daily_loss_pct = 0.0  # Placeholder (would be tracked in production)
        self.current_total_loss_pct = 0.0  # Placeholder
        self.trades_today = 0               # Placeholder
        self.open_positions = {}            # Dict of {symbol: position}
    
    def _load_rules(self, rules_path: str) -> Dict[str, Any]:
        """Load FTMO rules from YAML file."""
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove document separators to handle multi-document YAML
                content = content.replace('\n---\n', '\n')
                return yaml.safe_load(content) or self._default_rules()
        except FileNotFoundError:
            # Fallback to default rules if file not found
            return self._default_rules()
        except yaml.YAMLError:
            return self._default_rules()
    
    def _default_rules(self) -> Dict[str, Any]:
        """Default FTMO rules (Fase 1 hardcoded)"""
        return {
            'drawdown_limits': {
                'daily_max_loss_percent': 5.0,
                'total_max_loss_percent': 10.0,
            },
            'risk_per_trade': {
                'max_risk_percent': 1.0,
                'min_risk_percent': 0.5,
            },
            'session_rules': {
                'news_blackout': {
                    'enabled': True,
                    'minutes_before': 15,
                    'minutes_after': 15,
                },
                'correlation_block': {
                    'enabled': True,
                    'max_correlation': 0.7,
                },
                'max_trades_per_day': 8,
            },
            'quality_filters': {
                'min_confidence_score': 0.50,
                'min_alignment_score': 0.50,
                'min_context_quality': 0.55,
            },
        }
    
    def should_block(self, analysis: AnalysisOutput) -> ProposalVerdictOutput:
        """
        Main gate function. Determines if analysis should be allowed.
        
        Args:
            analysis: AnalysisOutput from ThesisEngine
        
        Returns:
            ProposalVerdictOutput with verdict and reasoning
        """
        
        checks_passed = {}
        violated_rules = []
        
        # ---- CHECK 1: Drawdown Limits ----
        daily_check = self._check_drawdown_daily()
        checks_passed['drawdown_daily_ok'] = daily_check['ok']
        if not daily_check['ok']:
            violated_rules.append(daily_check['reason'])
        
        total_check = self._check_drawdown_total()
        checks_passed['drawdown_total_ok'] = total_check['ok']
        if not total_check['ok']:
            violated_rules.append(total_check['reason'])
        
        if violated_rules:  # Any drawdown violation → BLOCKED
            return ProposalVerdictOutput(
                verdict=VerdictType.BLOCKED,
                reason=f"Drawdown limit exceeded: {violated_rules[0]}",
                violated_rules=violated_rules,
                checks_passed=checks_passed,
            )
        
        # ---- CHECK 2: Risk Per Trade ----
        risk_check = self._check_risk_per_trade(analysis)
        checks_passed['risk_per_trade_ok'] = risk_check['ok']
        if not risk_check['ok']:
            violated_rules.append(risk_check['reason'])
            return ProposalVerdictOutput(
                verdict=VerdictType.BLOCKED,
                reason=risk_check['reason'],
                violated_rules=violated_rules,
                checks_passed=checks_passed,
            )
        
        # ---- CHECK 3: News Blackout ----
        news_check = self._check_news_blackout()
        checks_passed['news_blackout_ok'] = news_check['ok']
        if not news_check['ok']:
            violated_rules.append(news_check['reason'])
            return ProposalVerdictOutput(
                verdict=VerdictType.BLOCKED,
                reason=news_check['reason'],
                violated_rules=violated_rules,
                checks_passed=checks_passed,
            )
        
        # ---- CHECK 4: Correlation Block ----
        correlation_check = self._check_correlation(analysis)
        checks_passed['correlation_ok'] = correlation_check['ok']
        if not correlation_check['ok']:
            violated_rules.append(correlation_check['reason'])
            return ProposalVerdictOutput(
                verdict=VerdictType.BLOCKED,
                reason=correlation_check['reason'],
                violated_rules=violated_rules,
                checks_passed=checks_passed,
            )
        
        # ---- CHECK 5: Trade Count ----
        trade_count_check = self._check_trade_count()
        checks_passed['trade_count_ok'] = trade_count_check['ok']
        if not trade_count_check['ok']:
            violated_rules.append(trade_count_check['reason'])
            return ProposalVerdictOutput(
                verdict=VerdictType.BLOCKED,
                reason=trade_count_check['reason'],
                violated_rules=violated_rules,
                checks_passed=checks_passed,
            )
        
        # ---- CHECK 6: Quality Filters ----
        quality_check = self._check_quality_filters(analysis)
        checks_passed['quality_confidence_ok'] = quality_check['confidence_ok']
        checks_passed['quality_alignment_ok'] = quality_check['alignment_ok']
        checks_passed['quality_context_ok'] = quality_check['context_ok']
        
        if not quality_check['all_ok']:
            # Quality issue → watch_only (not allowed, but not hard block)
            return ProposalVerdictOutput(
                verdict=VerdictType.WATCH_ONLY,
                reason=quality_check['reason'],
                violated_rules=[],  # Not a rule violation, just low quality
                checks_passed=checks_passed,
            )
        
        # ---- ALL CHECKS PASSED ----
        return ProposalVerdictOutput(
            verdict=VerdictType.ALLOWED,
            reason="All checks passed, good confluence",
            violated_rules=[],
            checks_passed=checks_passed,
        )
    
    # ========== INDIVIDUAL CHECK METHODS ==========
    
    def _check_drawdown_daily(self) -> Dict[str, Any]:
        """Check if daily loss exceeds limit"""
        max_loss = self.rules['drawdown_limits']['daily_max_loss_percent']
        
        if self.current_daily_loss_pct >= max_loss:
            return {
                'ok': False,
                'reason': f"Daily loss {self.current_daily_loss_pct}% >= {max_loss}% limit",
            }
        return {'ok': True, 'reason': ''}
    
    def _check_drawdown_total(self) -> Dict[str, Any]:
        """Check if total loss exceeds limit"""
        max_loss = self.rules['drawdown_limits']['total_max_loss_percent']
        
        if self.current_total_loss_pct >= max_loss:
            return {
                'ok': False,
                'reason': f"Total loss {self.current_total_loss_pct}% >= {max_loss}% limit",
            }
        return {'ok': True, 'reason': ''}
    
    def _check_risk_per_trade(self, analysis: AnalysisOutput) -> Dict[str, Any]:
        """
        Check if proposed risk respects FTMO limits.
        
        Note: In Phase 1, we don't have actual position sizing yet.
        In Phase 2, this will calculate actual risk from entry/stop.
        """
        max_risk = self.rules['risk_per_trade']['max_risk_percent']
        
        # Placeholder: Assume conservative 0.5% for now
        # In Phase 2: proposed_risk = (stop_loss_pips / account_balance) * 100
        proposed_risk = 0.75  # Mock value
        
        if proposed_risk > max_risk:
            return {
                'ok': False,
                'reason': f"Proposed risk {proposed_risk}% > {max_risk}% limit",
            }
        return {'ok': True, 'reason': ''}
    
    def _check_news_blackout(self) -> Dict[str, Any]:
        """Check if upcoming major news"""
        # Placeholder: In Phase 2, would check actual calendar
        # For now, assume no blackout
        return {'ok': True, 'reason': ''}
    
    def _check_correlation(self, analysis: AnalysisOutput) -> Dict[str, Any]:
        """Check for high correlation with open positions"""
        max_corr = self.rules['session_rules']['correlation_block']['max_correlation']
        
        if not self.open_positions:
            return {'ok': True, 'reason': ''}
        
        # Placeholder: In Phase 2, would calculate actual correlations
        # For now, assume no correlation issues
        return {'ok': True, 'reason': ''}
    
    def _check_trade_count(self) -> Dict[str, Any]:
        """Check if daily trade limit exceeded"""
        max_trades = self.rules['session_rules']['max_trades_per_day']
        
        if self.trades_today >= max_trades:
            return {
                'ok': False,
                'reason': f"Daily trade limit {max_trades} reached ({self.trades_today} trades)",
            }
        return {'ok': True, 'reason': ''}
    
    def _check_quality_filters(self, analysis: AnalysisOutput) -> Dict[str, Any]:
        """Check confidence, alignment, and context quality"""
        min_confidence = self.rules['quality_filters']['min_confidence_score']
        min_alignment = self.rules['quality_filters']['min_alignment_score']
        min_context = self.rules['quality_filters']['min_context_quality']
        
        checks = {
            'confidence_ok': analysis.confidence_score >= min_confidence,
            'alignment_ok': analysis.alignment_score >= min_alignment,
            'context_ok': True,  # Placeholder: context_quality not in AnalysisOutput yet
        }
        
        failed_checks = []
        if not checks['confidence_ok']:
            failed_checks.append(f"confidence {analysis.confidence_score:.0%} < {min_confidence:.0%}")
        if not checks['alignment_ok']:
            failed_checks.append(f"alignment {analysis.alignment_score:.0%} < {min_alignment:.0%}")
        
        return {
            'all_ok': all(checks.values()),
            'confidence_ok': checks['confidence_ok'],
            'alignment_ok': checks['alignment_ok'],
            'context_ok': checks['context_ok'],
            'reason': f"Quality issue: {', '.join(failed_checks)}" if failed_checks else "",
        }
    
    def update_state(self, daily_loss: float, total_loss: float, trades_count: int):
        """
        Update RiskGuardian state (called from main loop).
        
        Args:
            daily_loss: Current daily loss %
            total_loss: Total loss %
            trades_count: Number of trades today
        """
        self.current_daily_loss_pct = daily_loss
        self.current_total_loss_pct = total_loss
        self.trades_today = trades_count


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    from core.analysis_schema import BiaType, AnalysisType
    
    # Initialize RiskGuardian
    guardian = RiskGuardian()
    
    # Create a test analysis
    analysis_good = AnalysisOutput(
        symbol="NZDUSD",
        timeframe="M15",
        bias=BiaType.BULLISH,
        setup_type="liquidity_sweep_reclaim",
        confidence_score=0.75,
        alignment_score=0.68,
        technical_score=0.70,
        price_action_score=0.65,
        fundamental_score=0.70,
    )
    
    analysis_poor = AnalysisOutput(
        symbol="NZDUSD",
        timeframe="M15",
        bias=BiaType.BULLISH,
        setup_type="liquidity_sweep_reclaim",
        confidence_score=0.45,  # < 0.50
        alignment_score=0.40,   # < 0.50
        technical_score=0.50,
        price_action_score=0.40,
        fundamental_score=0.35,
    )
    
    # Test verdicts
    print("=" * 60)
    print("RISK GUARDIAN TEST")
    print("=" * 60)
    
    verdict_good = guardian.should_block(analysis_good)
    print(f"\nGood Analysis: {verdict_good.verdict.value}")
    print(f"Reason: {verdict_good.reason}")
    
    verdict_poor = guardian.should_block(analysis_poor)
    print(f"\nPoor Analysis: {verdict_poor.verdict.value}")
    print(f"Reason: {verdict_poor.reason}")
