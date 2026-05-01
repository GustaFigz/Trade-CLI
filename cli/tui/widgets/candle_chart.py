"""
Trade-CLI TUI — Candle Chart Widget
Displays ASCII candlestick chart using Unicode block elements.
Phase 3 TUI — Date: 2026-05-01
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.app import RenderResult
from rich.text import Text
from rich.panel import Panel
from typing import List, Dict, Any, Optional
from cli.tui.theme.candles import HEADER_FRAMES, bull_candle, bear_candle, doji_candle, score_bar
import asyncio


class CandleHeaderWidget(Widget):
    """
    Animated candle sequence for the app header.
    Cycles through HEADER_FRAMES at 150ms intervals.
    """
    
    DEFAULT_CSS = "CandleHeaderWidget { height: 1; }"
    
    frame: int = reactive(0)
    
    def on_mount(self) -> None:
        self.set_interval(0.15, self.advance_frame)
    
    def advance_frame(self) -> None:
        self.frame = (self.frame + 1) % len(HEADER_FRAMES)
    
    def render(self) -> RenderResult:
        return Text.from_markup(
            f"{HEADER_FRAMES[self.frame]}  "
            f"[bold #00e676]TRADE-CLI v2.0[/bold #00e676]  "
            f"{HEADER_FRAMES[(self.frame + 2) % len(HEADER_FRAMES)]}"
        )


class MiniCandleChart(Widget):
    """
    ASCII mini candlestick chart from OHLCV data.
    Displays last N candles in a fixed-height panel.
    """
    
    DEFAULT_CSS = "MiniCandleChart { height: 14; border: solid #1e1e1e; }"
    
    # Reactive data — updating this re-renders automatically
    candle_data: list = reactive([], layout=True)
    symbol: str = reactive("EURUSD")
    timeframe: str = reactive("H1")
    
    def set_data(self, candles: List[Dict[str, Any]], symbol: str, timeframe: str) -> None:
        """Update candle data. Each dict: {open, high, low, close}."""
        self.candle_data = candles[-20:]  # Show last 20 candles
        self.symbol = symbol
        self.timeframe = timeframe
    
    def render(self) -> RenderResult:
        if not self.candle_data:
            return Panel(
                Text("[dim]No data — run: analyze EURUSD H1[/dim]", justify="center"),
                title=f"[dim]{self.symbol} {self.timeframe}[/dim]",
                border_style="#1e1e1e",
            )
        
        chart_height = 8
        candles = self.candle_data
        
        # Normalize to chart height
        all_prices = [p for c in candles for p in [c['high'], c['low']]]
        price_min = min(all_prices)
        price_max = max(all_prices)
        price_range = price_max - price_min or 0.0001
        
        def to_row(price: float) -> int:
            return int((1 - (price - price_min) / price_range) * (chart_height - 1))
        
        # Build grid (rows × cols)
        cols = len(candles)
        grid = [[" " for _ in range(cols)] for _ in range(chart_height)]
        styles = [["" for _ in range(cols)] for _ in range(chart_height)]
        
        for col, candle in enumerate(candles):
            is_bull = candle['close'] >= candle['open']
            color = "green" if is_bull else "red"
            body_top = to_row(max(candle['open'], candle['close']))
            body_bot = to_row(min(candle['open'], candle['close']))
            wick_top = to_row(candle['high'])
            wick_bot = to_row(candle['low'])
            
            for row in range(chart_height):
                if row == wick_top:
                    grid[row][col] = "┬"
                    styles[row][col] = color
                elif wick_top < row < body_top:
                    grid[row][col] = "│"
                    styles[row][col] = color
                elif body_top <= row <= body_bot:
                    grid[row][col] = "█"
                    styles[row][col] = color
                elif body_bot < row < wick_bot:
                    grid[row][col] = "│"
                    styles[row][col] = color
                elif row == wick_bot:
                    grid[row][col] = "┴"
                    styles[row][col] = color
        
        # Render as Rich Text
        text = Text()
        for row in range(chart_height):
            for col in range(cols):
                char = grid[row][col]
                style = styles[row][col]
                if style:
                    text.append(char, style=style)
                else:
                    text.append(char, style="dim")
            text.append("\n")
        
        return Panel(
            text,
            title=f"[bold]{self.symbol}[/bold] [dim]{self.timeframe}[/dim]",
            border_style="#1e1e1e",
        )
