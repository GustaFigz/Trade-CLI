"""
Data Plane — Trade-CLI Phase 2

Provides abstraction layer for:
- MT5 data access (read-only)
- Mock data for testing
- Market data (OHLCV bars, ticks)
- Economic calendar
"""

from data.mt5_client import MT5Client
from data.mock_data import get_mock_bars, get_mock_ticks, get_mock_account_state

__all__ = [
    "MT5Client",
    "get_mock_bars",
    "get_mock_ticks",
    "get_mock_account_state"
]
