"""
Trade-CLI TUI — Engine Scores Widget
Displays engine analysis scores as coloured progress bars.
Phase 3 TUI — Date: 2026-05-01
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.app import RenderResult
from rich.text import Text
from rich.table import Table
from rich import box
from typing import List, Dict, Any
from cli.tui.theme.candles import score_bar


class EngineScoresWidget(Widget):
    """
    Displays all engine scores as labelled progress bars.
    Updates reactively when analysis result changes.
    """
    
    DEFAULT_CSS = "EngineScoresWidget { height: auto; padding: 0 1; }"
    
    engine_data: list = reactive([], layout=True)
    
    def update_scores(self, engine_outputs: List[Dict[str, Any]]) -> None:
        """Update with new engine outputs from Orchestrator result dict."""
        self.engine_data = engine_outputs
    
    def render(self) -> RenderResult:
        if not self.engine_data:
            return Text("[dim]Awaiting analysis...[/dim]")
        
        text = Text()
        text.append("ENGINE SCORES\n", style="bold #444444")
        text.append("─" * 22 + "\n", style="#222222")
        
        for eng in self.engine_data:
            name  = eng.get("name", "unknown").replace("_", " ").title()
            score = eng.get("score", 0.0)
            bar   = score_bar(score, width=10)
            pct   = f"{score:.0%}"
            
            # Pad name to 10 chars
            text.append(f"{name[:10]:<10} ", style="#888888")
            text.append_text(Text.from_markup(bar))
            text.append(f" {pct}\n", style="bold")
        
        return text
