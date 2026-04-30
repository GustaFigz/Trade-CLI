# Decisões Arquiteturais - Fase 1

**Data:** 30 de Abril de 2025  
**Status:** Frozen (Referência da Fase 1)  
**Validação:** Alinhado com projeto-ia-trading-forex.md + Fase 1.md

---

## 5 Decisões de Base (Definidas em Fase 1)

### DECISÃO 1: Estrutura Dual de Memória

**Decidido:** Obsidian para conhecimento curado + SQLite para dados estruturados

**Racional:**
- Obsidian deve guardar apenas notas navegáveis e reutilizáveis
- Banco estruturado guarda eventos, scores, histórico, cálculos
- Evita "despejo" indiscriminado de logs/chats que degrada recuperação
- Permite análise quantitativa (querys SQL) + análise qualitativa (navegação Obsidian)

**Implementação:**
- Obsidian: 7 pastas com estrutura clara (ativos/, teses/, post-mortems/, playbooks/, sessions/, prop-firm/, 00-meta/)
- SQLite: 5 tabelas (analyses, analysis_outcomes, engine_outputs, vetoed_ideas, knowledge_base)

**Congelado por:** Uso na Fase 2+ (não mudar sem aprovação)

---

### DECISÃO 2: Taxonomia de Notas (Unidades de Memória)

**Decidido:** Nota por Tese + Nota por Ativo + Nota por Post-Mortem (+ outras se ajudar)

**Racional:**
- Nota por tese: cada análise é isolada, consultável, com contexto completo
- Nota por ativo: hub consolidado (NZDUSD.md agrupa análises, playbooks, histórico do par)
- Nota por post-mortem: comparação tese vs realidade obriga a aprender
- Outras notas (playbooks, sessions, decisões): suportam o fluxo

**Alternativas rejeitadas:**
- Minimalista (só teses) — perde contexto de ativo
- Intermediária (só playbooks + journals) — fragmenta análises individuais
- Analítica com banco (redundância entre vault e SQLite)

**Estrutura final:**
```
Teses: 2025-04-30-NZDUSD-M15-setup.md
Ativos: NZDUSD.md (hub)
Post-Mortems: 2025-04-30-NZDUSD-M15-postmortem.md
Playbooks: liquidity-sweep-reclaim.md
Sessions: daily-context-2025-04-30.md
Decisões: prop-firm/ftmo-rules.md
```

**Congelado por:** Taxonomia (não adicionar novos tipos sem deliberação)

---

### DECISÃO 3: Formato de Análise (JSON Estruturado)

**Decidido:** Toda análise segue estrutura JSON consistente

**Schema:**
```json
{
  "symbol": "NZDUSD",
  "timeframe": "M15",
  "bias": "bullish_but_fragile",
  "setup_type": "liquidity_sweep_reclaim",
  "confidence": 0.68,
  "alignment_score": 0.61,
  "invalidations": ["M15 close below X", "macro event in 20m"],
  "risk_notes": ["spread elevated", "USD intermarket mixed"],
  "verdict": "watch_only"
}
```

**Racional:**
- Garante auditabilidade (rastreável de volta ao motor que gerou)
- Permite querys (buscar por confidence > 0.7, etc.)
- Serialização JSON viabiliza armazenamento e transmissão
- Evita narrativa fuzzy ("parece que..." → scores explícitos)

**Campos obrigatórios:**
- `symbol`, `timeframe` — coordenadas da análise
- `bias` — bullish, bearish, neutral, fragile
- `setup_type` — nome do padrão (liquidity_sweep, pullback_continuation, etc.)
- `confidence` — 0.0–1.0 (quão certo está)
- `alignment_score` — 0.0–1.0 (consenso entre motores)
- `invalidations` — array de condições que matam a tese
- `verdict` — allowed, watch_only, blocked (resultado de RiskGuardian)

**Congelado por:** Serialização (não mudar schema sem migration)

---

### DECISÃO 4: Motores Analíticos Iniciais (Fase 1 Focus)

**Decidido:** 4 motores + 1 consolidador + 1 guardião em Fase 1

**Motores implementados:**

| Motor | Responsabilidade | Saída |
|-------|-----------------|-------|
| **Técnico** | Tendência, suportes, resistências, regime | EngineOutput (score 0-1) |
| **Price Action** | Candles, padrões, qualidade de movimento | EngineOutput (score 0-1) |
| **Fundamental** | Macro, juros, eventos, viés | EngineOutput (score 0-1) |
| **Tese** | Consolida 3 motores, monta bias, invalidação | AnalysisOutput (JSON completo) |
| **Risco** | Aplica regras FTMO, decide verdict | ProposalVerdictOutput (allowed/watch_only/blocked) |

**Motores NÃO em Fase 1 (Fase 2+):**
- Intermarket (correlatos, DXY, yields)
- Sentimento (consensus, positioning)
- Volume Profile (POC, HVN, LVN)
- Wyckoff (acumulação, distribuição)
- ICT/SMC (liquidez, order blocks, displacement)
- Microestrutura (ticks, spread, tape)
- Visual (Gemma interpreta screenshots)

**Racional:**
- 4 motores cobrem análise mínima viável (técnica + contexto)
- RiskGuardian determinístico previne operar trash
- Expansão em Fase 2 sem quebrar foundação
- Cada motor tem interface clara (input → EngineOutput)

**Congelado por:** Interface de motores (contrato público)

---

### DECISÃO 5: Scope Controlado (Asset List + Timeframes)

**Decidido:** NZDUSD, M5/M15/H1/H4, FTMO como firm inicial

**Parâmetros:**

| Parâmetro | Fase 1 | Fase 2+ |
|-----------|--------|---------|
| **Par primário** | NZDUSD | +EURUSD, USDCAD |
| **Índices** | — | DXY, SPX, yields |
| **Timeframes** | M5, M15, H1, H4 | +M30, D1 (análise) |
| **Prop Firm** | FTMO | +outras firms |
| **MT5 dados** | Mock (Fase 1) | Real (Fase 2) |

**Racional:**
- NZDUSD: par suficientemente volátil, spread controlado, boa liquidez
- M5-H4: scalping (M5/M15) + contexto (H1/H4)
- FTMO: regras claras, drawdown duro, documentação boa
- Mock data: permite validar logic sem live data

**Congelado por:** Scope (não adicionar pares/timeframes sem plan de rollout)

---

## Decisões Secundárias

### Interface: Terminal CLI

**Decidido:** Terminal CLI (Python Click/Typer), sem Web UI

**Racional:**
- Terminal-first alinha com usabilidade local
- Diferida GUI para Fase 2+ (quando sistema estável)
- CLI permite automação e piping

**Congelado:** Sim (não adicionar Web UI em Fase 1)

---

### Stack Técnico

**Decidido:**
- Python 3.10+
- SQLite (local, simples)
- Obsidian (vault text, versionável)
- Click ou Typer (CLI)
- YAML para config (ftmo-rules.yaml)

**Congelado:** Stack (não mudar para Postgres/FastAPI sem deliberação)

---

### Sem Integração MT5/TradingView em Fase 1

**Decidido:** Apenas estrutura + stubs, dados serão mocked

**Racional:**
- Fase 1 é desenho da foundação, não integração
- MT5 integração chega em Fase 2 (quando arquitetura estável)
- TradingView webhooks chega em Fase 3 (automação)

**Congelado:** Sim (dados mock até Fase 2)

---

## Princípios que Guiam Estas Decisões

1. **Sem IA generativa rodando sozinha** → RiskGuardian determinístico veta
2. **Análise profunda vem de arquitetura e dados** → motores especializados + banco estruturado
3. **Memória curada, não bruta** → templates fixos + taxonomia clara
4. **Terminal-first permite auditabilidade** → cada comando deixa rastro
5. **Scope controlado evita ambição excessiva** → começar com 1 par, expandir depois

---

## Validação Contra Documentos Originais

### ✅ Alinhamento com `projeto-ia-trading-forex.md`

**Roadmap Fase 1 do projeto:**
- ✓ Escolher prop firm (FTMO) e modelar suas regras → DECISÃO 5 + ftmo-rules.yaml
- ✓ Integrar MT5 → diferida para Fase 2 (conforme user choice)
- ✓ Integrar TradingView → diferida para Fase 3
- ✓ Criar estrutura Obsidian → DECISÃO 1 + 2
- ✓ Implementar motores (técnico, price action, fundamental, risco) → DECISÃO 4

**6 Princípios de Projeto:**
1. IA não executa trades reais ✓ (RiskGuardian bloqueia)
2. LLM não é motor único ✓ (motores especializados)
3. Análise profunda com dados estruturados ✓ (SQLite schema)
4. Order flow com limitações claras ✓ (documentado)
5. Prop firm vem antes da tese ✓ (RiskGuardian determinístico)
6. Memória curada ✓ (templates + taxonomia)

**Arquitetura em Camadas:**
- Interface ✓ (CLI)
- Motores Analíticos ✓ (4 motores)
- Motor de Tese ✓ (sintetizador)
- Guardião de Risco ✓ (RiskGuardian)
- Memória ✓ (Obsidian + SQLite)

### ✅ Alinhamento com `Fase 1.md`

**3 Etapas de Fase 1:**
- Etapa 1: Desenho lógico ✓ (este documento + schema + rules)
- Etapa 2: Ficheiros reais ✓ (templates, vault, DB)
- Etapa 3: Comando que gera análise ✓ (CLI + motores)

**5 Decisões de Base:**
1. Árvore do Obsidian ✓ (DECISÃO 1 + 2)
2. Templates ✓ (Etapa 2 deliverable)
3. Schema banco local ✓ (DECISÃO 3 + db_schema.sql)
4. Formato da análise ✓ (DECISÃO 3)
5. Lista curta de ativos/timeframes ✓ (DECISÃO 5)

---

## Status de Freezing

| Decisão | Status | Próxima Review |
|---------|--------|---|
| Memória Dual | ✅ Frozen | Fase 2 |
| Taxonomia | ✅ Frozen | Fase 2 |
| Formato JSON | ✅ Frozen | Fase 2 |
| Motores | ⚠️ Semi-frozen | Expandir em Fase 2 |
| Scope (NZDUSD) | ✅ Frozen | Fase 2 (expandir com plan) |
| CLI | ⚠️ Semi-frozen | Adicionar subcomandos em Fase 2 |
| Stack | ✅ Frozen | Major change requer review |

---

## Mudanças Futuras (Fase 2+)

Se qualquer decisão precisar mudar:
1. Documentar **por quê** (contexto)
2. Revisar impacto na arquitetura
3. Atualizar este documento
4. Comunicar a todas as camadas afetadas

Exemplo: Se em Fase 2 descobrirmos que Postgres é necessário em vez de SQLite:
```markdown
## Mudança Phase 2: SQLite → Postgres

**Razão:** Concorrência, volume de dados, queries complexas
**Impacto:** db/migrations.py, schema atualizado
**Migração:** Script de dump SQLite → import Postgres
**Data:** 2025-06-XX
**Aprovação:** [Name]
```

---

## Referências

- Documento original: `projeto-ia-trading-forex.md`
- Planeamento Fase 1: `Fase 1.md`
- Obsidian structure: `docs/obsidian-structure.md`
- FTMO rules: `config/ftmo-rules.yaml`
- DB schema: `db/db_schema.sql`
