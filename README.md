# Trade-CLI: Local AI System for Forex Trading Analysis (FTMO)

**Trade-CLI** is a terminal-based analytical copilot for forex trading decisions with strict FTMO prop firm compliance. It combines multiple analytical engines (technical, price action, fundamental) with deterministic risk guardianship to suggest high-conviction setups.

**Key Philosophy:** AI supports decision-making; it never executes trades or bypasses risk rules.

## Quick Start

### Installation

```bash
# Clone or navigate to project directory
cd Trade-CLI

# Install dependencies
pip install -r requirements.txt

# Initialize system (creates Obsidian vault + SQLite database)
python main.py init
```

### First Analysis

```bash
# Run a test analysis on NZDUSD M15 timeframe
python main.py analyze NZDUSD M15 --test

# Expected output:
# - Bias (bullish/bearish/neutral/fragile)
# - Setup type (liquidity_sweep_reclaim, etc.)
# - Confidence score (0-100%)
# - Alignment between engines (0-100%)
# - Motor scores (Technical, Price Action, Fundamental)
# - Verdict (ALLOWED, WATCH_ONLY, or BLOCKED)
# - Reason & invalidation conditions
```

### Check System Health

```bash
python main.py health
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `python main.py --help` | Show all commands |
| `python main.py version` | Show version info |
| `python main.py init` | Initialize Obsidian vault + database |
| `python main.py health` | System status check |
| `python main.py analyze SYMBOL TF --test` | Analyze a setup (test mode) |
| `python main.py show ftmo-rules` | Display FTMO rule thresholds |
| `python main.py db-setup` | Recreate database schema |

## Project Structure

```
Trade-CLI/
├── Trade-CLI-Vault/              # Obsidian vault (curated knowledge)
│   ├── 00-meta/                  # System metadata & templates
│   ├── ativos/                   # Asset hubs (NZDUSD, etc.)
│   ├── teses/                    # Individual analyses (theses)
│   ├── post-mortems/             # Thesis vs reality comparisons
│   ├── playbooks/                # Reusable trading patterns
│   ├── sessions/                 # Daily macro context
│   └── prop-firm/                # FTMO rules & compliance
│
├── core/
│   ├── analysis_schema.py        # Core dataclasses (AnalysisOutput, EngineOutput)
│   ├── risk_guardian.py          # Deterministic FTMO rule enforcement
│   └── scoring.py                # Score calculation logic
│
├── engines/
│   ├── technical.py              # Technical analysis engine
│   ├── price_action.py           # Price action patterns
│   ├── fundamental.py            # Macro/fundamental context
│   └── __init__.py               # ThesisEngine (synthesizer)
│
├── db/
│   ├── db_schema.sql             # SQLite schema definition
│   ├── migrations.py             # Database initialization
│   └── models.py                 # ORM-like classes
│
├── cli/
│   └── main.py                   # Terminal interface (Typer)
│
├── config/
│   └── ftmo-rules.yaml           # FTMO rule thresholds (frozen for Phase 1)
│
├── docs/
│   ├── obsidian-structure.md     # Vault taxonomy & workflows
│   ├── decisions-phase1.md       # Architectural decisions (frozen)
│   ├── phase1-architecture.md    # System design & data flows
│   └── risk-guardian-guide.md    # FTMO rule logic explained
│
├── tests/
│   └── test_core.py              # Unit tests (15 test methods)
│
├── database.db                   # SQLite database (created on init)
├── requirements.txt              # Python dependencies
├── main.py                       # Entry point
└── README.md                     # This file
```

## Understanding the Analysis Output

When you run `analyze NZDUSD M15 --test`, you get:

```
============================================================
Analyzing NZDUSD M15
============================================================
Bias: NEUTRAL
Setup: liquidity_sweep_reclaim
Confidence: 63%
Alignment: 99%

Motor Scores:
  Technical: 70%
  Price Action: 55%
  Fundamental: 65%

Verdict: ALLOWED
Reason: All checks passed, good confluence

Invalidations:
  - M15 close below 0.5850
  - Macro event in 20 minutes

Risk Notes:
  - Spread elevated (2.1 pips)
  - USD intermarket mixed
```

**What Each Field Means:**
- **Bias:** The directional lean (bullish/bearish/neutral/fragile)
- **Setup:** Pattern type (e.g., liquidity sweep followed by retracement & reclaim)
- **Confidence:** How strong is this analysis (0-100%)?
- **Alignment:** Agreement between all analytical engines (0-100%)
- **Motor Scores:** Individual scores from Technical, Price Action, Fundamental engines
- **Verdict:** ALLOWED (high conviction), WATCH_ONLY (low conviction), or BLOCKED (FTMO rule violation)
- **Invalidations:** Specific price levels or events that would invalidate this thesis
- **Risk Notes:** Context concerns (volatility, news, correlations, etc.)

## Architectural Principles (Fase 1)

### 1. **Deterministic Risk Guardian**
- RiskGuardian applies FTMO rules before any suggestion
- Checks: drawdown limits, risk per trade, news blackout, correlation, trade count, quality
- **No negotiation:** If rule is violated → verdict is BLOCKED

### 2. **Dual Memory System**
- **Obsidian Vault:** Curated, readable trading knowledge (teses, playbooks, post-mortems)
- **SQLite Database:** Structured event history for learning & auditability

### 3. **Multi-Engine Analysis**
- **Technical Engine:** Trends, support/resistance, regime
- **Price Action Engine:** Candle patterns, compression, rejection
- **Fundamental Engine:** Macro context, interest rates, events
- **Thesis Engine:** Synthesizes all engines, resolves conflicts

### 4. **Consensus via Alignment**
- All engines contribute equally
- Alignment score = how tightly they agree (0-100%)
- Low alignment = watch_only (regardless of individual scores)

### 5. **Frozen Architectural Decisions (Phase 1)**
See `docs/decisions-phase1.md` for 5 locked decisions that define Phase 1 scope.

## FTMO Compliance Rules (Hardcoded Phase 1)

Trade-CLI blocks analyses that violate FTMO prop firm rules:

| Rule | Threshold | Action |
|------|-----------|--------|
| Daily Drawdown | 5% max loss in one day | Block all trades if hit |
| Total Drawdown | 10% max loss over period | Challenge failed if hit |
| Risk Per Trade | 0.5%-1.0% of balance | Block if outside range |
| News Blackout | ±15 min around high-impact news | Block during blackout |
| Max Trades/Day | 8 max | Block after 8th |
| Min Confluence | 50% alignment between engines | Watch-only if below |

These thresholds are loaded from `config/ftmo-rules.yaml` at startup.

## Database Schema

Trade-CLI stores analyses in SQLite for auditability & learning:

**Main Tables:**
- `analyses` — Individual analysis records (symbol, timeframe, confidence, verdict, etc.)
- `analysis_outcomes` — Actual price action results (validated later)
- `engine_outputs` — Individual engine scores & evidence
- `vetoed_ideas` — Rejected analyses with reasons
- `knowledge_base` — Playbooks, patterns, trading rules

Query examples:
```sql
-- Find all allowed analyses on NZDUSD
SELECT * FROM analyses WHERE symbol = 'NZDUSD' AND verdict = 'allowed';

-- Track veto accuracy over time
SELECT veto_reason, COUNT(*) as count 
FROM vetoed_ideas 
GROUP BY veto_reason;
```

## Testing

Run all unit tests:
```bash
python -m pytest tests/test_core.py -v
```

Expected result: **All 15 tests pass** ✓

Tests cover:
- Dataclass creation & validation
- JSON serialization/deserialization
- RiskGuardian blocking logic
- Engine synthesis
- Full end-to-end pipeline

## Obsidian Vault Guide

The vault is organized into 7 main sections:

1. **00-meta/** — System metadata, templates, decisions
2. **ativos/** — Per-asset hubs (NZDUSD.md, etc.)
3. **teses/** — Individual analyses with detailed setup/bias/invalidation
4. **post-mortems/** — Thesis vs reality comparisons (learning)
5. **playbooks/** — Reusable trading patterns & edge cases
6. **sessions/** — Daily macro context & session planning
7. **prop-firm/** — FTMO rules, compliance notes, verdicts

**Key Workflow:**
1. Create a thesis in `teses/` using the template
2. Run analysis via CLI
3. If verdict = ALLOWED, execute and track outcome
4. Post-result: create post-mortem in `post-mortems/` (compare thesis vs reality)
5. Extract pattern into `playbooks/` if replicable

**Search Queries (built into Obsidian):**
```
tag:#bullish tag:#liquidity-sweep  # Find bullish liquidity sweeps
path:playbooks                      # Show all playbooks
tag:#blocked                        # Analyses that were blocked
```

## Configuration

### Environment Variables (Phase 2+)
Create `.env` file for future integrations:
```
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
TRADINGVIEW_API_KEY=your_api_key
GEMMA_MODEL_PATH=/path/to/gemma-model
```

### FTMO Rules
Edit `config/ftmo-rules.yaml` to customize thresholds. Changes take effect on next `analyze` command.

## Known Limitations (Phase 1)

- **No live data:** All analyses use mock data (Phase 2 adds MT5/TradingView)
- **No LLM orchestration:** Engines use deterministic logic (Phase 2 adds Gemma)
- **Single pair focus:** NZDUSD emphasized; other pairs not yet configured
- **No visual analysis:** Terminal-only output (Phase 2 may add TradingView integration)
- **No portfolio correlation:** Intermarket relationships not yet modeled
- **No Wyckoff/ICT/SMC:** Advanced methods in Phase 2+

## Roadmap

**Fase 2:** Data integration (MT5), Gemma orchestrator, playbook automation
**Fase 3:** TradingView webhooks, intermarket analysis, visual backtesting
**Fase 4:** Advanced pattern recognition, AI-driven optimization

## Troubleshooting

### "ModuleNotFoundError: No module named 'core'"
```bash
cd Trade-CLI
python main.py analyze NZDUSD M15 --test
```
Ensure you're in the project root directory.

### "Database initialization failed"
```bash
rm database.db  # Remove old database
python main.py init
```

### "YAML parse error in ftmo-rules.yaml"
Ensure config file is valid YAML. Run:
```bash
python main.py show ftmo-rules  # Shows loaded rules
```

### Obsidian vault not opening
```bash
ls Trade-CLI-Vault/  # Verify directory exists
```
Open `Trade-CLI-Vault/` as a vault in Obsidian app (not a folder).

## Contributing to Fase 1 Scope

Fase 1 is **frozen**—changes require documented decisions. See `docs/decisions-phase1.md` before proposing modifications.

To propose Fase 2 features, create an issue with:
- Feature description
- Why it's needed
- How it aligns with architecture

## Support

For questions or issues:
1. Check `docs/phase1-architecture.md` for system design details
2. Review `docs/decisions-phase1.md` for frozen decisions
3. Run `python main.py health` to check system status
4. Examine `tests/test_core.py` for usage examples

---

**Version:** Fase 1 Foundation (2025-04-30)  
**Status:** ✓ Production-ready for analytical use (no live trading)  
**Next:** Fase 2 (Data Plane + Gemma Orchestrator)
