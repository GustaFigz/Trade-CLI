"""
Tests for data providers — Fase 2.3.
Tests MockDataProvider class and backward-compatible functions.

Fase: 2.3
Data: 2026-05-01
"""
import pytest
from data.mock_data import MockDataProvider, SUPPORTED_SYMBOLS, TF_MINUTES, get_mock_bars, get_mock_account_state


class TestMockDataProvider:
    """Tests for the new MockDataProvider class."""

    def test_eurusd_bars(self):
        provider = MockDataProvider()
        bars = provider.get_bars("EURUSD", "H1", count=100)
        assert len(bars) == 100
        assert "open" in bars.columns
        assert "high" in bars.columns
        assert "low" in bars.columns
        assert "close" in bars.columns
        assert "volume" in bars.columns
        assert "timestamp" in bars.columns

    def test_bars_ohlc_logic(self):
        """High must be >= open and close; Low must be <= open and close."""
        provider = MockDataProvider()
        bars = provider.get_bars("EURUSD", "H1", count=50)
        for _, row in bars.iterrows():
            assert row["high"] >= row["open"], "High must be >= open"
            assert row["high"] >= row["close"], "High must be >= close"
            assert row["low"] <= row["open"], "Low must be <= open"
            assert row["low"] <= row["close"], "Low must be <= close"

    def test_unsupported_symbol_raises(self):
        provider = MockDataProvider()
        with pytest.raises(ValueError, match="não suportado"):
            provider.get_bars("NZDUSD", "H1")

    def test_unknown_symbol_raises(self):
        provider = MockDataProvider()
        with pytest.raises(ValueError):
            provider.get_bars("GBPCHF", "H1")

    def test_all_supported_symbols(self):
        provider = MockDataProvider()
        for symbol in SUPPORTED_SYMBOLS:
            bars = provider.get_bars(symbol, "H1", count=10)
            assert len(bars) == 10

    def test_different_timeframes(self):
        provider = MockDataProvider()
        for tf in ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]:
            bars = provider.get_bars("EURUSD", tf, count=5)
            assert len(bars) == 5

    def test_w1_timeframe(self):
        """W1 timeframe should work."""
        provider = MockDataProvider()
        bars = provider.get_bars("EURUSD", "W1", count=5)
        assert len(bars) == 5

    def test_invalid_timeframe_rejected(self):
        provider = MockDataProvider()
        with pytest.raises(ValueError, match="não reconhecido"):
            provider.get_bars("EURUSD", "H99")

    def test_account_state(self):
        provider = MockDataProvider()
        state = provider.get_account_state()
        assert state.balance == 100_000.0
        assert state.drawdown_pct >= 0
        assert state.margin_free > 0
        assert state.equity > 0

    def test_get_spread(self):
        provider = MockDataProvider()
        spread = provider.get_spread("EURUSD")
        assert spread == 0.8
        spread_unknown = provider.get_spread("UNKNOWN")
        assert spread_unknown == 1.5  # default

    def test_is_mock(self):
        provider = MockDataProvider()
        assert provider.is_mock() is True

    def test_bar_count_matches_request(self):
        provider = MockDataProvider()
        for count in [1, 10, 50, 200]:
            bars = provider.get_bars("EURUSD", "H1", count=count)
            assert len(bars) == count

    def test_supported_symbols_set(self):
        """SUPPORTED_SYMBOLS should be a set with 5 elements."""
        assert isinstance(SUPPORTED_SYMBOLS, set)
        assert len(SUPPORTED_SYMBOLS) == 5
        assert "EURUSD" in SUPPORTED_SYMBOLS
        assert "NZDUSD" not in SUPPORTED_SYMBOLS

    def test_tf_minutes_has_m30_w1(self):
        """TF_MINUTES should include M30 and W1."""
        assert "M30" in TF_MINUTES
        assert "W1" in TF_MINUTES


class TestBackwardCompatFunctions:
    """Tests for backward-compatible module-level functions."""

    def test_get_mock_bars_legacy(self):
        bars = get_mock_bars("EURUSD", "H1", count=100)
        assert len(bars) == 100
        assert "time" in bars.columns
        assert "tick_volume" in bars.columns

    def test_get_mock_account_state_legacy(self):
        state = get_mock_account_state()
        assert "balance" in state
        assert state["balance"] > 0
