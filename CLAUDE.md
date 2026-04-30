# Trade-CLI — Copilot/Claude Instructions

**MANDATORY READING** — This file ensures every development session starts aligned with project reality.

---

## 🎯 Project Identity

**Trade-CLI** is a LOCAL AI analytical copilot for Forex trading decisions. It NEVER executes real trades.

**Sole Purpose:** Analysis, knowledge management, and decision support.

---

## 🔒 Architecture Rules (NON-NEGOTIABLE)

### Rule 1: RiskGuardian is ALWAYS Final Decision Layer
- Every analysis → RiskGuardian.should_block()
- If BLOCKED → verdict is BLOCKED (no override possible)
- Only test mode can bypass (--test flag)

### Rule 2: Every Engine Must Return EngineOutput
```python
EngineOutput(
    engine_name="technical",
    score=0.0,          # 0.0 to 1.0
    explanation="...",  # why this score
    evidence={...}      # data used
)
```

### Rule 3: LLM Synthesizes, Never Replaces
- LLM orchestrator synthesizes engine outputs
- Explains reasoning to user
- Never overrides RiskGuardian checks
- Gemma 7B local (Ollama) — zero cost

### Rule 4: Dual Memory
- **Obsidian:** Human-readable knowledge (teses, playbooks, concepts)
- **SQLite:** Structured event log + vector embeddings for RAG
- Never dump chat logs to Obsidian

### Rule 5: No Live Trading Orders
- MT5 integration: Read-only data access
- No order placement through CLI
- Account state queries only

### Rule 6: No Cloud APIs (Free & Local Only)
- ❌ Claude API
- ❌ OpenAI
- ❌ TradingView Premium
- ✅ Local Gemma (Ollama)
- ✅ Local embeddings (sentence-transformers)
- ✅ Local vector DB (FAISS)

---

## 📊 Current Status

### Phase 1 (COMPLETE ✓)
- ✓ Schema & dataclasses (core/analysis_schema.py)
- ✓ RiskGuardian (core/risk_guardian.py)
- ✓ Mock engines (technical, price_action, fundamental)
- ✓ ThesisEngine synthesizer
- ✓ CLI (6 subcommands: analyze, init, health, show, db-setup, version)
- ✓ Obsidian vault (7 folders + 5 templates)
- ✓ SQLite schema (5 tables)
- ✓ 15 unit tests (100% passing)

### Phase 2 (ACTIVE 🚀)
- 🚧 MT5 data client (data/mt5_client.py)
- 🚧 Knowledge RAG system (knowledge/ module)
- 🚧 LLM orchestrator (orchestrator/ + Ollama Gemma)
- 🚧 Training system (training/ + knowledge ingestion)
- 🚧 New engines (sentiment, intermarket, volume)
- 🚧 CLI commands (train, knowledge, outcome, review)
- 🚧 Obsidian expansion (metodos/, conceitos/, treino/, revisoes/)

### Phase 3 (FUTURE)
- TradingView webhooks
- Advanced engines (Wyckoff, ICT, SMC)
- Visual backtesting

---

## 🛠️ Code Standards

### Type Hints
```python
# ✓ REQUIRED on all functions
def analyze(symbol: str, timeframe: str, data: pd.DataFrame) -> AnalysisOutput:
    pass

# ✗ NOT ALLOWED
def analyze(symbol, timeframe, data):
    pass
```

### Dataclasses
```python
# ✓ Use for all data structures
@dataclass
class MyOutput:
    score: float
    explanation: str

# ✗ Avoid dicts for important data
my_output = {"score": 0.5, "explanation": "..."}
```

### Testing
- Minimum 80% coverage on core/ and engines/
- Test location: tests/test_*.py
- Run: `pytest tests/ -v --cov`

### Never Commit
- database.db
- .env (use .env.example as template)
- Model files (*.gguf, *.bin)
- __pycache__, .pytest_cache

---

## 📁 File Structure (Exact)

```
Trade-CLI/
├── core/                     ✓ FROZEN Phase 1
│   ├── analysis_schema.py    (dataclasses)
│   └── risk_guardian.py      (veto layer)
│
├── engines/                  🚧 Phase 2
│   ├── __init__.py           (ThesisEngine)
│   ├── technical.py          (needs real MT5 data)
│   ├── price_action.py
│   ├── fundamental.py
│   ├── sentiment.py          ❌ TO CREATE Phase 2.4
│   ├── intermarket.py        ❌ TO CREATE Phase 2.4
│   └── volume.py             ❌ TO CREATE Phase 2.4
│
├── data/                     ❌ TO CREATE Phase 2.2
│   ├── mt5_client.py         (read-only wrapper)
│   ├── mock_data.py          (fallback)
│   ├── market_data.py        (OHLCV abstraction)
│   └── calendar_client.py    (economic calendar)
│
├── knowledge/                ❌ TO CREATE Phase 2.2
│   ├── obsidian_reader.py    (reads vault files)
│   ├── chunk_vectorizer.py   (text→embeddings)
│   ├── rag_retriever.py      (FAISS search)
│   └── context_builder.py    (LLM context assembly)
│
├── orchestrator/             ❌ TO CREATE Phase 2.3
│   ├── llm_client.py         (Ollama wrapper)
│   ├── orchestrator.py       (engine decisions + synthesis)
│   ├── tool_registry.py      (engine registry)
│   └── prompt_templates.py   (structured prompts)
│
├── training/                 ❌ TO CREATE Phase 2.2
│   ├── ingest.py             (PDF/Markdown/TXT parsing)
│   ├── chunker.py            (semantic chunks)
│   ├── tagger.py             (auto-tagging)
│   ├── kb_writer.py          (SQLite + Obsidian)
│   └── review_feeder.py      (post-mortem processing)
│
├── db/                       ✓ Phase 1 + Phase 2.5
│   ├── db_schema.sql         (update Phase 2.5)
│   └── migrations.py         ✓
│
├── cli/                      ✓ Phase 1 + Phase 2.4
│   └── main.py               (update with train, knowledge, etc.)
│
├── config/                   ✓ Phase 1 + Phase 2.1
│   ├── ftmo-rules.yaml       ✓
│   └── assets.yaml           ❌ TO CREATE Phase 2.1
│
├── docs/                     ✓ Phase 1
│   ├── obsidian-structure.md
│   ├── decisions-phase1.md
│   ├── phase1-architecture.md
│   └── decisions-phase2.md   ❌ TO CREATE Phase 2.5
│
├── Trade-CLI-Vault/          ✓ Phase 1 + Phase 2.5
│   ├── 00-meta/              ✓ + update templates
│   ├── ativos/               ✓ + add EURUSD/USDJPY/USDCAD
│   ├── metodos/              ❌ TO CREATE
│   ├── conceitos/            ❌ TO CREATE
│   ├── teses/                ✓
│   ├── post-mortems/         ✓
│   ├── playbooks/            ✓
│   ├── sessions/             ✓
│   ├── prop-firm/            ✓
│   ├── treino/               ❌ TO CREATE
│   └── revisoes/             ❌ TO CREATE
│
├── tests/                    ✓ Phase 1 + Phase 2
│   ├── test_core.py          ✓ (15 tests)
│   ├── test_rag.py           ❌ TO CREATE
│   ├── test_orchestrator.py  ❌ TO CREATE
│   └── test_engines.py       ❌ TO CREATE
│
├── .gitignore                ✓ Phase 2.1
├── requirements.txt          ✓ Phase 2.1
├── .env.example              ✓
├── CLAUDE.md                 ✓ Phase 2.1 (this file)
├── main.py                   ✓
├── README.md                 ✓
└── database.db               (git ignored)
```

---

## 🎬 When Adding a New Feature

### 1. Schema Update
```python
# core/analysis_schema.py
@dataclass
class AnalysisOutput:
    # Add new fields with type hints
    sentiment_score: float = 0.0
    # Don't remove existing fields (backward compat)
```

### 2. Database Migration
```sql
-- db/db_schema.sql
-- Add new column or table
-- Don't modify existing schema (use ALTER TABLE)
```

### 3. Engine Integration
```python
# engines/__init__.py (ThesisEngine)
# Update synthesis logic if adding new engine
# Ensure all 6 engines now contribute to final score
```

### 4. CLI Command
```python
# cli/main.py
@app.command()
def new_command(param: str):
    """Your command description"""
    # Implementation
```

### 5. Tests
```python
# tests/test_new_feature.py
def test_something():
    # Arrange
    # Act
    # Assert (>80% coverage required)
```

### 6. Documentation
```markdown
# docs/decisions-phase2.md
## New Feature Decision
- Why: ...
- How: ...
- Trade-offs: ...
```

---

## 🚫 Forbidden Actions (STRICT)

### Network & Cloud
- ❌ Never add calls to cloud APIs (Claude, OpenAI, etc.)
- ❌ Never store API keys in code
- ❌ Never send user data to external services

### Data & Privacy
- ❌ Never commit database.db
- ❌ Never commit .env files
- ❌ Never log sensitive data

### Orders & Trading
- ❌ Never implement order placement
- ❌ Never execute real trades
- ❌ MT5 read-only only

### Architecture
- ❌ Never bypass RiskGuardian
- ❌ Never modify frozen core schema without migration
- ❌ Never hardcode credentials
- ❌ Never mix mock data with real data without clear labeling

### Obsidian
- ❌ Never dump chat logs to vault
- ❌ Never commit .obsidian/cache/
- ❌ Never remove existing template structure

---

## 💾 Ollama Setup (Required for Phase 2)

```bash
# 1. Install Ollama (https://ollama.ai)
# 2. Run in background: ollama serve
# 3. Download Gemma:
#    ollama pull gemma:7b
# 4. Test:
#    ollama list  # should show gemma:7b
# 5. Python can now call it:
#    import ollama
#    response = ollama.chat(model="gemma:7b", messages=[...])
```

**Zero cost, zero privacy concerns, 100% offline.**

---

## 📝 Primary Symbols (Replace NZDUSD)

Phase 1 used NZDUSD for testing only. Phase 2 focuses on:

### Forex (Major pairs)
- EURUSD (most important)
- USDJPY
- USDCAD

### Indices
- US30 (Dow Jones)
- NAS100 (NASDAQ)

### Removed
- NZDUSD (Phase 1 testing only — use EURUSD)

---

## 🔍 Analysis Output Contract (CRITICAL)

Every `python main.py analyze SYMBOL TF` must produce:

```python
AnalysisOutput(
    # Required
    symbol="EURUSD",
    timeframe="H1",
    bias="bullish|bearish|neutral|fragile",
    setup_type="setup_name",
    confidence_score=0.0-1.0,
    alignment_score=0.0-1.0,
    
    # Engine scores
    technical_score=0.0-1.0,
    price_action_score=0.0-1.0,
    fundamental_score=0.0-1.0,
    # Phase 2 new:
    sentiment_score=0.0-1.0,
    intermarket_score=0.0-1.0,
    volume_score=0.0-1.0,
    
    # Context (Phase 2)
    session="london|tokyo|new_york|overlap",
    market_regime="trending|ranging|volatile",
    macro_risk="high|medium|low",
    
    # LLM (Phase 2)
    llm_used=True/False,
    llm_model="gemma:7b",
    llm_reasoning="...",
    
    # Required always
    invalidations=["condition1", "condition2"],
    risk_notes=["risk1", "risk2"],
    verdict="allowed|watch_only|blocked",
    
    # Source tracking
    data_source="mt5|mock",
    obsidian_link="[[teses/...]]",
    
    # Graphify (Obsidian)
    method_links=["[[metodos/ICT]]"],
    concept_links=["[[conceitos/order-block]]"]
)
```

---

## 🧠 Knowledge Base Philosophy

When training the system with knowledge:

1. **Process > Content** — Document HOW to analyze, not just WHAT to analyze
2. **Curated > Comprehensive** — Less noise = better RAG retrieval
3. **Always Provide Context** — Every concept needs: when to use, when NOT to use, examples
4. **Tag Consistently** — [symbol, method, timeframe, confidence_level, setup_type]

---

## 🔄 Obsidian Vault Rules

### Frontend
- Every note must have frontmatter: type, symbol, created, tags
- Every thesis links to: [[ativos/SYMBOL]], [[metodos/METHOD]], [[conceitos/CONCEPT]]
- Post-mortems link back to original thesis
- Training notes go in: treino/ with proper template

### Graphify Integration
- Links create knowledge graph
- Every note should have 2-3 outgoing links minimum
- Use consistent naming: [[symbol/EURUSD]], [[conceitos/order-block]]

### No Auto-Dump
- CLI never auto-saves chat to Obsidian
- Only save vetted, structured notes
- Reviews always manual before commit

---

## 🚨 When Something Breaks

### Database Error
```bash
rm database.db
python main.py init
```

### Ollama Not Running
```bash
# Terminal 1:
ollama serve

# Terminal 2:
python main.py analyze EURUSD H1
```

### Import Errors
```bash
pip install -r requirements.txt
python -c "import ollama; print(ollama.__version__)"
```

### Test Failures
```bash
pytest tests/ -v --tb=short
# Check what changed since last Phase
```

---

## 📞 Decision Escalation

If you need to change:
- ✅ Add new engine? Document in decisions-phase2.md
- ✅ Change CLI command? Update this file + README
- ✅ New data source? Add to data/ module
- ❌ Modify RiskGuardian logic? STOP — contact user first
- ❌ Change core schema? STOP — requires migration strategy
- ❌ Add cloud API? STOP — violates architecture rules

---

## ⚡ Quick Reference

```bash
# Health check
python main.py health

# Run analysis
python main.py analyze EURUSD H1

# Train with knowledge
python main.py train --file "ict.pdf" --topic "ict"

# Run tests
pytest tests/ -v --cov

# Update database
python main.py db-setup

# Check LLM
ollama list
```

---

**Last Updated:** 2026-04-30  
**Phase:** 2 (Active)  
**Context Level:** MANDATORY FOR ALL SESSIONS
