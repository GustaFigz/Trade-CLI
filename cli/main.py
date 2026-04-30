"""
Trade-CLI Command Line Interface

Main CLI entry point using Typer.

Phase 1: Core subcommands (init, analyze, db setup, show, health)
Date: 2025-04-30
"""

import typer
from pathlib import Path
import json
from datetime import datetime

from engines import ThesisEngine
from core.risk_guardian import RiskGuardian
from core.analysis_schema import AnalysisOutput, BiaType, AnalysisType
from db.migrations import create_database

app = typer.Typer(
    help="Trade-CLI: Local IA for Forex Trading Analysis (FTMO)",
    no_args_is_help=True,
)

# ============================================================================
# SUBCOMMAND: init
# ============================================================================

@app.command()
def init():
    """Initialize Trade-CLI (Obsidian + Database)"""
    
    print("Initializing Trade-CLI...")
    
    # Check Obsidian vault
    vault_path = Path("Trade-CLI-Vault")
    if vault_path.exists():
        print(f"✓ Obsidian vault exists at {vault_path}")
    else:
        print(f"✗ Obsidian vault not found at {vault_path}")
        raise typer.Exit(code=1)
    
    # Initialize database
    try:
        create_database("database.db")
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise typer.Exit(code=1)
    
    print("\n✓ Trade-CLI initialized successfully!")
    print("Next: trade-cli analyze NZDUSD M15 --test")


# ============================================================================
# SUBCOMMAND: analyze
# ============================================================================

@app.command()
def analyze(
    symbol: str = typer.Argument(..., help="Symbol (e.g., NZDUSD)"),
    timeframe: str = typer.Argument(..., help="Timeframe (e.g., M15)"),
    test: bool = typer.Option(False, "--test", help="Run with mock data"),
    notes: str = typer.Option("", "--notes", help="Analyst notes"),
):
    """Analyze a setup"""
    
    print(f"\n{'='*60}")
    print(f"Analyzing {symbol} {timeframe}")
    print(f"{'='*60}\n")
    
    # Create engines
    thesis_engine = ThesisEngine()
    risk_guardian = RiskGuardian()
    
    # Generate analysis
    analysis = thesis_engine.synthesize(
        symbol=symbol,
        timeframe=timeframe,
        analyst_notes=notes or "Phase 1 test analysis",
    )
    
    # Get RiskGuardian verdict
    verdict = risk_guardian.should_block(analysis)
    analysis.verdict = verdict.verdict
    analysis.veto_reason = verdict.reason
    
    # Display results
    print(f"Bias: {analysis.bias.value.upper()}")
    print(f"Setup: {analysis.setup_type}")
    print(f"Confidence: {analysis.confidence_score:.0%}")
    print(f"Alignment: {analysis.alignment_score:.0%}")
    print(f"\nMotor Scores:")
    print(f"  Technical: {analysis.technical_score:.0%}")
    print(f"  Price Action: {analysis.price_action_score:.0%}")
    print(f"  Fundamental: {analysis.fundamental_score:.0%}")
    print(f"\nVerdict: {verdict.verdict.value.upper()}")
    print(f"Reason: {verdict.reason}")
    print(f"\nInvalidations:")
    for inv in analysis.invalidations:
        print(f"  - {inv}")
    print(f"\nRisk Notes:")
    for note in analysis.risk_notes:
        print(f"  - {note}")
    
    print(f"\n{'='*60}")
    print("Full JSON Output:")
    print(f"{'='*60}")
    print(analysis.to_json())
    
    if test:
        print(f"\n✓ Test analysis complete (no save)")
    else:
        # In Phase 2: Save to Obsidian + SQLite
        print(f"\n[Phase 2] Would save to Obsidian + SQLite")


# ============================================================================
# SUBCOMMAND: db setup
# ============================================================================

@app.command()
def db_setup():
    """Setup database schema"""
    
    print("Setting up database...")
    try:
        create_database("database.db")
        print("✓ Database setup complete")
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        raise typer.Exit(code=1)


# ============================================================================
# SUBCOMMAND: show ftmo-rules
# ============================================================================

@app.command()
def show(
    resource: str = typer.Argument(..., help="Resource to show (e.g., ftmo-rules)"),
):
    """Show system information"""
    
    if resource == "ftmo-rules":
        print("\nFTMO Rules (Phase 1):")
        print("="*60)
        print("Daily Loss Limit: 5.0%")
        print("Total Loss Limit: 10.0%")
        print("Risk Per Trade: 0.5%-1.0%")
        print("News Blackout: ±15 minutes")
        print("Max Trades/Day: 8")
        print("Correlation Block: > 0.7")
        print("\nDetailed config: config/ftmo-rules.yaml")
    else:
        print(f"Unknown resource: {resource}")
        raise typer.Exit(code=1)


# ============================================================================
# SUBCOMMAND: health
# ============================================================================

@app.command()
def health():
    """Check system health"""
    
    print("Trade-CLI Health Check")
    print("="*60)
    
    checks = {
        "Obsidian Vault": Path("Trade-CLI-Vault").exists(),
        "Database": Path("database.db").exists(),
        "Config (ftmo-rules)": Path("config/ftmo-rules.yaml").exists(),
        "Engines": True,  # Always available
        "RiskGuardian": True,  # Always available
    }
    
    for check, status in checks.items():
        symbol = "✓" if status else "✗"
        print(f"{symbol} {check}")
    
    all_ok = all(checks.values())
    print(f"\n{'='*60}")
    print(f"Status: {'✓ OK' if all_ok else '✗ Issues Found'}")
    
    if not all_ok:
        print("\nRun: trade-cli init")
        raise typer.Exit(code=1)


# ============================================================================
# SUBCOMMAND: version
# ============================================================================

@app.command()
def version():
    """Show version"""
    print("Trade-CLI v1.0.0 (Phase 1)")
    print("Date: 2025-04-30")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app()
