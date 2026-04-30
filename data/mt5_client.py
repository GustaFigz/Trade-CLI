"""
MT5 Client — Trade-CLI Phase 2
Read-only data access to MetaTrader5

Falls back to mock data if MT5 not available.
"""

from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MT5Client:
    """
    Wrapper for MetaTrader5 Python API.
    Read-only access only (no order placement).
    Fallsback to mock data if MT5 unavailable.
    """
    
    def __init__(self, fallback_to_mock: bool = True):
        """
        Initialize MT5 client.
        
        Args:
            fallback_to_mock: If True, use mock data when MT5 unavailable
        """
        self.connected = False
        self.fallback_to_mock = fallback_to_mock
        self.mt5 = None
        
        # Try to import MT5
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            logger.info("MetaTrader5 module loaded")
        except ImportError:
            logger.warning("MetaTrader5 not installed. Using mock data.")
            self.fallback_to_mock = True
    
    def connect(self, login: int = None, password: str = None, server: str = None) -> bool:
        """
        Connect to MT5 (optional credentials).
        
        Returns:
            True if connected (or fallback enabled), False otherwise
        """
        if not self.mt5:
            if self.fallback_to_mock:
                logger.info("MT5 not available. Using mock data mode.")
                return True
            return False
        
        try:
            if login and password and server:
                if self.mt5.initialize(login=login, password=password, server=server):
                    self.connected = True
                    logger.info("Connected to MT5")
                    return True
            else:
                # Try default initialization
                if self.mt5.initialize():
                    self.connected = True
                    logger.info("Connected to MT5 (default)")
                    return True
        except Exception as e:
            logger.error(f"MT5 connection failed: {e}")
            if self.fallback_to_mock:
                logger.info("Falling back to mock data")
                return True
            return False
        
        return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.mt5 and self.connected:
            self.mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
    
    def get_bars(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """
        Get OHLCV bars (read-only).
        
        Args:
            symbol: Currency pair (e.g., "EURUSD")
            timeframe: Timeframe (e.g., "H1", "M15")
            count: Number of bars
            
        Returns:
            DataFrame with OHLCV data, or None if failed
        """
        if self.connected and self.mt5:
            try:
                # Convert timeframe string to MT5 constant
                tf_map = {
                    "M1": self.mt5.TIMEFRAME_M1,
                    "M5": self.mt5.TIMEFRAME_M5,
                    "M15": self.mt5.TIMEFRAME_M15,
                    "H1": self.mt5.TIMEFRAME_H1,
                    "H4": self.mt5.TIMEFRAME_H4,
                    "D1": self.mt5.TIMEFRAME_D1,
                    "W1": self.mt5.TIMEFRAME_W1,
                    "MN": self.mt5.TIMEFRAME_MN1,
                }
                
                tf_const = tf_map.get(timeframe.upper())
                if not tf_const:
                    logger.error(f"Unknown timeframe: {timeframe}")
                    return None
                
                rates = self.mt5.copy_rates_from_pos(symbol, tf_const, 0, count)
                if rates is not None:
                    df = pd.DataFrame(rates)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    return df[['time', 'open', 'high', 'low', 'close', 'tick_volume']].copy()
                    
            except Exception as e:
                logger.error(f"Error fetching bars: {e}")
        
        # Fallback to mock
        if self.fallback_to_mock:
            from data.mock_data import get_mock_bars
            return get_mock_bars(symbol, timeframe, count)
        
        return None
    
    def get_ticks(self, symbol: str, count: int = 1000) -> Optional[pd.DataFrame]:
        """
        Get tick data (read-only).
        
        Args:
            symbol: Currency pair
            count: Number of ticks
            
        Returns:
            DataFrame with tick data, or None if failed
        """
        if self.connected and self.mt5:
            try:
                ticks = self.mt5.copy_ticks_from(symbol, datetime.utcnow(), count, self.mt5.COPY_TICKS_ALL)
                if ticks is not None:
                    df = pd.DataFrame(ticks)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    return df[['time', 'bid', 'ask', 'volume']].copy()
                    
            except Exception as e:
                logger.error(f"Error fetching ticks: {e}")
        
        # Fallback to mock
        if self.fallback_to_mock:
            from data.mock_data import get_mock_ticks
            return get_mock_ticks(symbol, count)
        
        return None
    
    def get_spread(self, symbol: str) -> Optional[float]:
        """
        Get current spread in pips (read-only).
        
        Args:
            symbol: Currency pair
            
        Returns:
            Spread in pips, or None if unavailable
        """
        if self.connected and self.mt5:
            try:
                info = self.mt5.symbol_info(symbol)
                if info:
                    spread = info.spread / (10 ** info.digits)
                    return spread
            except Exception as e:
                logger.error(f"Error fetching spread: {e}")
        
        # Mock value
        return 1.5  # typical spread in pips
    
    def get_account_state(self) -> Dict[str, Any]:
        """
        Get account state (read-only).
        
        Returns:
            Dict with balance, equity, profit, margin, drawdown
        """
        if self.connected and self.mt5:
            try:
                acc = self.mt5.account_info()
                if acc:
                    return {
                        "balance": acc.balance,
                        "equity": acc.equity,
                        "profit": acc.profit,
                        "margin": acc.margin,
                        "margin_free": acc.margin_free,
                        "drawdown_pct": ((acc.balance - acc.equity) / acc.balance * 100) if acc.balance > 0 else 0
                    }
            except Exception as e:
                logger.error(f"Error fetching account state: {e}")
        
        # Mock value
        from data.mock_data import get_mock_account_state
        return get_mock_account_state()
    
    def is_market_open(self, symbol: str) -> bool:
        """
        Check if market is open for symbol (read-only).
        
        Args:
            symbol: Currency pair
            
        Returns:
            True if market open, False otherwise
        """
        if self.connected and self.mt5:
            try:
                info = self.mt5.symbol_info(symbol)
                if info:
                    return info.trade_mode != self.mt5.SYMBOL_TRADE_MODE_DISABLED
            except Exception as e:
                logger.error(f"Error checking market: {e}")
        
        # Assume forex is open
        return True
