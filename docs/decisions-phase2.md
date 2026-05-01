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

## ADR-007: Gemma4:e4b como modelo default (Phase 2.3)
**Status:** Accepted  
**Context:** Phase 1 used gemma3:latest; Phase 2.3 moved to 4-bit quantization for lower memory.  
**Decision:** Update OLLAMA_MODEL default to gemma4:e4b across .env, orchestrator, tests.  
**Consequences:**  
✅ Smaller model (3.5B params 4-bit) = faster inference on CPU  
✅ Better reasoning than gemma3 with same footprint  
❌ Requires `ollama pull gemma4:e4b` once  
❌ Inference slightly slower on low-end hardware  
**Fallback:** Can use any OpenAI-compatible endpoint via LLM_API_BASE env var.

---

## ADR-008: Chat history persistence (Phase 2.3)
**Status:** Accepted  
**Context:** REPL sessions are ephemeral; trader loses conversation context on exit.  
**Decision:** Save chat history to ~/.tradecli/chat_history.json (max 40 messages).
Load on session init, save after each interaction. Async to not block.  
**Consequences:**  
✅ Conversation survives process restart  
✅ Easy to audit trader decisions retroactively  
✅ Lightweight JSON (no database overhead)  
❌ File grows unbounded without pruning (max 40 msg limit caps it)  
❌ No encryption (trader's machine is the trust boundary)

---

## ADR-009: Streaming responses (Phase 2.3)
**Status:** Accepted  
**Context:** LLM synthesis can take 5-10 sec on CPU; user sees no feedback.  
**Decision:** Add `LLMClient.stream_chat()` Iterator[str] method for token-by-token output.
CLI launcher displays tokens in Live widget from rich.progress.  
**Consequences:**  
✅ User sees immediate feedback — better UX  
✅ Identifies stuck processes faster  
✅ Token streaming = no memory buffer for large responses  
❌ Cannot easily handle streaming errors mid-response  
❌ Rich Live widget adds complexity to launcher

---

## ADR-010: Six-engine synthesis with new engines (Phase 2.4)
**Status:** Accepted  
**Context:** Phase 1 had 3 engines (technical, price_action, fundamental); Phase 2.4 adds 3 more.  
**Decision:** Add SentimentEngine, IntermarketEngine, VolumeEngine. ThesisEngine.synthesize()
averages all 6 scores for final confidence/alignment. All 6 included in AnalysisOutput.  
**Consequences:**  
✅ Richer signal = better confluence detection  
✅ Sentiment/intermarket cheaper than 3 real engines  
✅ Volume profile adds new risk dimension  
❌ avg_score(6) differs from avg_score(3) — alignment/confidence change  
❌ New engines initially deterministic heuristics, not real data  
**Migration:** Phase 2.4+ implements real sentiment (RSS), real correlations (USD index), real volume.

---

## ADR-011: Obsidian wikilinks for knowledge graph (Phase 2.4)
**Status:** Accepted  
**Context:** RAG needs structured knowledge; free-form text is hard to discover.  
**Decision:** Every vault note must have [[symbol]], [[method]], [[concept]] wikilinks
(minimum 2 per note). RAGRetriever returns chunks sorted by graph distance.  
**Consequences:**  
✅ Obsidian Graphify shows knowledge interconnections  
✅ RAG ranks by both TF-IDF similarity AND wikilink proximity  
✅ Graph forces trader to structure knowledge  
❌ Requires manual tagging of each note  
❌ Wikilinks break if folder/file renamed

---

## ADR-012: PromptSession with persistent REPL history (Phase 2.3)
**Status:** Accepted  
**Context:** Plain console.input() has no history, autocomplete, or persistence.  
**Decision:** Replace with prompt_toolkit.PromptSession + FileHistory at ~/.tradecli/repl_history.
Auto-suggest from history, arrow keys for navigation.  
**Consequences:**  
✅ Trader can repeat recent commands quickly  
✅ Command history survives process restart  
✅ Better UX — familiar like bash/zsh  
❌ prompt_toolkit adds dependency  
❌ History file has no encryption

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
