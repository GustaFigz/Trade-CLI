"""
Trade-CLI Launcher — Interface profissional do terminal.
Modo primário: chat interactivo com especialista em Forex.
Modo secundário: comandos directos (tradecli analyze EURUSD H1).

Design inspirado em Claude Code e OpenCode.
Cores semânticas, animações Rich, REPL persistente.

Fase: 2.3
Data: 2026-05-01
"""
from __future__ import annotations

from collections.abc import Iterable
import os
import sys
import time
from pathlib import Path

import structlog
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich.rule import Rule
from rich.spinner import Spinner
from rich import box
from rich.markdown import Markdown

log = structlog.get_logger(__name__)
console = Console(highlight=False)

# ─── Paleta de cores ───────────────────────────────────────────────────────────
C_ACCENT  = "red"
C_DIM     = "dim white"
C_OK      = "bright_green"
C_WARN    = "bright_yellow"
C_ERR     = "bright_red"
C_MUTED   = "grey54"
C_BRAND   = "bold red"

# ─── Logo ASCII ────────────────────────────────────────────────────────────────
LOGO = """\
 ████████╗██████╗  █████╗ ██████╗ ███████╗ ██████╗██╗     ██╗
    ██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██║     ██║
    ██║   ██████╔╝███████║██║  ██║█████╗  ██║     ██║     ██║
    ██║   ██╔══██╗██╔══██║██║  ██║██╔══╝  ██║     ██║     ██║
    ██║   ██║  ██║██║  ██║██████╔╝███████╗╚██████╗███████╗██║
    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝╚══════╝╚═╝"""

VERSION = os.getenv("TRADECLI_VERSION", "0.2.0")
TAGLINE = "Local AI Specialist · Forex Trading · 100% Offline"


# ─── Helpers de estado ─────────────────────────────────────────────────────────

def _check_ollama() -> tuple[bool, str]:
    try:
        import httpx
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
        r = httpx.get(f"{base}/api/tags", timeout=2.0)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            if any(model.split(":")[0] in m for m in models):
                return True, f"Ollama · {model}"
            return False, f"Ollama up mas {model} não instalado"
        return False, "Ollama sem resposta"
    except Exception:
        return False, "Ollama offline"


def _check_db() -> tuple[bool, str]:
    db = Path(os.getenv("DB_PATH", "database.db"))
    return db.exists(), "SQLite OK" if db.exists() else "Não inicializado (run: init)"


def _check_vault() -> tuple[bool, str]:
    vault = Path(os.getenv("OBSIDIAN_VAULT_PATH", "./Trade-CLI-Vault"))
    ok = vault.exists() and (vault / "00-meta").exists()
    return ok, "Vault OK" if ok else "Vault não encontrado"


def _check_mock() -> tuple[bool, str]:
    mock = os.getenv("MOCK_DATA", "true").lower() == "true"
    return True, "Mock (dados simulados)" if mock else "MT5 (dados reais)"


# ─── Render functions ──────────────────────────────────────────────────────────

def render_splash() -> None:
    """Animação de entrada linha a linha — estilo Claude Code."""
    console.clear()
    lines = LOGO.split("\n")
    built = Text()

    for line in lines:
        built.append(line + "\n", style=C_BRAND)
        console.clear()
        console.print(
            Panel(
                Align.center(built),
                border_style=C_ACCENT,
                padding=(0, 2),
            )
        )
        time.sleep(0.06)

    # Tagline e versão
    time.sleep(0.1)
    console.clear()
    full = Text.assemble(
        (LOGO + "\n", C_BRAND),
        (f"\n  {TAGLINE}\n", f"italic {C_MUTED}"),
        (f"  v{VERSION}", f"dim {C_ACCENT}"),
    )
    console.print(Panel(Align.center(full), border_style=C_ACCENT, padding=(1, 2)))
    time.sleep(0.25)


def render_status_panel() -> Table:
    """Tabela de estado dos serviços."""
    t = Table(box=None, show_header=False, padding=(0, 2), expand=False)
    t.add_column(style=C_MUTED, no_wrap=True, min_width=8)
    t.add_column(no_wrap=True)

    checks = [
        ("LLM",   _check_ollama()),
        ("DB",    _check_db()),
        ("Vault", _check_vault()),
        ("Dados", _check_mock()),
    ]
    for label, (ok, msg) in checks:
        status = Text.assemble(
            ("● " if ok else "○ ", C_OK if ok else C_WARN),
            (msg, "white" if ok else C_WARN),
        )
        t.add_row(label, status)
    return t


def render_help() -> Table:
    """Tabela de comandos disponíveis."""
    t = Table(box=None, show_header=False, padding=(0, 2), expand=True)
    t.add_column(style=f"bold {C_ACCENT}", min_width=32, no_wrap=True)
    t.add_column(style=C_DIM)

    cmds = [
        # Chat
        ("  [chat] qualquer pergunta",      "Pergunta directamente ao especialista"),
        ("  O que achas do EURUSD agora?",  "Exemplo de chat com contexto"),
        ("",                                 ""),
        # Análise
        ("  analyze <SYMBOL> <TF>",          "Análise completa com engines + LLM"),
        ("  analyze EURUSD H1",              "Exemplo com EURUSD"),
        ("  analyze USDJPY M15 --fast",      "Análise rápida sem síntese LLM"),
        ("",                                 ""),
        # Conhecimento
        ("  train --file <ficheiro>",        "Ensinar um PDF/MD ao sistema"),
        ("  train --text \"...\"",           "Ensinar texto directamente"),
        ("  knowledge search <query>",       "Pesquisar na base de conhecimento"),
        ("",                                 ""),
        # Gestão
        ("  outcome --id <ID> --result ...", "Registar resultado de uma análise"),
        ("  review weekly",                  "Revisão semanal assistida por IA"),
        ("  history",                        "Últimas 10 análises"),
        ("",                                 ""),
        # Sistema
        ("  health",                         "Estado detalhado de todos os serviços"),
        ("  models",                         "Modelos Ollama disponíveis"),
        ("  init",                           "Inicializar vault + base de dados"),
        ("  clear",                          "Limpar ecrã"),
        ("  exit / quit",                    "Sair"),
    ]
    for cmd, desc in cmds:
        t.add_row(cmd, desc)
    return t


def render_main_screen() -> None:
    """Ecrã principal completo."""
    console.clear()

    # Header compacto
    header = Text.assemble(
        ("  TRADE", C_BRAND),
        ("-", f"bold {C_MUTED}"),
        ("CLI  ", C_BRAND),
        (f"v{VERSION}  ", f"dim {C_MUTED}"),
        ("EURUSD · USDJPY · USDCAD · US30 · NAS100", C_MUTED),
    )
    console.print(Panel(header, border_style=C_ACCENT, height=3))

    # Status
    console.print(render_status_panel())
    console.print(Rule(style=C_MUTED))

    # Help
    console.print(render_help())
    console.print(Rule(style=C_MUTED))

    # Dica inicial
    console.print(
        Text.assemble(
            ("  Escreve uma pergunta, um comando, ou ", C_MUTED),
            ("help", f"bold {C_ACCENT}"),
            (" para começar.  ", C_MUTED),
            ("Ctrl+C para sair.", C_DIM),
        )
    )
    console.print()


# ─── Output helpers ────────────────────────────────────────────────────────────

def print_thinking(message: str = "A pensar...") -> Live:
    """Spinner durante processamento — retorna o Live para controlo externo."""
    return Live(
        Spinner("dots2", text=Text(f"  {message}", style=C_ACCENT)),
        console=console,
        refresh_per_second=12,
        transient=True,
    )


def print_assistant_response(content: str, model: str = "", ms: float = 0) -> None:
    """Renderiza resposta do especialista com Markdown."""
    footer = ""
    if model:
        footer = f"  {model}"
    if ms:
        footer += f"  ·  {ms:.0f}ms"

    console.print(
        Panel(
            Markdown(content),
            title=Text("  Especialista", style=f"bold {C_ACCENT}"),
            subtitle=Text(footer, style=C_DIM) if footer else None,
            border_style=C_ACCENT,
            padding=(0, 2),
        )
    )


def print_verdict(verdict: str, reason: str, symbol: str = "") -> None:
    """Painel de veredito colorido."""
    styles = {
        "allowed":    (C_OK,   "ALLOWED",    "✓"),
        "watch_only": (C_WARN, "WATCH ONLY", "◈"),
        "blocked":    (C_ERR,  "BLOCKED",    "✗"),
    }
    color, label, icon = styles.get(verdict.lower(), (C_MUTED, verdict.upper(), "?"))
    title = f"  {icon} {label}" + (f"  ·  {symbol}" if symbol else "")
    console.print(
        Panel(
            Text(f"  {reason}", style=C_MUTED),
            title=Text(title, style=f"bold {color}"),
            border_style=color,
            padding=(0, 1),
        )
    )


def print_engine_scores(scores: dict[str, float]) -> None:
    """Barras de progresso para scores dos engines."""
    console.print(Rule("  Engine Scores", style=C_MUTED))
    for engine, score in scores.items():
        pct = int(score * 100)
        filled = int(pct / 5)
        bar = "█" * filled + "░" * (20 - filled)
        color = C_OK if pct >= 70 else C_WARN if pct >= 50 else C_ERR
        console.print(
            Text.assemble(
                (f"  {engine:<22}", C_MUTED),
                (bar, color),
                (f"  {pct:3d}%", f"bold {color}"),
            )
        )
    console.print()


def print_error(msg: str) -> None:
    console.print(Text.assemble(("  ✗  ", C_ERR), (msg, "white")))


def print_success(msg: str) -> None:
    console.print(Text.assemble(("  ✓  ", C_OK), (msg, "white")))


def print_info(msg: str) -> None:
    console.print(Text.assemble(("  ·  ", C_ACCENT), (msg, C_MUTED)))


def print_analyzing(symbol: str, timeframe: str) -> None:
    """Indicador de análise em curso — animado."""
    with Live(
        Spinner("dots", text=Text(f"  Analisando {symbol} {timeframe}...", style=C_ACCENT)),
        console=console,
        refresh_per_second=10,
    ) as live:
        time.sleep(1.5)  # será substituído pelo tempo real de análise
    print_success(f"Análise {symbol} {timeframe} concluída")


def _print_streaming_response(token_iter: Iterable[str], model: str = "") -> None:
    """Imprime resposta em streaming com Rich Live."""
    full = ""
    console.print()
    with Live(
        Spinner("dots2", text=Text("  a processar...", style=C_ACCENT)),
        console=console,
        refresh_per_second=20,
        transient=False,
    ) as live:
        for chunk in token_iter:
            full += chunk
            live.update(
                Panel(
                    Markdown(full),
                    title=Text("  Especialista", style=f"bold {C_ACCENT}"),
                    subtitle=Text(f"  {model}", style=C_DIM) if model else None,
                    border_style=C_ACCENT,
                    padding=(0, 2),
                )
            )
    if not full:
        print_error("Sem resposta do modelo.")


# ─── Boot sequence ─────────────────────────────────────────────────────────────

def boot_sequence() -> None:
    """Sequência de boot animada após o splash."""
    steps = [
        ("Carregando configuração",         0.2),
        ("Conectando à base de dados",      0.25),
        ("Verificando vault Obsidian",      0.2),
        ("Verificando Ollama",              0.35),
        ("Inicializando engines",           0.2),
        ("Sistema pronto",                  0.1),
    ]
    with Live(console=console, refresh_per_second=10, transient=True) as live:
        for step, delay in steps:
            live.update(Spinner("dots", text=Text(f"  {step}...", style=C_ACCENT)))
            time.sleep(delay)


# ─── REPL principal ────────────────────────────────────────────────────────────

def start_repl() -> None:
    """
    REPL interactivo com prompt_toolkit.
    Histórico persistente, autosuggest e respostas em streaming.
    """
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.formatted_text import ANSI
    from prompt_toolkit.history import FileHistory
    from orchestrator.chat_engine import ChatEngine

    repl_history_file = Path.home() / ".tradecli" / "repl_history"
    repl_history_file.parent.mkdir(parents=True, exist_ok=True)
    session = PromptSession(
        history=FileHistory(str(repl_history_file)),
        auto_suggest=AutoSuggestFromHistory(),
    )

    chat_engine = ChatEngine()
    render_main_screen()

    # Comandos que vão directamente para o Typer CLI
    CLI_COMMANDS = {
        "analyze", "train", "knowledge", "outcome",
        "review", "history", "health", "init", "db-setup",
        "show", "version", "models", "assets", "tui", "config",
    }

    while True:
        try:
            raw = session.prompt(
                ANSI("\033[31m  tradecli\033[0m\033[2m › \033[0m")
            ).strip()

            if not raw:
                continue

            cmd = raw.lower().split()[0] if raw.split() else ""

            # Sair
            if cmd in ("exit", "quit", "q", "sair", "bye"):
                console.print(
                    Text.assemble(("\n  Até já. ", C_MUTED), ("Bons trades.\n", C_BRAND))
                )
                break

            # Limpar
            if cmd == "clear":
                render_main_screen()
                continue

            # Help
            if cmd == "help":
                console.print(render_help())
                continue

            # Comandos CLI directos (Typer)
            if cmd in CLI_COMMANDS:
                _run_cli_command(raw.split())
                continue

            # Tudo o resto → chat com o especialista
            _print_streaming_response(
                chat_engine.stream(raw),
                model=chat_engine.model_name,
            )

        except KeyboardInterrupt:
            console.print(
                Text.assemble(
                    ("\n\n  Ctrl+C detectado. ", C_MUTED),
                    ("Escreve exit para sair correctamente.\n", C_DIM),
                )
            )
        except EOFError:
            break
        except Exception as e:
            print_error(f"Erro inesperado: {e}")
            log.error("repl_error", error=str(e))


def _run_cli_command(parts: list[str]) -> None:
    """Executa sub-comando Typer directamente sem CliRunner."""
    import sys as _sys
    from cli.main import app
    from typer.main import get_command

    old_argv = _sys.argv
    _sys.argv = ["tradecli", *parts]
    try:
        click_app = get_command(app)
        click_app.main(args=parts, prog_name="tradecli", standalone_mode=False)
    except SystemExit:
        pass
    except Exception as e:
        print_error(f"Erro no comando '{' '.join(parts)}': {e}")
        log.error("cli_command_error", cmd=parts, error=str(e))
    finally:
        _sys.argv = old_argv


# ─── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """
    Entry point do Trade-CLI.
    Com argumentos → executa comando directamente.
    Sem argumentos → launcher interactivo com splash.
    """
    if len(sys.argv) > 1:
        # Modo comando directo: tradecli analyze EURUSD H1
        from cli.main import app
        app()
        return

    # Modo interactivo
    render_splash()
    boot_sequence()
    start_repl()


if __name__ == "__main__":
    main()
