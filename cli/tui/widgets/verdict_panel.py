"""
Trade-CLI TUI — Verdict Panel Widget
Shows FTMO RiskGuardian verdict with colour animation.
Phase 3 TUI — Date: 2026-05-01
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.app import RenderResult
from rich.panel import Panel
from rich.text import Text
from rich import box
from cli.tui.theme.candles import VERDICT_STYLES, BIAS_INDICATORS


class VerdictPanelWidget(Widget):
    """
    Displays the RiskGuardian verdict prominently.
    Green pulse for ALLOWED, red for BLOCKED, yellow for WATCH_ONLY.
    """
    
    DEFAULT_CSS = "VerdictPanelWidget { height: auto; padding: 0 1; }"
    
    verdict_str: str = reactive("pending")
    verdict_reason: str = reactive("")
    confidence: float = reactive(0.0)
    alignment: float = reactive(0.0)
    bias_str: str = reactive("neutral")
    setup_type: str = reactive("")
    
    def update_verdict(self, result: dict) -> None:
        """Update from Orchestrator result dict."""
        self.verdict_str   = result.get("verdict", "pending").lower()
        self.verdict_reason = result.get("verdict_reason", "")
        analysis = result.get("analysis", {})
        self.confidence    = analysis.get("confidence_score", 0.0)
        self.alignment     = analysis.get("alignment_score", 0.0)
        self.bias_str      = analysis.get("bias", "neutral")
        self.setup_type    = analysis.get("setup_type", "")
    
    def render(self) -> RenderResult:
        style_map = VERDICT_STYLES
        vstyle = style_map.get(self.verdict_str, style_map["watch_only"])
        icon   = vstyle["icon"]
        color  = vstyle["color"]
        
        bias_char, bias_color = BIAS_INDICATORS.get(self.bias_str, ("─", "white"))
        
        content = Text()
        content.append(f"  {icon}  {self.verdict_str.upper().replace('_', ' ')}  \n", style=color)
        content.append("─" * 20 + "\n", style="#333333")
        content.append("Confidence  ", style="#666666")
        content.append(f"{self.confidence:.0%}\n", style="bold white")
        content.append("Alignment   ", style="#666666")
        content.append(f"{self.alignment:.0%}\n", style="bold white")
        content.append("Bias        ", style="#666666")
        content.append(f"{bias_char} {self.bias_str.upper()}\n", style=f"bold {bias_color}")
        content.append("Setup       ", style="#666666")
        content.append(f"{self.setup_type or '—'}\n", style="cyan")
        
        if self.verdict_reason:
            content.append("\n", style="")
            content.append("Reason: ", style="#666666")
            content.append(self.verdict_reason[:40], style="italic dim")
        
        border_color = {
            "allowed": "#00c853",
            "blocked": "#ff1744",
            "watch_only": "#ffd600",
            "pending": "#333333",
        }.get(self.verdict_str, "#333333")
        
        return Panel(content, border_style=border_color, padding=(0, 1))
