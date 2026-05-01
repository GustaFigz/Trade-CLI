"""
Trade-CLI Launcher — Interface profissional do terminal.
Inspirado em Claude Code, OpenCode e Copilot CLI.
Splash animado + REPL interactivo + painel de estado.

Fase: 2.3
Data: 2026-05-01
"""
from __future__ import annotations

import sys
import time
import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.table import Table
from rich.align import Align
from rich.columns import Columns
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.rule import Rule
from rich import box
from rich.style import Style

console = Console()

# ── Paleta de cores Trade-CLI ──────────────────────────────────────────────────
ACCENT = "bright_cyan"
DIM = "dim white"
SUCCESS = "bright_green"
WARNING = "bright_yellow"
DANGER = "bright_red"
MUTED = "grey58"
HEADER_BG = "on black"

# ── ASCII Art do Trade-CLI ─────────────────────────────────────────────────────
LOGO_COMPACT = """
 ▀█▀ █▀█ ▄▀█ █▀▄ █▀▀   █▀▀ █░░ █
 ░█░ █▀▄ █▀█ █▄▀ ██▄   █▄▄ █▄▄ █
"""

TAGLINE = "Local AI Copilot for Forex Trading Decisions"
VERSION = "v0.2.0-phase2"


def render_splash() -> None:
    """Animação de entrada — estilo Claude Code."""
    console.clear()

    # Frame 1: logo aparece linha a linha
    logo_lines = LOGO_COMPACT.strip().split("\n")
    rendered = Text()
    for i, line in enumerate(logo_lines):
        time.sleep(0.08)
        rendered.append(line + "\n", style=f"bold {ACCENT}")
        console.clear()
        header = Panel(
            Align.center(rendered),
            border_style=ACCENT,
            padding=(0, 4),
        )
        console.print(header)

    # Frame 2: tagline e versão
    time.sleep(0.15)
    console.clear()

    logo_text = Text(LOGO_COMPACT.strip(), style=f"bold {ACCENT}")
    tagline_text = Text(f"\n  {TAGLINE}", style=f"italic {MUTED}")
    version_text = Text(f"  {VERSION}", style=f"dim {ACCENT}")

    panel = Panel(
        Align.center(
            Text.assemble(logo_text, tagline_text, "\n", version_text)
        ),
        border_style=ACCENT,
        padding=(1, 4),
        subtitle=Text("  Iniciando...", style=DIM),
    )
    console.print(panel)
    time.sleep(0.3)


def render_status_bar() -> Table:
    """Painel de estado do sistema."""
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column(style=MUTED, no_wrap=True)
    table.add_column(style="white", no_wrap=True)
    table.add_column(style=MUTED, no_wrap=True)
    table.add_column(style="white", no_wrap=True)

    # Verificar estado real dos serviços
    ollama_ok = _check_ollama()
    db_ok = _check_database()
    vault_ok = _check_vault()

    ollama_str = (
        Text("● Ollama OK", style=SUCCESS) if ollama_ok
        else Text("○ Ollama offline", style=WARNING)
    )
    db_str = (
        Text("● DB OK", style=SUCCESS) if db_ok
        else Text("○ DB não inicializado", style=WARNING)
    )
    vault_str = (
        Text("● Vault OK", style=SUCCESS) if vault_ok
        else Text("○ Vault não encontrado", style=DANGER)
    )

    table.add_row(
        "LLM", ollama_str,
        "DB", db_str,
    )
    table.add_row(
        "Vault", vault_str,
        "Dados", Text("mock", style=WARNING),
    )
    return table


def render_help_panel() -> Panel:
    """Painel de comandos disponíveis — estilo Claude Code."""
    table = Table(box=None, show_header=False, padding=(0, 2), expand=True)
    table.add_column(style=f"bold {ACCENT}", min_width=22)
    table.add_column(style=DIM)

    commands = [
        ("analyze <SYMBOL> <TF>", "Analisar setup de trading"),
        ("analyze EURUSD H1", "Exemplo com EURUSD"),
        ("train --file <FILE>", "Alimentar base de conhecimento"),
        ("knowledge search <query>", "Pesquisar na KB"),
        ("outcome --id <ID>", "Registar resultado de análise"),
        ("review weekly", "Revisão semanal assistida"),
        ("health", "Estado de todos os serviços"),
        ("init", "Inicializar vault + base de dados"),
        ("help", "Mostrar esta ajuda"),
        ("exit / quit", "Sair do Trade-CLI"),
    ]

    for cmd, desc in commands:
        table.add_row(f"  {cmd}", desc)

    return Panel(
        table,
        title=Text("  Comandos", style=f"bold {ACCENT}"),
        border_style=MUTED,
        padding=(0, 1),
    )


def render_main_screen() -> None:
    """Ecrã principal após o splash."""
    console.clear()

    # Header
    header_text = Text.assemble(
        ("  TRADE", f"bold {ACCENT}"),
        ("-", f"bold {MUTED}"),
        ("CLI  ", f"bold {ACCENT}"),
        (f"{VERSION}  ", f"dim {MUTED}"),
        ("EURUSD · USDJPY · USDCAD · US30 · NAS100", MUTED),
    )
    console.print(Panel(header_text, border_style=ACCENT, height=3))

    # Status bar
    console.print(render_status_bar())
    console.print(Rule(style=MUTED))

    # Help panel
    console.print(render_help_panel())
    console.print(Rule(style=MUTED))

    # Prompt hint
    console.print(
        Text.assemble(
            ("  Escreve um comando ou ", MUTED),
            ("help", f"bold {ACCENT}"),
            (" para começar. ", MUTED),
            ("Ctrl+C ou exit para sair.", DIM),
        )
    )
    console.print()


def _check_ollama() -> bool:
    """Check if Ollama server is reachable."""
    try:
        import httpx
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        r = httpx.get(f"{base}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _check_database() -> bool:
    """Check if database file exists."""
    return Path("database.db").exists()


def _check_vault() -> bool:
    """Check if Obsidian vault exists with proper structure."""
    vault = Path(os.getenv("OBSIDIAN_VAULT_PATH", "./Trade-CLI-Vault"))
    return vault.exists() and (vault / "00-meta").exists()


def print_analyzing(symbol: str, timeframe: str) -> None:
    """Indicador de análise em curso — animado."""
    with Live(
        Spinner("dots", text=Text(f"  Analisando {symbol} {timeframe}...", style=ACCENT)),
        console=console,
        refresh_per_second=10,
    ) as live:
        time.sleep(1.5)  # será substituído pelo tempo real de análise
    console.print(
        Text.assemble(
            ("  ✓ ", SUCCESS),
            (f"Análise {symbol} {timeframe} ", "white"),
            ("concluída", SUCCESS),
        )
    )


def print_verdict(verdict: str, reason: str) -> None:
    """Renderiza o veredito da análise com cor e estilo."""
    styles = {
        "allowed": (SUCCESS, "ALLOWED", "✓"),
        "watch_only": (WARNING, "WATCH ONLY", "◈"),
        "blocked": (DANGER, "BLOCKED", "✗"),
    }
    color, label, icon = styles.get(verdict.lower(), (MUTED, verdict.upper(), "?"))
    console.print(
        Panel(
            Text.assemble(
                (f"  {icon} {label}\n", f"bold {color}"),
                (f"  {reason}", MUTED),
            ),
            border_style=color,
            padding=(0, 1),
        )
    )


def print_engine_scores(scores: dict[str, float]) -> None:
    """Renderiza scores dos engines com barras de progresso visuais."""
    console.print(Rule("  Engine Scores", style=MUTED))
    for engine, score in scores.items():
        pct = int(score * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        color = SUCCESS if pct >= 70 else WARNING if pct >= 50 else DANGER
        console.print(
            Text.assemble(
                (f"  {engine:<20}", MUTED),
                (f" {bar} ", color),
                (f" {pct:3d}%", f"bold {color}"),
            )
        )
    console.print()


def start_repl() -> None:
    """REPL interactivo — o coração da interface."""
    render_main_screen()

    while True:
        try:
            # Prompt customizado — estilo Claude Code
            raw = console.input(
                Text.assemble(
                    ("  tradecli", f"bold {ACCENT}"),
                    (" > ", MUTED),
                ).plain
            ).strip()

            if not raw:
                continue

            if raw.lower() in ("exit", "quit", "q", "sair"):
                console.print(
                    Text.assemble(
                        ("\n  Até já. ", MUTED),
                        ("Bons trades.\n", f"bold {ACCENT}"),
                    )
                )
                break

            if raw.lower() == "help":
                console.print(render_help_panel())
                continue

            if raw.lower() == "clear":
                render_main_screen()
                continue

            # Passar o comando para o Typer CLI
            parts = raw.split()
            try:
                from click.testing import CliRunner
                from typer import main as typer_main

                # Import the app from cli.main
                from cli.main import app as cli_app

                # Convert Typer app to Click app for testing
                click_app = typer_main.get_command(cli_app)
                runner = CliRunner(mix_stderr=False)
                result = runner.invoke(click_app, parts, catch_exceptions=False)
                if result.output:
                    console.print(result.output, end="")
                if result.exit_code != 0 and result.exception:
                    console.print(
                        Text(f"  Erro: {result.exception}", style=DANGER)
                    )
            except SystemExit:
                pass
            except Exception as e:
                console.print(Text(f"  ✗ Erro: {e}", style=DANGER))

        except KeyboardInterrupt:
            console.print(
                Text.assemble(
                    ("\n\n  Interrompido. ", MUTED),
                    ("Usa exit para sair correctamente.\n", DIM),
                )
            )
        except EOFError:
            break


def main() -> None:
    """Entry point do launcher Trade-CLI."""
    # Se há argumentos, executar directamente (modo comando)
    if len(sys.argv) > 1:
        from cli.main import app
        app()
        return

    # Modo launcher interactivo
    render_splash()
    time.sleep(0.2)

    # Boot sequence animado
    with Live(console=console, refresh_per_second=8) as live:
        steps = [
            ("Carregando configuração", 0.3),
            ("Verificando base de dados", 0.3),
            ("Conectando ao vault Obsidian", 0.3),
            ("Verificando Ollama", 0.4),
            ("Iniciando engines analíticos", 0.3),
            ("Trade-CLI pronto", 0.2),
        ]
        for step, delay in steps:
            live.update(
                Spinner("dots", text=Text(f"  {step}...", style=ACCENT))
            )
            time.sleep(delay)

    start_repl()


if __name__ == "__main__":
    main()
