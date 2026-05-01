"""
Trade-CLI Command Line Interface

Main CLI entry point using Typer + Rich.
Phase 2: Full orchestrator integration.

Note: Windows terminal emoji fix applied at startup.

Phase 2 Active (2.2)
Date: 2026-05-01
"""

import sys
import os

# Fix Windows terminal encoding for rich output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

import typer
from pathlib import Path
import json
import yaml
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from orchestrator.orchestrator import Orchestrator
from core.analysis_schema import AnalysisOutput, BiaType, AnalysisType, VerdictType
from db.migrations import create_database

app = typer.Typer(
    help="Trade-CLI v2.0.0 — Local AI for Forex Trading Analysis (FTMO)",
    no_args_is_help=True,
)
console = Console()


# ============================================================================
# SUBCOMMAND: init
# ============================================================================

@app.command()
def init():
    """Inicializar Trade-CLI (Obsidian + Database)"""
    
    console.print(Panel("[bold cyan]Initializing Trade-CLI...[/bold cyan]", border_style="cyan"))
    
    # Check Obsidian vault
    vault_path = Path("Trade-CLI-Vault")
    if vault_path.exists():
        console.print(f"[green]✓[/green] Obsidian vault at [bold]{vault_path}[/bold]")
    else:
        console.print(f"[red]✗[/red] Obsidian vault not found at [bold]{vault_path}[/bold]")
        raise typer.Exit(code=1)
    
    # Initialize database
    try:
        create_database("database.db")
        console.print("[green]✓[/green] Database initialized")
    except Exception as e:
        console.print(f"[red]✗[/red] Database initialization failed: {e}")
        raise typer.Exit(code=1)
    
    console.print("\n[bold green]✓ Trade-CLI initialized successfully![/bold green]")
    console.print("Next: [cyan]python main.py analyze EURUSD H1 --test[/cyan]")


# ============================================================================
# SUBCOMMAND: analyze
# ============================================================================

@app.command()
def analyze(
    symbol: str = typer.Argument(..., help="Par de trading (ex: EURUSD, USDJPY, US30)"),
    timeframe: str = typer.Argument(..., help="Timeframe (M5, M15, H1, H4, D1)"),
    notes: str = typer.Option("", "--notes", "-n", help="Notas do analista"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Desactivar LLM (mais rápido)"),
    no_rag: bool = typer.Option(False, "--no-rag", help="Desactivar RAG"),
    test: bool = typer.Option(False, "--test", help="Modo teste (usa mock data)"),
):
    """Analisar um activo com o sistema completo Fase 2."""
    
    console.print(Panel(
        f"[bold cyan]Analysing {symbol.upper()} {timeframe.upper()}[/bold cyan]",
        subtitle=f"[dim]LLM={'OFF' if no_llm else 'ON'} | RAG={'OFF' if no_rag else 'ON'} | {'TEST MODE' if test else 'LIVE MODE'}[/dim]",
        border_style="cyan"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Running analysis pipeline...", total=None)
        
        try:
            orch = Orchestrator(
                use_llm=not no_llm,
                use_rag=not no_rag,
                use_mt5=not test,
            )
            result = orch.analyze(symbol=symbol.upper(), timeframe=timeframe.upper(), user_query=notes)
        except Exception as e:
            console.print(f"[red]✗ Analysis failed: {e}[/red]")
            raise typer.Exit(code=1)
    
    if 'error' in result:
        console.print(f"[red]✗ {result['error']}[/red]")
        raise typer.Exit(code=1)
    
    # --- Display results ---
    analysis = result.get('analysis', {})
    verdict_str = result.get('verdict', 'unknown').upper()
    verdict_reason = result.get('verdict_reason', '')
    
    # Verdict color
    verdict_colors = {
        'ALLOWED': 'bold green',
        'WATCH_ONLY': 'bold yellow',
        'BLOCKED': 'bold red',
    }
    verdict_color = verdict_colors.get(verdict_str, 'white')
    
    # Bias indicator (ASCII-safe for Windows terminal)
    bias_indicators = {
        'bullish': '[+]',
        'bearish': '[-]',
        'neutral': '[~]',
        'fragile': '[!]',
    }
    bias_val = analysis.get('bias', 'neutral')
    bias_emoji = bias_indicators.get(bias_val, '[?]')
    
    # Main summary panel
    summary = Text()
    summary.append(f"\n  Bias:       ", style="dim")
    summary.append(f"{bias_emoji} {bias_val.upper()}", style="bold")
    summary.append(f"\n  Setup:      ", style="dim")
    summary.append(analysis.get('setup_type', 'N/A'), style="cyan")
    summary.append(f"\n  Confidence: ", style="dim")
    summary.append(f"{analysis.get('confidence_score', 0):.0%}", style="bold white")
    summary.append(f"\n  Alignment:  ", style="dim")
    summary.append(f"{analysis.get('alignment_score', 0):.0%}", style="bold white")
    summary.append(f"\n\n  Verdict:    ", style="dim")
    summary.append(f"  {verdict_str}  ", style=verdict_color)
    summary.append(f"\n  Reason:     ", style="dim")
    summary.append(verdict_reason, style="italic")
    
    console.print(Panel(summary, title="[bold]Analysis Result[/bold]", border_style=verdict_color.split()[-1]))
    
    # Engine scores table
    engine_table = Table(title="Engine Scores", box=box.ROUNDED, show_header=True)
    engine_table.add_column("Engine", style="cyan")
    engine_table.add_column("Score", justify="center")
    engine_table.add_column("Explanation", style="dim")
    
    for eng in result.get('engine_outputs', []):
        score = eng.get('score', 0)
        score_color = "green" if score >= 0.65 else ("yellow" if score >= 0.45 else "red")
        engine_table.add_row(
            eng.get('name', 'unknown').replace('_', ' ').title(),
            Text(f"{score:.0%}", style=f"bold {score_color}"),
            eng.get('explanation', '')[:60],
        )
    console.print(engine_table)
    
    # Invalidations
    if result.get('invalidations'):
        console.print("\n[bold yellow]⚠ Invalidations:[/bold yellow]")
        for inv in result['invalidations']:
            console.print(f"  • {inv}")
    
    # Risk notes
    if result.get('risk_notes'):
        console.print("\n[bold orange3]📋 Risk Notes:[/bold orange3]")
        for note in result['risk_notes']:
            console.print(f"  • {note}")
    
    # Data source
    data_src = result.get('data_source', 'mock')
    llm_used = result.get('llm_used', False)
    console.print(f"\n[dim]Data: {data_src} | LLM: {'✓' if llm_used else '✗'} | {result.get('timestamp', '')}[/dim]")
    
    if test:
        console.print("\n[dim italic]✓ Test mode — no data saved[/dim italic]")
    else:
        console.print("\n[dim italic][Phase 2.3] SQLite + Obsidian persistence coming soon[/dim italic]")


# ============================================================================
# SUBCOMMAND: health
# ============================================================================

@app.command()
def health():
    """Verificar estado de todos os componentes Fase 2."""
    
    console.print(Panel("[bold]Trade-CLI Health Check[/bold]", border_style="blue"))
    
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("Component", style="cyan", min_width=20)
    table.add_column("Status", justify="center", min_width=10)
    table.add_column("Details", style="dim")
    
    def ok(msg: str = "") -> tuple:
        return Text("✓ OK", style="bold green"), msg
    
    def warn(msg: str = "") -> tuple:
        return Text("⚠ WARN", style="bold yellow"), msg
    
    def err(msg: str = "") -> tuple:
        return Text("✗ FAIL", style="bold red"), msg
    
    # MT5
    try:
        from data.mt5_client import MT5Client
        client = MT5Client(fallback_to_mock=True)
        st, det = ok("mock mode") if not client.connected else ok("connected")
        table.add_row("MT5 Client", st, det)
    except Exception as e:
        table.add_row("MT5 Client", *err(str(e)))
    
    # Ollama LLM
    try:
        from orchestrator.llm_client import LocalLLMClient
        llm = LocalLLMClient()
        if llm.available:
            try:
                avail = llm.is_available()
                if avail:
                    table.add_row("LLM (Ollama)", *ok(f"model: {llm.model}"))
                else:
                    table.add_row("LLM (Ollama)", *warn(f"Ollama running but model {llm.model} not found"))
            except Exception:
                table.add_row("LLM (Ollama)", *warn("Ollama not running — run: ollama serve"))
        else:
            table.add_row("LLM (Ollama)", *warn("ollama package not installed"))
    except Exception as e:
        table.add_row("LLM (Ollama)", *err(str(e)))
    
    # RAG / Vault
    vault_path = Path("Trade-CLI-Vault")
    if vault_path.exists():
        md_count = len(list(vault_path.rglob("*.md")))
        table.add_row("RAG / Vault", *ok(f"{md_count} notes found"))
    else:
        table.add_row("RAG / Vault", *err("Vault not found — run: python main.py init"))
    
    # Risk Guardian
    try:
        from core.risk_guardian import RiskGuardian
        rg = RiskGuardian()
        table.add_row("Risk Guardian", *ok("FTMO rules loaded"))
    except Exception as e:
        table.add_row("Risk Guardian", *err(str(e)))
    
    # Database
    db_path = Path("database.db")
    if db_path.exists():
        table.add_row("Database", *ok(f"{db_path.stat().st_size // 1024} KB"))
    else:
        table.add_row("Database", *warn("Not initialized — run: python main.py db-setup"))
    
    # Config
    config_path = Path("config/ftmo-rules.yaml")
    if config_path.exists():
        table.add_row("FTMO Config", *ok("ftmo-rules.yaml loaded"))
    else:
        table.add_row("FTMO Config", *err("config/ftmo-rules.yaml not found"))
    
    # Assets config
    assets_path = Path("config/assets.yaml")
    if assets_path.exists():
        table.add_row("Assets Config", *ok("assets.yaml loaded"))
    else:
        table.add_row("Assets Config", *warn("config/assets.yaml not found"))
    
    console.print(table)


# ============================================================================
# SUBCOMMAND: version
# ============================================================================

@app.command()
def version():
    """Mostrar versão do Trade-CLI."""
    console.print(Panel(
        "[bold cyan]Trade-CLI v2.0.0 (Phase 2 Active)[/bold cyan]\n"
        "[dim]Date: 2026-05-01 | Agent: Antigravity[/dim]\n"
        "[dim]Local AI for Forex Trading Analysis — FTMO compliant[/dim]",
        border_style="cyan"
    ))


# ============================================================================
# SUBCOMMAND: db-setup
# ============================================================================

@app.command()
def db_setup():
    """Configurar esquema da base de dados."""
    
    console.print("Setting up database...")
    try:
        create_database("database.db")
        console.print("[green]✓[/green] Database setup complete")
    except Exception as e:
        console.print(f"[red]✗[/red] Database setup failed: {e}")
        raise typer.Exit(code=1)


# ============================================================================
# SUBCOMMAND: show
# ============================================================================

@app.command()
def show(
    resource: str = typer.Argument(..., help="Resource to show (e.g., ftmo-rules)"),
):
    """Mostrar informação do sistema."""
    
    if resource == "ftmo-rules":
        try:
            with open("config/ftmo-rules.yaml", 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            table = Table(title="FTMO Rules", box=box.ROUNDED)
            table.add_column("Rule", style="cyan")
            table.add_column("Value", justify="right")
            
            dd = rules.get('drawdown_limits', {})
            table.add_row("Daily Loss Limit", f"{dd.get('daily_max_loss_percent', 5.0)}%")
            table.add_row("Total Loss Limit", f"{dd.get('total_max_loss_percent', 10.0)}%")
            
            rpt = rules.get('risk_per_trade', {})
            table.add_row("Risk Per Trade (min)", f"{rpt.get('min_risk_percent', 0.5)}%")
            table.add_row("Risk Per Trade (max)", f"{rpt.get('max_risk_percent', 1.0)}%")
            
            sess = rules.get('session_rules', {})
            news = sess.get('news_blackout', {})
            table.add_row("News Blackout", f"±{news.get('minutes_before', 15)} min")
            table.add_row("Max Trades/Day", str(sess.get('max_trades_per_day', 8)))
            
            console.print(table)
            console.print(f"\n[dim]Detailed config: config/ftmo-rules.yaml[/dim]")
        except Exception as e:
            console.print(f"[yellow]Using default rules (YAML error: {e})[/yellow]")
    else:
        console.print(f"[red]Unknown resource: {resource}[/red]")
        raise typer.Exit(code=1)


# ============================================================================
# SUBCOMMAND: train
# ============================================================================

@app.command()
def train(
    file: str = typer.Argument(..., help="Caminho para o ficheiro (PDF, MD, TXT, DOCX)"),
    topic: str = typer.Option("", "--topic", "-t", help="Tópico principal (ex: ict, smc, wyckoff)"),
    symbol: str = typer.Option("", "--symbol", "-s", help="Símbolo associado (ex: EURUSD)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simula sem escrever"),
):
    """Ingerir material de estudo para a base de conhecimento."""
    
    from training.ingest import ingest_document
    from training.chunker import chunk_text
    from training.tagger import auto_tag
    
    file_path = Path(file)
    if not file_path.exists():
        console.print(f"[red]✗ File not found: {file}[/red]")
        raise typer.Exit(code=1)
    
    console.print(Panel(
        f"[bold]Training: {file_path.name}[/bold]",
        subtitle=f"[dim]topic={topic or 'auto'} | symbol={symbol or 'auto'} | dry_run={dry_run}[/dim]",
        border_style="cyan"
    ))
    
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console, transient=True) as progress:
        
        # Step 1: Ingest
        progress.add_task("Reading document...")
        text = ingest_document(file)
        if not text:
            console.print(f"[red]✗ Failed to read: {file}[/red]")
            raise typer.Exit(code=1)
        console.print(f"[green]✓[/green] Ingested: {len(text):,} chars")
        
        # Step 2: Chunk
        progress.add_task("Chunking text...")
        chunks = chunk_text(text, chunk_size=512)
        console.print(f"[green]✓[/green] Created {len(chunks)} chunks")
        
        # Step 3: Tag
        progress.add_task("Auto-tagging...")
        all_tags: dict = {}
        for chunk in chunks:
            tags = auto_tag(chunk)
            for k, v in tags.items():
                if k not in all_tags:
                    all_tags[k] = set()
                if isinstance(v, list):
                    all_tags[k].update(v)
        console.print(f"[green]✓[/green] Tags: {dict(all_tags)}")
    
    if dry_run:
        console.print("\n[yellow]DRY RUN — nothing written to database[/yellow]")
    else:
        from training.kb_writer import batch_write_knowledge
        progress.add_task("Writing to knowledge base...")
        
        # Prepare chunks format
        chunks_data = []
        for text_chunk in chunks:
            chunk_data = {
                'text': text_chunk,
                'metadata': {
                    'category': 'educational',
                    'symbols': [symbol] if symbol else [],
                    'methods': [topic] if topic else [],
                    'tags': list(all_tags.keys()),
                    'confidence': 0.8
                },
                'source_file': str(file_path.name)
            }
            chunks_data.append(chunk_data)
            
        counts = batch_write_knowledge(chunks_data)
        console.print(f"\n[green]✓[/green] Persisted {counts['db_written']} chunks to SQLite and {counts['obsidian_written']} to Obsidian")
    
    console.print(f"\n[bold green]✓ Training pipeline complete[/bold green]")


# ============================================================================
# SUBCOMMAND: knowledge
# ============================================================================

@app.command()
def knowledge(
    action: str = typer.Argument("list", help="list | search | stats"),
    query: str = typer.Option("", "--query", "-q", help="Termo de pesquisa"),
    symbol: str = typer.Option("", "--symbol", "-s", help="Filtrar por símbolo"),
):
    """Gerir e consultar a base de conhecimento."""
    
    import sqlite3
    
    db_path = Path("database.db")
    if not db_path.exists():
        console.print("[yellow]Database not found. Run: python main.py db-setup[/yellow]")
        raise typer.Exit(code=1)
    
    if action == "list":
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM knowledge_base")
            count = cursor.fetchone()[0]
            conn.close()
            console.print(f"[cyan]Knowledge base:[/cyan] {count} entries")
        except Exception as e:
            console.print(f"[yellow]knowledge_base table not found yet: {e}[/yellow]")
    
    elif action == "stats":
        console.print("[dim]Knowledge base stats — coming in Phase 2.3[/dim]")
    
    elif action == "search":
        if not query:
            console.print("[red]--query required for search action[/red]")
            raise typer.Exit(code=1)
        console.print(f"[dim]Semantic search for '{query}' — coming in Phase 2.3[/dim]")
    
    else:
        console.print(f"[red]Unknown action: {action}. Use: list | search | stats[/red]")
        raise typer.Exit(code=1)


# ============================================================================
# SUBCOMMAND: outcome
# ============================================================================

@app.command()
def outcome(
    trade_id: str = typer.Argument(..., help="ID do trade (ex: T20260501-001)"),
    result: float = typer.Argument(..., help="Resultado em pips/pontos (negativo = perda)"),
    notes: str = typer.Option("", "--notes", "-n", help="Notas pós-trade"),
):
    """Registar o resultado de um trade para post-mortem."""
    
    console.print(Panel(
        f"[bold]Recording Outcome: {trade_id}[/bold]\n"
        f"Result: [{'green' if result >= 0 else 'red'}]{'+' if result >= 0 else ''}{result:.1f} pips[/{'green' if result >= 0 else 'red'}]",
        border_style="green" if result >= 0 else "red"
    ))
    
    # Phase 2.3: Write to SQLite + Obsidian post-mortem
    console.print(f"[dim italic]Outcome '{trade_id}' logged (SQLite persistence in Phase 2.3)[/dim italic]")
    if notes:
        console.print(f"[dim]Notes: {notes}[/dim]")


# ============================================================================
# SUBCOMMAND: review
# ============================================================================

@app.command()
def review(
    period: str = typer.Argument("week", help="week | month | custom"),
    output: str = typer.Option("", "--output", "-o", help="Guardar relatório em ficheiro"),
):
    """Gerar revisão de performance semanal ou mensal."""
    
    console.print(Panel(
        f"[bold cyan]Performance Review — {period.upper()}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Phase 2.3: Read from SQLite and generate report
    table = Table(title="Review Summary (Placeholder)", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Period", period)
    table.add_row("Total Analyses", "0 (no data yet)")
    table.add_row("Allowed", "0")
    table.add_row("Blocked", "0")
    table.add_row("Watch Only", "0")
    
    console.print(table)
    
    if output:
        console.print(f"[dim]Report save to file: {output} — coming in Phase 2.3[/dim]")
    
    console.print("[dim italic]Full review system in Phase 2.3 (SQLite reads)[/dim italic]")


# ============================================================================
# SUBCOMMAND: assets
# ============================================================================

@app.command()
def assets():
    """Listar ativos configurados e respectivos parâmetros."""
    
    assets_path = Path("config/assets.yaml")
    if not assets_path.exists():
        console.print("[red]✗ config/assets.yaml not found[/red]")
        raise typer.Exit(code=1)
    
    with open(assets_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    table = Table(title="Configured Assets", box=box.ROUNDED, show_header=True)
    table.add_column("Symbol", style="bold cyan", min_width=10)
    table.add_column("Type", style="dim")
    table.add_column("Sessions", style="dim")
    table.add_column("Spread", justify="right")
    
    # Forex
    forex = config.get('assets', {}).get('forex_primary', {})
    for sym, data in forex.items():
        sessions = ", ".join(data.get('sessions', []))
        spread = data.get('typical_spread_pips', 'N/A')
        table.add_row(sym, "Forex Major", sessions, f"{spread} pips")
    
    # Indices
    indices = config.get('assets', {}).get('indices_primary', {})
    for sym, data in indices.items():
        sessions = ", ".join(data.get('sessions', []))
        spread = data.get('typical_spread_pips', 'N/A')
        table.add_row(sym, "Index", sessions, f"{spread} pts")
    
    console.print(table)
    
    # Primary timeframe
    tf_config = config.get('timeframes', {})
    primary_tf = tf_config.get('primary_analysis', 'H1')
    console.print(f"\n[dim]Primary timeframe: [bold]{primary_tf}[/bold] | Config: config/assets.yaml[/dim]")


# ============================================================================
# SUBCOMMAND: tui
# ============================================================================

@app.command()
def tui():
    """Iniciar interface TUI (Dashboard Interactivo)."""
    try:
        from cli.tui.app import TradeCLIApp
        app_tui = TradeCLIApp()
        app_tui.run()
    except ImportError as e:
        console.print(f"[red]Error loading TUI: {e}[/red]")
        console.print("[dim]Make sure textual is installed: pip install textual[/dim]")
        raise typer.Exit(code=1)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app()
