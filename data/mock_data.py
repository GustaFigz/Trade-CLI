"""
Mock Data Provider — Trade-CLI Fase 2
Interface idêntica ao MT5Client para uso em testes e dev.
Quando MT5 disponível, trocar apenas o provider, não os engines.

Também mantém as funções originais get_mock_bars() e get_mock_ticks()
para backward compatibility com o MT5Client existente.

Fase: 2.3
Data: 2026-05-01
"""
from __future__ import annotations

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class MarketBar:
    """Single OHLCV bar."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    spread: float


@dataclass
class AccountState:
    """Trading account state snapshot."""
    balance: float
    equity: float
    profit: float
    margin: float
    margin_free: float
    drawdown_pct: float


class MockDataProvider:
    """
    Provider de dados mock para desenvolvimento sem MT5.
    Simula comportamento realista de mercado para EURUSD, USDJPY, USDCAD, US30, NAS100.
    """

    BASE_PRICES: Dict[str, float] = {
        "EURUSD": 1.0850,
        "USDJPY": 154.50,
        "USDCAD": 1.3650,
        "US30": 38500.0,
        "NAS100": 17800.0,
    }

    VOLATILITY: Dict[str, float] = {
        "EURUSD": 0.0005,
        "USDJPY": 0.08,
        "USDCAD": 0.0006,
        "US30": 50.0,
        "NAS100": 80.0,
    }

    SPREADS: Dict[str, float] = {
        "EURUSD": 0.8,
        "USDJPY": 1.0,
        "USDCAD": 1.2,
        "US30": 3.0,
        "NAS100": 2.5,
    }

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        count: int = 200,
    ) -> pd.DataFrame:
        """Gera barras OHLCV realistas com tendência simulada."""
        if symbol not in self.BASE_PRICES:
            raise ValueError(
                f"Símbolo {symbol} não suportado. "
                f"Usar: {list(self.BASE_PRICES.keys())}"
            )

        price = self.BASE_PRICES[symbol]
        vol = self.VOLATILITY[symbol]

        tf_minutes = {
            "M1": 1, "M5": 5, "M15": 15,
            "H1": 60, "H4": 240, "D1": 1440,
        }
        minutes = tf_minutes.get(timeframe, 60)

        now = datetime.utcnow()
        timestamps = [
            now - timedelta(minutes=minutes * i) for i in range(count, 0, -1)
        ]

        closes = [price]
        for _ in range(count - 1):
            change = np.random.normal(0, vol)
            closes.append(max(closes[-1] + change, price * 0.5))

        bars = []
        for i, ts in enumerate(timestamps):
            c = closes[i]
            o = closes[i - 1] if i > 0 else c
            h = max(o, c) + abs(np.random.normal(0, vol * 0.5))
            l_val = min(o, c) - abs(np.random.normal(0, vol * 0.5))
            v = abs(np.random.normal(1000, 200))
            bars.append({
                "timestamp": ts,
                "open": round(o, 5),
                "high": round(h, 5),
                "low": round(l_val, 5),
                "close": round(c, 5),
                "volume": round(v, 2),
            })

        return pd.DataFrame(bars)

    def get_spread(self, symbol: str) -> float:
        """Get typical spread for symbol in pips."""
        return self.SPREADS.get(symbol, 1.5)

    def get_account_state(self) -> AccountState:
        """Get simulated account state."""
        balance = 100_000.0
        return AccountState(
            balance=balance,
            equity=balance * random.uniform(0.99, 1.01),
            profit=random.uniform(-500, 500),
            margin=balance * 0.05,
            margin_free=balance * 0.95,
            drawdown_pct=random.uniform(0, 2),
        )

    def is_mock(self) -> bool:
        """Identifies this as a mock provider."""
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# Backward-compatible module-level functions (used by MT5Client fallback)
# ═══════════════════════════════════════════════════════════════════════════════

_provider = MockDataProvider()


def get_mock_bars(symbol: str, timeframe: str, count: int = 500) -> pd.DataFrame:
    """
    Generate synthetic OHLCV bars (backward-compatible function).

    Args:
        symbol: Currency pair (e.g., "EURUSD")
        timeframe: Timeframe (e.g., "H1", "M15")
        count: Number of bars to generate

    Returns:
        DataFrame with OHLCV data
    """
    # Use legacy format with 'time' and 'tick_volume' column names
    # to maintain compatibility with MT5Client and existing code
    prices = {
        "EURUSD": 1.0850,
        "USDJPY": 150.50,
        "USDCAD": 1.3650,
        "US30": 40000,
        "NAS100": 19500,
    }

    base_price = prices.get(symbol, 1.0)

    np.random.seed(42)  # Reproducible

    tf_minutes = {
        "M1": 1, "M5": 5, "M15": 15, "H1": 60, "H4": 240, "D1": 1440
    }
    minutes = tf_minutes.get(timeframe, 60)

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

        change = np.random.normal(0.0001, 0.0005)
        open_price = current_price
        close_price = current_price + change
        high_price = max(open_price, close_price) + abs(
            np.random.normal(0, 0.0003)
        )
        low_price = min(open_price, close_price) - abs(
            np.random.normal(0, 0.0003)
        )

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
    Generate synthetic tick data (backward-compatible function).

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

        tick_change = np.random.normal(0, 0.00001)
        bid = current_price + tick_change
        ask = bid + 0.0001

        volume = int(np.random.uniform(0.01, 1.0))

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
    Get mock account state (backward-compatible function).

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
