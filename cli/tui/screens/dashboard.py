"""
Trade-CLI TUI — Main Dashboard Screen
Arranges all widgets in the layout.
Phase 3 TUI — Date: 2026-05-01
"""

from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static
from cli.tui.widgets.candle_chart import CandleHeaderWidget, MiniCandleChart
from cli.tui.widgets.engine_scores import EngineScoresWidget
from cli.tui.widgets.verdict_panel import VerdictPanelWidget
from cli.tui.widgets.asset_sidebar import AssetSidebarWidget
from typing import Dict, Any


class DashboardScreen(Screen):
    """
    Main layout screen.
    Left: Sidebar (Assets/Vault).
    Center: Input bar & Candle Chart.
    Right: Analysis scores & Verdict.
    """
    
    def compose(self):
        yield CandleHeaderWidget(id="header")
        
        with Horizontal():
            # Left Sidebar
            yield Container(
                AssetSidebarWidget(id="asset-sidebar"),
                id="sidebar"
            )
            
            # Center Panel
            with Vertical(id="main-panel"):
                yield Input(placeholder="Analyze command (e.g., EURUSD H1)", id="input-bar")
                yield MiniCandleChart(id="candle-chart")
            
            # Right Panel
            with Vertical(id="right-panel"):
                yield VerdictPanelWidget(id="verdict-panel")
                yield EngineScoresWidget(id="engine-scores")
                
        yield Footer(id="footer")
    
    def on_mount(self):
        self.query_one("#input-bar").focus()
    
    def update_analysis(self, result: Dict[str, Any], symbol: str, timeframe: str, candles: list):
        """Update all widgets with new data."""
        self.query_one("#asset-sidebar").active_symbol = symbol
        self.query_one("#candle-chart").set_data(candles, symbol, timeframe)
        self.query_one("#engine-scores").update_scores(result.get("engine_outputs", []))
        self.query_one("#verdict-panel").update_verdict(result)
