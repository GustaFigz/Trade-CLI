"""
Trade-CLI TUI — Main Application
Phase 3 TUI — Date: 2026-05-01
"""

import os
from textual.app import App
from textual.widgets import Input
from cli.tui.screens.dashboard import DashboardScreen
from orchestrator.orchestrator import Orchestrator

class TradeCLIApp(App):
    """
    Textual application for Trade-CLI.
    Loads theme and handles input processing.
    """
    
    CSS_PATH = "theme/trade_cli.tcss"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        # Ensure we run from root directory to find configs
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
        self.orchestrator = Orchestrator(use_llm=False, use_rag=False, use_mt5=True)
    
    def on_mount(self):
        self.push_screen(DashboardScreen())
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Handle analysis commands from input bar."""
        cmd = event.value.strip().upper().split()
        if len(cmd) >= 2:
            symbol = cmd[0]
            timeframe = cmd[1]
            
            event.input.value = "Analyzing..."
            
            # Run orchestrator
            try:
                # In a real app this should be non-blocking (async)
                # But for Phase 3 prototype we run synchronously for now
                result = self.orchestrator.analyze(symbol, timeframe)
                
                # Fetch recent candles for chart
                candles = []
                if self.orchestrator.mt5_client:
                    df = self.orchestrator.mt5_client.get_bars(symbol, timeframe, count=40)
                    if df is not None and not df.empty:
                        candles = df.to_dict('records')
                
                # Update UI
                screen = self.screen
                if isinstance(screen, DashboardScreen):
                    screen.update_analysis(result, symbol, timeframe, candles)
                    
            except Exception as e:
                event.input.value = f"Error: {e}"
            else:
                event.input.value = ""
        else:
            event.input.value = "Format: SYMBOL TIMEFRAME (e.g. EURUSD H1)"
