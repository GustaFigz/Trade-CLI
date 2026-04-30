# Fase 1 Architecture: Trade-CLI System Design

## Overview

Trade-CLI Phase 1 is a **deterministic, local AI system** for forex trading analysis with strict FTMO compliance. It combines multiple analytical engines with a veto layer that prevents rule violations before any suggestion reaches the user.

**Core Principle:** AI supports decision-making, never circumvents risk rules.

---

## 1. System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        TRADE-CLI SYSTEM                          │
└──────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   USER TERMINAL     │
                    │  (CLI / Typer)      │
                    └──────────┬──────────┘
                               │
                    analyze NZDUSD M15 --test
                               │
                ┌──────────────▼──────────────┐
                │    ANALYSIS PIPELINE       │
                │  (cli/main.py analyze)     │
                └──────────────┬──────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐
    │  TECHNICAL  │    │ PRICE ACTION│    │ FUNDAMENTAL  │
    │  ENGINE     │    │  ENGINE     │    │  ENGINE      │
    │             │    │             │    │              │
    │ Trends      │    │ Candles     │    │ Macro        │
    │ Support/Res │    │ Compression │    │ Interest     │
    │ Regime      │    │ Rejection   │    │ Inflation    │
    │             │    │ Structure   │    │ Events       │
    │ score: 0.7  │    │ score: 0.55 │    │ score: 0.65  │
    └──────┬──────┘    └──────┬──────┘    └───────┬──────┘
           │                  │                   │
           └──────────────────┼───────────────────┘
                              │
                   ┌──────────▼──────────┐
                   │   THESIS ENGINE     │
                   │  (Synthesizer)      │
                   │                     │
                   │ • Avg scores        │
                   │ • Alignment check   │
                   │ • Bias heuristic    │
                   │                     │
                   │ AnalysisOutput:     │
                   │  confidence: 0.633  │
                   │  alignment: 0.992   │
                   │  bias: neutral      │
                   └──────────┬──────────┘
                              │
                   ┌──────────▼──────────────┐
                   │  RISK GUARDIAN         │
                   │ (Deterministic Veto)   │
                   │                        │
                   │ 1. Drawdown check      │
                   │ 2. Risk per trade      │
                   │ 3. News blackout       │
                   │ 4. Correlation block   │
                   │ 5. Trade count        │
                   │ 6. Quality filters     │
                   │                        │
                   │ ProposalVerdictOutput: │
                   │  verdict: ALLOWED      │
                   │  reason: "Good conf"   │
                   └──────────┬─────────────┘
                              │
                   ┌──────────▼──────────────┐
                   │   OUTPUT LAYER         │
                   │                        │
                   │ • Terminal display     │
                   │ • JSON output          │
                   │ • Save to Obsidian     │
                   │ • Save to SQLite       │
                   └────────────────────────┘

                   ┌──────────────────────┐
                   │  PERSISTENCE         │
                   │                      │
                   │ Trade-CLI-Vault/    │
                   │ (Obsidian - notes)  │
                   │                      │
                   │ database.db          │
                   │ (SQLite - events)    │
                   └──────────────────────┘
```

---

## 2. Data Flow: Analysis → Verdict

```
INPUT
  │
  ├─ Symbol: "NZDUSD"
  ├─ Timeframe: "M15"
  ├─ Market data: [mocked in Phase 1]
  └─ Config: ftmo-rules.yaml
  │
  ▼

MOTORS (Parallel Execution)
  │
  ├─ Technical Engine
  │   ├─ Reads: price, volume, regime
  │   ├─ Analyzes: trend, S/R, momentum
  │   └─ Returns: EngineOutput(score=0.70, explanation="...", evidence={...})
  │
  ├─ Price Action Engine
  │   ├─ Reads: candle patterns, compression, structure
  │   ├─ Analyzes: setup quality, rejection confirmation
  │   └─ Returns: EngineOutput(score=0.55, explanation="...", evidence={...})
  │
  └─ Fundamental Engine
      ├─ Reads: macro calendar, interest rates, inflation
      ├─ Analyzes: bias alignment, event risk
      └─ Returns: EngineOutput(score=0.65, explanation="...", evidence={...})

  ▼

THESIS ENGINE (Synthesizer)
  │
  ├─ Combine motors:
  │   ├─ Avg confidence = (0.70 + 0.55 + 0.65) / 3 = 0.633
  │   ├─ Variance = 0.0055 → alignment = 1 - variance = 0.992
  │   └─ Bias = "neutral" (avg < 0.65 but > 0.35)
  │
  ├─ Create AnalysisOutput:
  │   ├─ id: UUID
  │   ├─ symbol: "NZDUSD"
  │   ├─ timeframe: "M15"
  │   ├─ confidence_score: 0.633
  │   ├─ alignment_score: 0.992
  │   ├─ bias: "neutral"
  │   ├─ setup_type: "liquidity_sweep_reclaim"
  │   ├─ technical_score: 0.70
  │   ├─ price_action_score: 0.55
  │   ├─ fundamental_score: 0.65
  │   ├─ invalidations: ["M15 close below 0.5850", "macro event in 20m"]
  │   ├─ risk_notes: ["Spread elevated", "USD mixed"]
  │   └─ created_at: timestamp
  │
  └─ Return AnalysisOutput

  ▼

RISK GUARDIAN (Deterministic Veto)
  │
  ├─ Check 1: Drawdown Limit
  │   ├─ Input: current_daily_loss_pct=2.3%, max=5%
  │   ├─ Decision: ✓ PASS (2.3% < 5%)
  │
  ├─ Check 2: Risk Per Trade
  │   ├─ Input: risk_percent=0.8%, min=0.5%, max=1.0%
  │   ├─ Decision: ✓ PASS (0.8% in range)
  │
  ├─ Check 3: News Blackout
  │   ├─ Input: minutes_to_next_news=25, blackout_window=±15
  │   ├─ Decision: ✓ PASS (25 > 15, outside blackout)
  │
  ├─ Check 4: Correlation Block
  │   ├─ Input: pairs_in_portfolio=[], max_corr=0.7
  │   ├─ Decision: ✓ PASS (no correlated pairs)
  │
  ├─ Check 5: Trade Count
  │   ├─ Input: trades_today=3, max_per_day=8
  │   ├─ Decision: ✓ PASS (3 < 8)
  │
  ├─ Check 6: Quality Filters
  │   ├─ Alignment: 0.992 > 0.50 ✓ PASS
  │   ├─ Confidence: 0.633 > 0.55 ✓ PASS
  │   ├─ Decision: ✓ PASS (all filters satisfied)
  │
  └─ Final Verdict:
      ├─ All checks passed → verdict = "ALLOWED"
      ├─ reason = "All checks passed, good confluence"
      └─ Create ProposalVerdictOutput

  ▼

OUTPUT & PERSISTENCE
  │
  ├─ Console Output:
  │   ├─ Bias: NEUTRAL
  │   ├─ Setup: liquidity_sweep_reclaim
  │   ├─ Confidence: 63%
  │   ├─ Alignment: 99%
  │   ├─ Verdict: ALLOWED
  │   └─ Reason: All checks passed, good confluence
  │
  ├─ JSON Output (full AnalysisOutput)
  │
  ├─ Save to Obsidian Vault:
  │   └─ teses/2025-04-30-NZDUSD-M15-test.md
  │
  └─ Save to SQLite:
      └─ analyses table (structured for auditability)
```

---

## 3. Component Interaction Chart

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRADE-CLI COMPONENTS                        │
└─────────────────────────────────────────────────────────────────┘

CLI LAYER (cli/main.py)
├─ analyze(symbol, timeframe)
│   ├─ Instantiates engines
│   ├─ Calls ThesisEngine.synthesize()
│   ├─ Instantiates RiskGuardian
│   ├─ Calls RiskGuardian.should_block()
│   ├─ Formats and displays output
│   └─ Saves to DB/Obsidian
├─ init()
│   ├─ Checks Obsidian vault
│   └─ Calls db.migrations.create_database()
├─ health()
│   ├─ Checks files/folders
│   ├─ Checks database connection
│   └─ Validates config
└─ show() / db-setup() / version()

CORE LOGIC LAYER (core/)
├─ analysis_schema.py
│   ├─ BiaType: bullish, bearish, neutral, fragile
│   ├─ VerdictType: allowed, watch_only, blocked
│   ├─ AnalysisOutput: central dataclass
│   ├─ EngineOutput: individual engine result
│   ├─ ProposalVerdictOutput: final verdict
│   └─ JSON serialization methods
├─ risk_guardian.py
│   ├─ RiskGuardian class
│   ├─ _load_rules(): loads ftmo-rules.yaml
│   ├─ should_block(): returns ALLOWED/WATCH_ONLY/BLOCKED
│   ├─ _check_drawdown()
│   ├─ _check_risk_per_trade()
│   ├─ _check_news_blackout()
│   ├─ _check_correlation()
│   ├─ _check_trade_count()
│   ├─ _check_quality_filters()
│   └─ decision tree logic
└─ scoring.py
    ├─ calculate_alignment()
    ├─ determine_bias()
    └─ aggregate_confidence()

ENGINES LAYER (engines/)
├─ __init__.py
│   ├─ TechnicalEngine
│   │   ├─ analyze(symbol, timeframe)
│   │   ├─ Returns: EngineOutput(score=0.70)
│   │   └─ Evidence: {trend, support, resistance, regime}
│   ├─ PriceActionEngine
│   │   ├─ analyze(symbol, timeframe)
│   │   ├─ Returns: EngineOutput(score=0.55)
│   │   └─ Evidence: {pattern, compression, rejection}
│   ├─ FundamentalEngine
│   │   ├─ analyze(symbol, timeframe)
│   │   ├─ Returns: EngineOutput(score=0.65)
│   │   └─ Evidence: {macro_bias, event_risk, rates}
│   └─ ThesisEngine
│       ├─ synthesize(engines_outputs)
│       ├─ Returns: AnalysisOutput
│       └─ Logic: average, alignment, bias heuristic

DATABASE LAYER (db/)
├─ db_schema.sql
│   ├─ analyses table (central)
│   ├─ analysis_outcomes table
│   ├─ engine_outputs table
│   ├─ vetoed_ideas table
│   ├─ knowledge_base table
│   ├─ 4 views (verdict_accuracy, veto_accuracy)
│   └─ 15 indexes for performance
├─ migrations.py
│   ├─ create_database()
│   ├─ Reads schema from db_schema.sql
│   └─ Handles encoding issues
└─ models.py (ORM placeholders for Phase 2)

CONFIG LAYER (config/)
├─ ftmo-rules.yaml
│   ├─ drawdown_limits (daily 5%, total 10%)
│   ├─ risk_per_trade (0.5%-1.0%)
│   ├─ session_rules (news blackout, trade count)
│   ├─ quality_filters (min confidence, alignment)
│   └─ Loaded by RiskGuardian at startup
└─ settings.py (Phase 2)

PERSISTENCE LAYER
├─ Obsidian Vault (Trade-CLI-Vault/)
│   ├─ 00-meta/ (system metadata)
│   ├─ ativos/ (asset hubs)
│   ├─ teses/ (individual analyses)
│   ├─ post-mortems/ (thesis vs reality)
│   ├─ playbooks/ (reusable patterns)
│   ├─ sessions/ (daily context)
│   └─ prop-firm/ (FTMO rules)
└─ SQLite Database (database.db)
    ├─ Structured event history
    ├─ Auditability trail
    └─ Learning data for Phase 2+
```

---

## 4. RiskGuardian Decision Tree

```
PROPOSAL ARRIVES
       │
       ▼
┌─────────────────────────────────────┐
│ RiskGuardian.should_block()         │
│                                     │
│ Deterministic veto layer            │
│ (No fuzzy logic, all checks pass)   │
└────────────────────┬────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────┐           ┌─────────────────┐
   │ CHECK 1 │           │   [Sequential]  │
   │         │           │                 │
   │Drawdown │ ──NO──→   │ If ANY check    │
   │         │           │ fails:          │
   │ 5% ?    │           │                 │
   │         │   ┌────▼──────────────┐    │
   │ YES ────┤   │ BLOCKED verdict   │    │
   │         │   │ reason: "rule name"     │
   │         │   └───────────────────┘    │
   └────┬────┘                            │
        │                                 │
        ▼                                 │
   ┌─────────┐                           │
   │ CHECK 2 │                           │
   │         │                           │
   │ Risk %  │ ──NO──→ BLOCKED           │
   │         │           ▲               │
   │0.5-1%? │           │               │
   │         │   ┌───────┴────────────┐  │
   │ YES ────┤   │ Veto set           │  │
   │         │   │ reason saved       │  │
   │         │   │ in DB             │  │
   │         │   └───────────────────┘  │
   └────┬────┘                          │
        │                               │
        ▼                               │
   ┌─────────┐                         │
   │ CHECK 3 │                         │
   │         │                         │
   │ News    │ ──NO──→ BLOCKED         │
   │Blackout │           ▲             │
   │         │           │             │
   │ ±15min? │   ┌───────┴─────────┐   │
   │         │   │ High-impact news│   │
   │ YES ────┤   │ incoming (veto) │   │
   │         │   └───────────────┘   │
   │         │                       │
   └────┬────┘                       │
        │                           │
        ▼                           │
   ┌─────────┐                     │
   │ CHECK 4 │                     │
   │         │                     │
   │Correlation│ ──NO──→ BLOCKED   │
   │         │           ▲         │
   │ <0.7 ?  │           │         │
   │         │   ┌───────┴──────┐  │
   │ YES ────┤   │ Pair too     │  │
   │         │   │ correlated   │  │
   │         │   └───────────────┘ │
   │         │                     │
   └────┬────┘                     │
        │                         │
        ▼                         │
   ┌─────────┐                   │
   │ CHECK 5 │                   │
   │         │                   │
   │Trade    │ ──NO──→ BLOCKED   │
   │Count    │           ▲       │
   │         │           │       │
   │ <8/day? │   ┌───────┴────┐  │
   │         │   │ Daily limit│  │
   │ YES ────┤   │ reached    │  │
   │         │   └────────────┘  │
   │         │                   │
   └────┬────┘                   │
        │                       │
        ▼                       │
   ┌─────────┐                 │
   │ CHECK 6 │                 │
   │         │                 │
   │Quality  │                 │
   │Filters  │ ──NO──→ BLOCKED │
   │         │           ▲     │
   │ •Conf   │           │     │
   │  >55%?  │   ┌───────┴──┐  │
   │ •Align  │   │ Low      │  │
   │  >50%?  │   │ consensus│  │
   │         │   │ (veto)   │  │
   │ ALL YES─┤   └────────┘   │
   │         │               │
   └────┬────┘               │
        │                   │
        ▼                   │
   ┌──────────────────────┐ │
   │ ALL CHECKS PASSED    │ │
   │                      │ │
   │ verdict = ALLOWED    │ │
   │ reason = "All checks │ │
   │  passed, good conf"  │ │
   │                      │ │
   └────────┬─────────────┘ │
            │               │
            │ ┌─────────────┴──────────────┐
            │ │                            │
            ▼ ▼                            ▼
        ┌──────────┐          ┌────────────────────┐
        │ ALLOWED  │          │  WATCH_ONLY        │
        │          │          │  (Low confidence)  │
        │ Execute? │          │  (Low alignment)   │
        │ Ready    │          │  (Quality filter)  │
        │ for user │          │                    │
        │ decision │          │  Monitor, don't    │
        │          │          │  execute           │
        └──────────┘          └────────────────────┘
```

---

## 5. Verdict Types and Meanings

| Verdict | Triggered By | What It Means | Action |
|---------|--------------|--------------|--------|
| **ALLOWED** | All 6 checks pass | High-conviction setup, ready for execution | User can execute; no FTMO rule violation |
| **WATCH_ONLY** | Low confidence (<55%) OR low alignment (<50%) OR quality filters fail | Setup exists but not high-conviction enough | Monitor price action; don't execute; gather more context |
| **BLOCKED** | Any FTMO rule violation | FTMO prop firm rule would be violated | Never execute; system prevents trades |

**Key:** BLOCKED is **deterministic and non-negotiable**. If a rule is violated, no amount of confidence changes the verdict.

---

## 6. JSON Schema: AnalysisOutput

```json
{
  "id": "750f80f0-861b-4854-80d1-f8c8dfb6fc36",
  "symbol": "NZDUSD",
  "timeframe": "M15",
  "analysis_type": "thesis",
  "bias": "neutral",
  "setup_type": "liquidity_sweep_reclaim",
  "confidence_score": 0.6333,
  "alignment_score": 0.9922,
  "technical_score": 0.70,
  "price_action_score": 0.55,
  "fundamental_score": 0.65,
  "invalidations": [
    "M15 close below 0.5850",
    "Macro event in 20 minutes"
  ],
  "risk_notes": [
    "Spread elevated (2.1 pips)",
    "USD intermarket mixed"
  ],
  "verdict": "allowed",
  "veto_reason": "All checks passed, good confluence",
  "created_at": "2026-04-30T22:26:23.251736",
  "obsidian_link": "Trade-CLI-Vault/teses/2025-04-30-NZDUSD-M15-test.md",
  "analyst_notes": "Phase 1 test analysis"
}
```

**Field Descriptions:**
- `id` — UUID for tracking & auditability
- `symbol` — Trading pair (NZDUSD)
- `timeframe` — Timeframe (M5, M15, H1, H4)
- `bias` — bullish, bearish, neutral, fragile
- `confidence_score` — 0-1, how certain about analysis
- `alignment_score` — 0-1, agreement between engines
- `technical_score` — Technical engine score
- `price_action_score` — Price action engine score
- `fundamental_score` — Fundamental engine score
- `invalidations` — Specific events/prices that invalidate thesis
- `risk_notes` — Context concerns
- `verdict` — ALLOWED, WATCH_ONLY, BLOCKED
- `veto_reason` — Why this verdict (FTMO rule, low quality, etc.)

---

## 7. Phase 1 vs Phase 2+ Architecture Differences

### Phase 1 (Current)
```
Mocked Data Flow
└─ Terminal-only interface
   └─ Local engines (mock scores)
      └─ RiskGuardian (deterministic rules)
         └─ Obsidian + SQLite storage
```

### Phase 2 (Planned)
```
Live Data Flow (MT5 via Python API)
└─ Terminal + WebUI
   └─ LLM Orchestrator (Gemma local)
      ├─ Technical engine (real indicators)
      ├─ Price action engine (real charts)
      ├─ Fundamental engine (calendar API)
      ├─ Intermarket engine (new)
      ├─ Sentiment engine (new)
      └─ RiskGuardian (same, with live data)
         └─ Obsidian + SQLite + MongoDB (for scale)
```

**Key Additions Phase 2:**
- Real price data (MT5)
- LLM orchestration (Gemma local)
- Additional analytical engines
- Portfolio correlation tracking
- Historical backtesting

---

## 8. Database Views (for Learning)

Trade-CLI creates 4 SQL views for auditability & learning:

```sql
-- View: All allowed analyses with their outcomes
SELECT a.symbol, a.timeframe, a.verdict, a.confidence_score, a.alignment_score,
       o.price_action, o.invalidated, o.profit_loss_pips
FROM analyses a
LEFT JOIN analysis_outcomes o ON a.id = o.analysis_id
WHERE a.verdict = 'allowed'
ORDER BY a.created_at DESC;

-- View: Veto accuracy over time
SELECT veto_reason, COUNT(*) as veto_count,
       SUM(CASE WHEN overruled = 1 THEN 1 ELSE 0 END) as false_positives
FROM vetoed_ideas
GROUP BY veto_reason
ORDER BY veto_count DESC;

-- View: Motor performance (which engine scores most accurately)
SELECT e.engine_name, AVG(e.score) as avg_score, STDDEV(e.score) as variance
FROM engine_outputs e
JOIN analyses a ON e.analysis_id = a.id
WHERE a.verdict = 'allowed'
GROUP BY e.engine_name;

-- View: Best playbooks (patterns with highest success rate)
SELECT kb.setup_type, COUNT(*) as count, 
       SUM(CASE WHEN o.invalidated = 0 THEN 1 ELSE 0 END) as successes,
       ROUND(100.0 * SUM(CASE WHEN o.invalidated = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM knowledge_base kb
JOIN analyses a ON a.setup_type = kb.setup_type
LEFT JOIN analysis_outcomes o ON a.id = o.analysis_id
GROUP BY kb.setup_type
ORDER BY success_rate DESC;
```

---

## 9. Frozen Architectural Decisions (Phase 1)

See `docs/decisions-phase1.md` for 5 locked decisions:

1. **Dual Memory:** Obsidian (curated) + SQLite (structured)
2. **Taxonomy:** Teses, Ativos, Post-mortems, Playbooks, Sessions, Decisões
3. **Analysis Format:** JSON with required fields (bias, setup, confidence, alignment, invalidations, risk_notes, verdict)
4. **Engines:** Technical, Price Action, Fundamental, Thesis (synthesis)
5. **Asset Focus:** NZDUSD + M5/M15/H1/H4 timeframes

**Any changes to these 5 decisions require documented rationale in Fase 2 planning.**

---

## 10. Troubleshooting Common Issues

### Issue: "RiskGuardian loaded default rules (YAML error)"
**Cause:** `config/ftmo-rules.yaml` has syntax error
**Fix:**
```bash
python main.py show ftmo-rules  # See what rules are loaded
# Edit config/ftmo-rules.yaml and validate YAML syntax
```

### Issue: "Obsidian vault not found"
**Cause:** `Trade-CLI-Vault/` directory missing
**Fix:**
```bash
python main.py init  # Recreates vault structure
```

### Issue: "Database locked / no such table"
**Cause:** Corrupted database or migrations failed
**Fix:**
```bash
rm database.db
python main.py db-setup  # Recreates schema
```

### Issue: "Engine returned None score"
**Cause:** Phase 1 mock engines not returning data (shouldn't happen)
**Fix:**
- Review `engines/__init__.py` and ensure all engines return EngineOutput
- Run tests: `python -m pytest tests/test_core.py -v`

---

## 11. Key Performance Indicators (Phase 1)

Track these metrics to evaluate Phase 1 effectiveness:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Veto Accuracy | >90% (false positive rate <10%) | Count vetoed ideas vs actual rule violations |
| Allowed Success Rate | >60% (analyses that profited) | analysis_outcomes.invalidated = 0 |
| Motor Agreement | >80% (avg alignment_score) | AVG(alignment_score) from analyses table |
| Drawdown Protection | 100% (no violations) | Count(violations) = 0 |
| System Uptime | 99% (no crashes) | Monitor cli/main.py exceptions |

---

## 12. File Structure Summary

```
trade-cli/
├─ Trade-CLI-Vault/          # Obsidian vault
│  ├─ 00-meta/
│  ├─ ativos/
│  ├─ teses/
│  ├─ post-mortems/
│  ├─ playbooks/
│  ├─ sessions/
│  └─ prop-firm/
│
├─ core/                      # Core business logic
│  ├─ analysis_schema.py
│  ├─ risk_guardian.py
│  └─ scoring.py
│
├─ engines/                   # Analytical engines
│  └─ __init__.py
│
├─ db/                        # Database
│  ├─ db_schema.sql
│  ├─ migrations.py
│  └─ models.py
│
├─ cli/                       # Terminal interface
│  └─ main.py
│
├─ config/                    # Configuration
│  └─ ftmo-rules.yaml
│
├─ docs/                      # Documentation
│  ├─ obsidian-structure.md
│  ├─ decisions-phase1.md
│  ├─ phase1-architecture.md  (this file)
│  └─ risk-guardian-guide.md
│
├─ tests/                     # Unit tests
│  └─ test_core.py
│
├─ database.db                # SQLite database (created on init)
├─ requirements.txt           # Python dependencies
├─ main.py                    # Entry point
└─ README.md                  # Quick start guide
```

---

**Fase 1 Status:** ✓ Architecture complete, all components documented and tested.

**Next:** Fase 2 planning with user feedback on Phase 1 stability.
