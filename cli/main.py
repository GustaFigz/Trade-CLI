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
import sqlite3
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
    from cli.launcher import print_verdict, print_engine_scores

    analysis = result.get('analysis', {})
    verdict_str = result.get('verdict', 'unknown')
    verdict_reason = result.get('verdict_reason', '')
    
    # Verdict color
    verdict_colors = {
        'ALLOWED': 'bold green',
        'WATCH_ONLY': 'bold yellow',
        'BLOCKED': 'bold red',
    }
    verdict_color = verdict_colors.get(verdict_str.upper(), 'white')
    
    # Main summary panel
    result_table = Table(box=box.SIMPLE_HEAD, show_header=False, expand=True)
    result_table.add_column(style="dim", min_width=18)
    result_table.add_column(style="bold white")

    result_table.add_row("Símbolo", f"{symbol.upper()}")
    result_table.add_row("Timeframe", f"{timeframe.upper()}")
    result_table.add_row("Bias", f"{analysis.get('bias', 'neutral').upper()}")
    result_table.add_row("Setup", f"{analysis.get('setup_type', 'N/A')}")
    result_table.add_row("Confiança", f"{analysis.get('confidence_score', 0):.0%}")
    result_table.add_row("Alinhamento", f"{analysis.get('alignment_score', 0):.0%}")

    console.print(Panel(result_table, title="  Análise", border_style="cyan"))

    # Engine scores with visual bars
    engine_scores = {}
    for eng in result.get('engine_outputs', []):
        name = eng.get('name', 'unknown').replace('_', ' ').title()
        engine_scores[name] = eng.get('score', 0)
    if engine_scores:
        print_engine_scores(engine_scores)
    
    # Verdict with styled panel
    print_verdict(verdict_str, verdict_reason)
    
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
        # Persist analysis to SQLite
        analysis_id = _persist_analysis(result, symbol.upper(), timeframe.upper())
        
        # Create vault note
        vault_note = _create_vault_note(result, analysis_id)
        
        # Show persistence feedback
        if analysis_id:
            msg = f"💾 Guardado — ID #{analysis_id}"
            if vault_note:
                msg += f" | 📝 [[teses/{vault_note.stem}]]"
            console.print(f"\n[green]{msg}[/green]")
        else:
            console.print("\n[yellow]⚠ Análise concluída mas persistência falhou[/yellow]")


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
        from orchestrator.llm_client import LLMClient
        llm = LLMClient()
        if llm.is_ollama_available():
            table.add_row("LLM (Ollama)", *ok(f"model: {llm.ollama_model}"))
        elif llm.fallback_base:
            table.add_row("LLM (Ollama)", *warn(f"Ollama offline — fallback: {llm.fallback_base}"))
        else:
            table.add_row("LLM (Ollama)", *warn("Ollama not running — run: ollama serve"))
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
    analysis_id: str = typer.Argument(..., help="ID do trade (ex: 2026-05-01-EURUSD-H1)"),
    result: float = typer.Argument(..., help="Resultado em pips/pontos (negativo = perda)"),
    price_moved: int = typer.Option(0, "--price-moved", "-p", help="Pips de movimento real"),
    execution: str = typer.Option("acceptable", "--execution", "-e", help="ideal | acceptable | poor | not_traded"),
    invalidated: bool = typer.Option(False, "--invalidated", help="Se a setup foi invalidada"),
    invalidation_type: str = typer.Option("", "--invalidation-type", help="Qual invalidação ocorreu"),
    notes: str = typer.Option("", "--notes", "-n", help="Notas pós-trade (reflexão)"),
):
    """Registar o resultado de um trade para post-mortem e aprendizado."""
    
    from datetime import datetime
    import json
    
    try:
        db_path = Path("database.db")
        if not db_path.exists():
            console.print("[red]✗ Database not found. Run 'python main.py init' first.[/red]")
            raise typer.Exit(code=1)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verify analysis exists
        cursor.execute("SELECT symbol, timeframe, bias FROM analyses WHERE id = ?", (analysis_id,))
        analysis_row = cursor.fetchone()
        
        if not analysis_row:
            console.print(f"[red]✗ Analysis not found: {analysis_id}[/red]")
            raise typer.Exit(code=1)
        
        symbol, timeframe, bias = analysis_row
        
        # Generate outcome ID
        outcome_id = f"outcome-{analysis_id}-{datetime.now().isoformat()[:10]}"
        
        # Insert outcome record
        cursor.execute("""
            INSERT INTO analysis_outcomes
            (id, analysis_id, outcome_timestamp, outcome_source, price_moved_pips,
             profit_loss_pips, invalidated, invalidation_type, execution_quality,
             post_mortem_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            outcome_id,
            analysis_id,
            datetime.now().isoformat(),
            "manual",
            price_moved,
            int(result),
            invalidated,
            invalidation_type if invalidated else None,
            execution,
            notes or None,
        ))
        
        conn.commit()
        conn.close()
        
        # Display result
        result_color = "green" if result >= 0 else "red"
        console.print(Panel(
            f"[bold]Outcome Recorded: {analysis_id}[/bold]\n"
            f"[{result_color}]{'+' if result >= 0 else ''}{result:.0f} pips[/{result_color}] | "
            f"Execution: {execution} | "
            f"Invalidated: {'✓' if invalidated else '✗'}",
            border_style=result_color
        ))
        
        # Create post-mortem note in vault
        vault_dir = Path("Trade-CLI-Vault/revisoes")
        vault_dir.mkdir(parents=True, exist_ok=True)
        
        outcome_note = vault_dir / f"{analysis_id}-outcome.md"
        outcome_note.write_text(f"""---
type: revisao
analysis_id: {analysis_id}
symbol: {symbol}
timeframe: {timeframe}
outcome_date: {datetime.now().isoformat()[:10]}
tags: [outcome, post-mortem, {bias}]
---

# Post-Mortem — {analysis_id}

## Resultado

- **Pips**: {'+' if result >= 0 else ''}{result:.0f} pips
- **Execução**: {execution}
- **Invalidado**: {'Sim' if invalidated else 'Não'}
{f'- **Tipo de Invalidação**: {invalidation_type}' if invalidated else ''}
- **Preço Movido**: {price_moved} pips

## Reflexão

{notes if notes else '(Sem notas adicionadas)'}

## Ligações

Ver análise original: [[teses/{analysis_id}]]

---
*Gerado em {datetime.now().isoformat()[:19]}*
""")
        
        console.print(f"[green]✓ Post-mortem saved: [[revisoes/{outcome_note.stem}]][/green]")
    
    except Exception as e:
        console.print(f"[red]✗ Failed to record outcome: {e}[/red]")
        raise typer.Exit(code=1)


# ============================================================================
# SUBCOMMAND: review
# ============================================================================

@app.command()
def review(
    period: str = typer.Argument("week", help="week | month | all"),
    symbol: str = typer.Option("", "--symbol", "-s", help="Filtrar por símbolo"),
    output: str = typer.Option("", "--output", "-o", help="Guardar relatório em ficheiro"),
):
    """Gerar revisão de performance semanal, mensal ou histórica."""
    
    from datetime import datetime, timedelta
    
    try:
        db_path = Path("database.db")
        if not db_path.exists():
            console.print("[red]✗ Database not found. Run 'python main.py init' first.[/red]")
            raise typer.Exit(code=1)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Calculate date filter
        now = datetime.now()
        if period == "week":
            start_date = (now - timedelta(days=7)).isoformat()
            title = "Weekly Review"
        elif period == "month":
            start_date = (now - timedelta(days=30)).isoformat()
            title = "Monthly Review"
        else:  # all
            start_date = "1970-01-01"
            title = "All-Time Review"
        
        # Build query
        query = """
            SELECT 
                a.symbol,
                COUNT(*) as total_analyses,
                SUM(CASE WHEN a.verdict = 'allowed' THEN 1 ELSE 0 END) as allowed_count,
                SUM(CASE WHEN a.verdict = 'watch_only' THEN 1 ELSE 0 END) as watch_count,
                SUM(CASE WHEN a.verdict = 'blocked' THEN 1 ELSE 0 END) as blocked_count,
                AVG(a.confidence_score) as avg_confidence,
                SUM(CASE WHEN ao.profit_loss_pips > 0 THEN 1 ELSE 0 END) as profitable_outcomes,
                COUNT(ao.id) as total_outcomes,
                AVG(ao.profit_loss_pips) as avg_pips
            FROM analyses a
            LEFT JOIN analysis_outcomes ao ON a.id = ao.analysis_id
            WHERE a.timestamp > ?
        """
        params = [start_date]
        
        if symbol:
            query += " AND a.symbol = ?"
            params.append(symbol.upper())
        
        query += " GROUP BY a.symbol ORDER BY total_analyses DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        # Display results
        console.print(Panel(
            f"[bold cyan]{title}[/bold cyan]\n"
            f"[dim]Period: {start_date[:10]} to {now.isoformat()[:10]}[/dim]"
            f"{f' | Symbol: {symbol.upper()}' if symbol else ''}",
            border_style="cyan"
        ))
        
        if not rows:
            console.print("[yellow]No analyses found for this period.[/yellow]")
            return
        
        table = Table(title="Performance Summary", box=box.ROUNDED, show_header=True)
        table.add_column("Symbol", style="bold cyan")
        table.add_column("Total", justify="right", style="dim")
        table.add_column("Allowed", justify="right")
        table.add_column("Watch", justify="right", style="yellow")
        table.add_column("Blocked", justify="right", style="red")
        table.add_column("Avg Conf", justify="right", style="green")
        table.add_column("Outcomes", justify="right", style="magenta")
        table.add_column("Win %", justify="right")
        table.add_column("Avg Pips", justify="right")
        
        for row in rows:
            sym, total, allowed, watch, blocked, avg_conf, profitable, outcomes, avg_pips = row
            
            win_pct = ""
            if outcomes and outcomes > 0:
                win_pct = f"{(profitable / outcomes * 100):.0f}%"
            
            avg_pips_str = f"{avg_pips:+.0f}" if avg_pips else "—"
            
            table.add_row(
                sym,
                str(total),
                str(allowed or 0),
                str(watch or 0),
                str(blocked or 0),
                f"{avg_conf:.2f}" if avg_conf else "—",
                f"{outcomes or 0}",
                win_pct,
                avg_pips_str
            )
        
        console.print(table)
        
        # Summary stats
        total_analyses = sum(row[1] for row in rows)
        total_allowed = sum(row[2] or 0 for row in rows)
        total_outcomes = sum(row[7] or 0 for row in rows)
        total_pips = sum((row[8] or 0) * (row[7] or 0) for row in rows)
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total Analyses: {total_analyses}")
        console.print(f"  Allowed: {total_allowed} ({total_allowed/total_analyses*100:.0f}%)" if total_analyses else "  Allowed: 0")
        if total_outcomes > 0:
            console.print(f"  Tracked Outcomes: {total_outcomes}")
            console.print(f"  Total Pips: {total_pips:+.0f}")
            console.print(f"  Avg per Outcome: {total_pips/total_outcomes:+.0f}")
        
        # Save to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"Period: {start_date[:10]} to {now.isoformat()[:10]}\n")
                if symbol:
                    f.write(f"Symbol: {symbol.upper()}\n")
                f.write(f"\n## Statistics\n\n")
                f.write(f"- Total Analyses: {total_analyses}\n")
                f.write(f"- Allowed: {total_allowed}\n")
                f.write(f"- Blocked: {sum(row[4] or 0 for row in rows)}\n")
                if total_outcomes > 0:
                    f.write(f"- Total Outcomes: {total_outcomes}\n")
                    f.write(f"- Total Pips: {total_pips:+.0f}\n")
            console.print(f"[green]✓ Report saved to {output}[/green]")
    
    except Exception as e:
        console.print(f"[red]✗ Failed to generate review: {e}[/red]")
        raise typer.Exit(code=1)


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
# HELPER FUNCTIONS — Persistence Layer
# ============================================================================

def _persist_analysis(result: dict, symbol: str, timeframe: str) -> Optional[str]:
    """
    Persist analysis result to SQLite analyses table.
    Returns analysis ID (text) or None if failed.
    """
    try:
        db_path = Path("database.db")
        if not db_path.exists():
            create_database(str(db_path))
        
        conn = sqlite3.connect(str(db_path))
        analysis = result.get('analysis', {})
        
        # Generate ID: timestamp-symbol-timeframe
        ts = result.get('timestamp', datetime.now().isoformat())[:10]  # YYYY-MM-DD
        analysis_id = f"{ts}-{symbol}-{timeframe}"
        
        cursor = conn.execute("""
            INSERT INTO analyses 
            (id, symbol, timeframe, bias, confidence_score, alignment_score,
             verdict, technical_score, price_action_score, fundamental_score,
             invalidations, risk_notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            symbol,
            timeframe,
            analysis.get('bias', 'neutral'),
            analysis.get('confidence_score', 0.0),
            analysis.get('alignment_score', 0.0),
            result.get('verdict', 'blocked'),
            analysis.get('technical_score', 0.0),
            analysis.get('price_action_score', 0.0),
            analysis.get('fundamental_score', 0.0),
            json.dumps(result.get('invalidations', [])),
            json.dumps(result.get('risk_notes', [])),
            result.get('timestamp', datetime.now().isoformat()),
        ))
        
        conn.commit()
        conn.close()
        return analysis_id
    
    except Exception as e:
        console.print(f"[yellow]⚠ Failed to persist analysis to SQLite: {e}[/yellow]")
        return None


def _create_vault_note(result: dict, analysis_id: Optional[int]) -> Optional[Path]:
    """
    Create markdown note in Trade-CLI-Vault/teses/ directory.
    Returns Path to created note or None if failed.
    """
    try:
        vault_path = Path("Trade-CLI-Vault")
        teses_dir = vault_path / "teses"
        teses_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate note filename: YYYY-MM-DD-SYMBOL-TF.md
        ts = result.get('timestamp', datetime.now().isoformat())[:10]
        symbol = result.get('symbol', 'UNKNOWN')
        tf = result.get('timeframe', 'UNKNOWN')
        note_name = f"{ts}-{symbol}-{tf}.md"
        note_path = teses_dir / note_name
        
        analysis = result.get('analysis', {})
        bias = analysis.get('bias', 'neutral').upper()
        verdict = result.get('verdict', 'blocked')
        confidence = analysis.get('confidence_score', 0.0)
        
        # Build engine scores table
        engine_scores_rows = ""
        for eng in result.get('engine_outputs', []):
            name = eng.get('name', 'unknown').replace('_', ' ').title()
            score = eng.get('score', 0.0)
            bar_filled = int(score * 10)
            bar_empty = 10 - bar_filled
            bar = "▓" * bar_filled + "░" * bar_empty
            engine_scores_rows += f"| {name} | {bar} {score:.0%} |\n"
        
        # Build invalidations
        invalidations_text = ""
        for inv in result.get('invalidations', []):
            invalidations_text += f"- {inv}\n"
        if not invalidations_text:
            invalidations_text = "None\n"
        
        # Build risk notes
        risk_text = ""
        for note in result.get('risk_notes', []):
            risk_text += f"- {note}\n"
        if not risk_text:
            risk_text = "None\n"
        
        # Frontmatter & content
        content = f"""---
type: tese
symbol: {symbol}
timeframe: {tf}
created: {ts}
bias: {bias.lower()}
verdict: {verdict}
confidence: {confidence:.2f}
tags: [{bias.lower()}, {tf.lower()}, {analysis.get('setup_type', 'unknown').replace(' ', '-').lower()}]
analysis_id: {analysis_id or 'N/A'}
---

# {symbol} {tf} — {bias} ({ts})

## Veredicto: {verdict.upper()}

{result.get('verdict_reason', '(sem razão fornecida)')}

## Engines

| Engine | Score |
|--------|-------|
{engine_scores_rows}

## Invalidações

{invalidations_text}

## Risk Notes

{risk_text}

## Links

Ver [[ativos/{symbol}]] com setup [[conceitos/confluence]] e [[metodos/smart-money-concepts]]

***
*Gerado por Trade-CLI Antigravity | {result.get('timestamp', '')}*
"""
        
        note_path.write_text(content, encoding='utf-8')
        return note_path
    
    except Exception as e:
        console.print(f"[yellow]⚠ Failed to create vault note: {e}[/yellow]")
        return None


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
