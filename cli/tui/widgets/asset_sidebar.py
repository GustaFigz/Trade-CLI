"""
Trade-CLI TUI — Asset Sidebar Widget
Lists configured trading assets from config/assets.yaml.
Phase 3 TUI — Date: 2026-05-01
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.app import RenderResult
from rich.text import Text
from pathlib import Path
import yaml


SUPPORTED_SYMBOLS = ["EURUSD", "USDJPY", "USDCAD", "US30", "NAS100"]


class AssetSidebarWidget(Widget):
    """
    Displays the list of configured assets in the sidebar.
    Shows active symbol with highlight.
    """
    
    DEFAULT_CSS = "AssetSidebarWidget { height: auto; padding: 0 1; }"
    
    active_symbol: str = reactive("EURUSD")
    
    def _load_assets(self) -> dict:
        try:
            with open("config/assets.yaml", "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            return cfg.get("assets", {})
        except Exception:
            return {}
    
    def render(self) -> RenderResult:
        assets = self._load_assets()
        text = Text()
        
        text.append("ASSETS\n", style="bold #444444")
        text.append("─" * 16 + "\n", style="#222222")
        
        # Forex
        forex = assets.get("forex_primary", {})
        for sym in forex:
            if sym == self.active_symbol:
                text.append(f"▶ {sym}\n", style="bold #00e676")
            else:
                text.append(f"  {sym}\n", style="#888888")
        
        # Indices
        indices = assets.get("indices_primary", {})
        if indices:
            text.append("\n", style="")
        for sym in indices:
            if sym == self.active_symbol:
                text.append(f"▶ {sym}\n", style="bold #00e676")
            else:
                text.append(f"  {sym}\n", style="#888888")
        
        # Vault stats
        vault = Path("Trade-CLI-Vault")
        if vault.exists():
            text.append("\nVAULT\n", style="bold #444444")
            text.append("─" * 16 + "\n", style="#222222")
            for folder in ["teses", "sessions", "post-mortems", "treino"]:
                count = len(list((vault / folder).glob("*.md"))) if (vault / folder).exists() else 0
                text.append(f"  {folder[:10]:<10} ", style="#666666")
                text.append(f"{count}\n", style="#888888")
        
        return text
