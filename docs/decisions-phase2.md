# Architecture Decisions — Phase 2
**Status:** Active | **Last Updated:** 2026-05-01

---

## ADR-001: Ollama + Gemma como LLM local
**Status:** Accepted  
**Context:** Need LLM synthesis for trading analysis. Cloud APIs (OpenAI, Anthropic)
expose trading strategy data and have per-token costs.  
**Decision:** Use Ollama running locally with gemma:7b as default model.  
**Consequences:**  
✅ Privacy — trading data never leaves the machine  
✅ Offline — works without internet connection  
✅ No cost per call — free to run 24/7  
❌ Requires local GPU/CPU (slower than cloud on CPU)  
❌ Model must be downloaded via `ollama pull gemma:7b`  
**Fallback:** Analysis works without LLM (`use_llm=False` or `--no-llm` flag).

---

## ADR-002: FAISS para vector search
**Status:** Accepted  
**Context:** Need semantic search over knowledge base for RAG.  
**Decision:** faiss-cpu with all-MiniLM-L6-v2 embeddings (384 dims).  
**Consequences:**  
✅ No server needed — runs in-process  
✅ Fast in-memory search — sub-millisecond for small indexes  
✅ Portable — index saved as .faiss file  
❌ Index must be rebuilt when knowledge base changes significantly  
❌ RAM-bound for very large indexes

---

## ADR-003: Obsidian como frontend de conhecimento
**Status:** Accepted  
**Context:** Need human-readable, editable knowledge base with graph view.  
**Decision:** Obsidian vault at Trade-CLI-Vault/ with Graphify plugin.  
**Consequences:**  
✅ Graph visualization with Graphify plugin  
✅ Human editable — trader can review and annotate  
✅ Markdown = readable by LLM directly (no parsing needed)  
❌ Requires Obsidian installed locally  
❌ [[wikilinks]] must follow consistent naming for graph to work

---

## ADR-004: MT5 read-only, nunca escreve ordens
**Status:** Accepted — NON-NEGOTIABLE  
**Context:** Safety constraint for FTMO compliance.  
**Decision:** MT5Client only reads bars, ticks, account state. Never places orders.  
**Consequences:**  
✅ Zero execution risk — cannot accidentally trade  
✅ Safe to run 24/7 without supervision  
✅ FTMO compliant — no automated order placement  
❌ Cannot automate entries (by design — user must execute manually)

---

## ADR-005: ThesisEngine mantém stubs na Fase 1→2 transition
**Status:** Accepted (temporary, until Phase 2.3)  
**Context:** Engines precisam de dados reais do MT5 para funcionar correctamente.  
**Decision:** Manter engines como mocks inteligentes (symbol-agnostic) até Fase 2.3
quando os dados MT5 estiverem estáveis e testados.  
**Consequences:**  
✅ Sistema funciona end-to-end em modo mock — useful for development  
✅ RiskGuardian ainda aplica regras reais  
❌ Análises ainda não são reais — apenas mock scores  
**Migration path:** Phase 2.3 adds real bars to TechnicalEngine via `bars` param

---

## ADR-006: Orchestrator como camada de composição
**Status:** Accepted  
**Context:** CLI needs single entry point that composes MT5 + RAG + LLM + Engines + Risk.  
**Decision:** `Orchestrator.analyze()` é o único método chamado pelo CLI.
Degradação graciosa: funciona mesmo sem LLM, sem MT5, sem RAG.  
**Consequences:**  
✅ Each component can fail without crashing the system (try/except at each step)  
✅ Flags: `--no-llm`, `--no-rag`, `--test` for selective disabling  
✅ Single entry point = easy to test and debug  
❌ Extra indirection layer vs calling engines directly

---

## 🗺️ Phase 3 Roadmap

| Fase | Deliverable | Target |
|------|-------------|--------|
| 2.3 | Engines reais com dados MT5 (TechnicalEngine com RSI/MA/MACD reais) | Next |
| 2.4 | Engines ICT/SMC/Wyckoff (order blocks, FVG, liquidity sweeps) | Soon |
| 3.0 | TradingView webhook listener | Future |
| 3.1 | Backtesting engine | Future |
| 3.2 | Performance analytics dashboard | Future |

---

*Last Updated: 2026-05-01 by Antigravity*  
*Reference: docs/decisions-phase1.md (frozen Phase 1 decisions)*
