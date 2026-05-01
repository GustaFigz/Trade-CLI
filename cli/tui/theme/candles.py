"""
Trade-CLI TUI — Candle Art Constants
Defines ASCII/Unicode representations for candlestick chart elements.
Phase 3 TUI — Date: 2026-05-01
"""

# Unicode block elements for candles
BLOCK_FULL  = "█"
BLOCK_UPPER = "▀"
BLOCK_LOWER = "▄"
BLOCK_LEFT  = "▌"
BLOCK_RIGHT = "▐"
LINE_VERT   = "│"
LINE_THIN   = "┃"

# Progress bar chars
BAR_FULL    = "█"
BAR_EMPTY   = "░"
BAR_HALF    = "▓"

# Candle building blocks (Rich markup strings)
def bull_candle(body_height: int = 3, wick_top: int = 1, wick_bot: int = 1) -> str:
    """Generate a bullish (green) candle as Rich markup string."""
    top_wick   = f"[green]{LINE_VERT}[/green]\n" * wick_top
    body       = f"[green]{BLOCK_FULL}[/green]\n" * body_height
    bot_wick   = f"[green]{LINE_VERT}[/green]\n" * wick_bot
    return top_wick + body + bot_wick

def bear_candle(body_height: int = 3, wick_top: int = 1, wick_bot: int = 1) -> str:
    """Generate a bearish (red) candle as Rich markup string."""
    top_wick   = f"[red]{LINE_VERT}[/red]\n" * wick_top
    body       = f"[red]{BLOCK_FULL}[/red]\n" * body_height
    bot_wick   = f"[red]{LINE_VERT}[/red]\n" * wick_bot
    return top_wick + body + bot_wick

def doji_candle() -> str:
    """Generate a doji candle (yellow)."""
    return f"[yellow]{LINE_VERT}\n─\n{LINE_VERT}[/yellow]"

# Animation frames for header (scrolling candle sequence)
HEADER_FRAMES = [
    "[green]▁[/green][red]▃[/red][green]▅[/green][red]▇[/red][green]█[/green][red]▆[/red][green]▄[/green][red]▂[/red]",
    "[green]▂[/green][red]▁[/red][green]▆[/green][red]█[/red][green]▇[/green][red]▅[/red][green]▃[/green][red]▄[/red]",
    "[red]▄[/red][green]▂[/green][red]█[/red][green]▅[/green][red]▁[/red][green]▇[/green][red]▆[/red][green]▃[/green]",
    "[red]▆[/red][green]▄[/green][red]▂[/red][green]█[/green][red]▃[/red][green]▁[/green][red]▇[/red][green]▅[/green]",
]

# Score bar builder
def score_bar(score: float, width: int = 12) -> str:
    """Generate a coloured progress bar for engine score."""
    filled = int(score * width)
    empty  = width - filled
    if score >= 0.65:
        color = "green"
    elif score >= 0.45:
        color = "yellow"
    else:
        color = "red"
    return f"[{color}]{BAR_FULL * filled}[/{color}][dim]{BAR_EMPTY * empty}[/dim]"

# Verdict styling
VERDICT_STYLES = {
    "allowed":    {"icon": "✅", "color": "bold green",   "bg": "on #003300"},
    "watch_only": {"icon": "👁",  "color": "bold yellow",  "bg": "on #332200"},
    "blocked":    {"icon": "🚫", "color": "bold red",     "bg": "on #330000"},
}

# Bias indicators
BIAS_INDICATORS = {
    "bullish": ("▲", "green"),
    "bearish": ("▼", "red"),
    "neutral": ("─", "yellow"),
    "fragile": ("◈", "yellow"),
}
