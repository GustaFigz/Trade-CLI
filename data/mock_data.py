"""
Mock Data Generator — Trade-CLI Phase 2

Generates synthetic market data for testing and demo.
Used when MT5 is unavailable.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any


def get_mock_bars(symbol: str, timeframe: str, count: int = 500) -> pd.DataFrame:
    """
    Generate synthetic OHLCV bars.
    
    Args:
        symbol: Currency pair (e.g., "EURUSD")
        timeframe: Timeframe (e.g., "H1", "M15")
        count: Number of bars to generate
        
    Returns:
        DataFrame with OHLCV data
    """
    
    # Base prices per symbol
    prices = {
        "EURUSD": 1.0850,
        "USDJPY": 150.50,
        "USDCAD": 1.3650,
        "US30": 40000,
        "NAS100": 19500,
    }
    
    base_price = prices.get(symbol, 1.0)
    
    # Generate random walk
    np.random.seed(42)  # Reproducible
    
    # Determine timeframe in minutes
    tf_minutes = {
        "M1": 1, "M5": 5, "M15": 15, "H1": 60, "H4": 240, "D1": 1440
    }
    minutes = tf_minutes.get(timeframe, 60)
    
    # Generate data
    times = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    current_time = datetime.utcnow() - timedelta(minutes=count * minutes)
    current_price = base_price
    
    for i in range(count):
        times.append(current_time)
        
        # Random walk with mean reversion
        change = np.random.normal(0.0001, 0.0005)  # Small drift + volatility
        open_price = current_price
        close_price = current_price + change
        high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.0003))
        low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.0003))
        
        volume = int(np.random.uniform(100, 1000))
        
        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)
        volumes.append(volume)
        
        current_price = close_price
        current_time += timedelta(minutes=minutes)
    
    return pd.DataFrame({
        'time': times,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'tick_volume': volumes
    })


def get_mock_ticks(symbol: str, count: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic tick data.
    
    Args:
        symbol: Currency pair
        count: Number of ticks to generate
        
    Returns:
        DataFrame with tick data
    """
    
    prices = {
        "EURUSD": 1.0850,
        "USDJPY": 150.50,
        "USDCAD": 1.3650,
        "US30": 40000,
        "NAS100": 19500,
    }
    
    base_price = prices.get(symbol, 1.0)
    
    np.random.seed(42)
    
    times = []
    bids = []
    asks = []
    volumes = []
    
    current_time = datetime.utcnow() - timedelta(seconds=count)
    current_price = base_price
    
    for i in range(count):
        times.append(current_time)
        
        # Bid-ask spread
        tick_change = np.random.normal(0, 0.00001)
        bid = current_price + tick_change
        ask = bid + 0.0001  # Spread
        
        volume = int(np.random.uniform(0.01, 1.0, ))
        
        bids.append(bid)
        asks.append(ask)
        volumes.append(volume)
        
        current_price = (bid + ask) / 2
        current_time += timedelta(seconds=1)
    
    return pd.DataFrame({
        'time': times,
        'bid': bids,
        'ask': asks,
        'volume': volumes
    })


def get_mock_account_state() -> Dict[str, Any]:
    """
    Get mock account state.
    
    Returns:
        Dict with account metrics
    """
    return {
        "balance": 100000,
        "equity": 98500,
        "profit": -1500,
        "margin": 45000,
        "margin_free": 55000,
        "drawdown_pct": 1.5
    }
