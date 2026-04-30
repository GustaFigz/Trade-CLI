# Trade-CLI — Plano de Melhorias, Fase 2 e Sistema de Treino
> Documento gerado com base em análise completa do repositório GustaFigz/Trade-CLI  
> Data: 2026-04-30  
> Status: Referência viva — atualizar a cada ciclo de melhorias

---

## 1. Estado atual (Fase 1 — o que está bem)

| Componente | Status | Observação |
|---|---|---|
| `core/analysis_schema.py` | ✅ Sólido | Dataclasses bem tipadas, serialização JSON, validação |
| `core/risk_guardian.py` | ✅ Sólido | Determinístico, FTMO hardcoded em YAML |
| `core/scoring.py` | ✅ Presente | Score de alinhamento entre motores |
| `engines/technical.py` | ⚠️ Mock | Existe mas usa dados fictícios |
| `engines/price_action.py` | ⚠️ Mock | Existe mas usa dados fictícios |
| `engines/fundamental.py` | ⚠️ Mock | Existe mas usa dados fictícios |
| `engines/__init__.py` (ThesisEngine) | ✅ Funcional | Sintetiza motores, calcula alignment |
| `db/db_schema.sql` | ✅ Sólido | 5 tabelas: analyses, outcomes, engine_outputs, vetoed_ideas, knowledge_base |
| `cli/main.py` (Typer) | ✅ Funcional | Commands: analyze, init, health, show, version, db-setup |
| `config/ftmo-rules.yaml` | ✅ Correto | Thresholds FTMO carregados no runtime |
| `Trade-CLI-Vault/` | ✅ Estrutura OK | 00-meta, ativos, teses, post-mortems, playbooks, sessions, prop-firm |
| `Trade-CLI-Vault/00-meta/` | ✅ Templates OK | 4 templates: thesis, postmortem, playbook, daily-context |
| `.env.example` | ✅ Organizado | MT5, TradingView, Gemma, DB, Obsidian |
| `requirements.txt` | ⚠️ Incompleto | Só 5 deps. Falta MT5, anthropic, rich, requests, etc. |
| `database.db` | ❌ Commitado | Ficheiro vazio no git — deve estar no .gitignore |
| `Fase 1.md` | ⚠️ Ruído | Contém texto de chat — não é documentação de código |

---

## 2. Problemas críticos a corrigir já

### 2.1 `.gitignore` ausente ou incompleto

**Problema:** `database.db` está commitado (0 bytes). Não deve nunca entrar no git.

**Correção — criar `.gitignore` na raiz:**

```gitignore
# Database
database.db
*.db
*.sqlite3

# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
*.egg
.venv/
venv/
env/

# Logs
*.log
trade-cli.log

# Models (Gemma — large files)
models/
*.gguf
*.bin
*.safetensors

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/settings.json
.idea/

# Tests cache
.pytest_cache/
.coverage
htmlcov/

# Fase 1.md (chat dump — não é documentação real)
"Fase 1.md"
```

---

### 2.2 `requirements.txt` desatualizado

**Problema:** Só tem 5 packages. Para Fase 2 e treino já precisas de mais.

**Correção — `requirements.txt` atualizado:**

```txt
# Core CLI
python-dotenv==1.0.0
typer==0.9.0
click==8.1.7
pyyaml==6.0.1
rich==13.7.0

# Testing
pytest==7.4.3

# Data & Analysis
pandas>=2.0.0
numpy>=1.26.0
ta>=0.11.0

# MT5 Integration (Phase 2 — Windows only)
# MetaTrader5>=5.0.45  # Uncomment on Windows

# LLM Integration (Phase 2)
anthropic>=0.25.0      # Claude / Haiku via API (backup)
# ollama>=0.1.0        # For local Gemma via Ollama

# HTTP & Webhooks
requests>=2.31.0
httpx>=0.27.0

# Scheduling
schedule>=1.2.0

# Database extras
# sqlalchemy>=2.0  # Optional for Phase 3 ORM layer

# Utilities
python-dateutil>=2.8.0
```

---

### 2.3 `Fase 1.md` na raiz — limpeza

**Problema:** É um dump de conversa de chat que não pertence ao código.  
**Correção:** Mover conteúdo útil para `docs/decisions-phase2.md` e apagar o ficheiro original.

---

### 2.4 `NZDUSD` hardcoded

**Problema:** README, exemplos e engines referem NZDUSD como único par. O projeto é EURUSD, USDJPY, USDCAD + índices.

**Correção — criar `config/assets.yaml`:**

```yaml
# config/assets.yaml
# Active assets for Trade-CLI analysis

forex:
  primary:
    - symbol: EURUSD
      description: Euro / US Dollar
      session_priority: [london, new_york, overlap]
      typical_spread_pips: 0.8
      correlation_group: usd_major

    - symbol: USDJPY
      description: US Dollar / Japanese Yen
      session_priority: [tokyo, london, new_york]
      typical_spread_pips: 1.0
      correlation_group: usd_major

    - symbol: USDCAD
      description: US Dollar / Canadian Dollar
      session_priority: [new_york]
      typical_spread_pips: 1.2
      correlation_group: usd_commodity

  secondary: []

indices:
  primary:
    - symbol: US30
      description: Dow Jones Industrial Average
      session_priority: [new_york]
      correlation_group: us_equity

    - symbol: NAS100
      description: NASDAQ 100
      session_priority: [new_york]
      correlation_group: us_equity

  secondary: []

timeframes:
  context: [D1, H4]
  execution: [H1, M15]
  scalping: [M5, M1]
  primary_analysis: H1
```

---

## 3. O que falta construir — Fase 2

### 3.1 Data Plane (MT5 + Market Data)

**O que falta:**

```
data/
├── __init__.py
├── mt5_client.py        # Wrapper do MetaTrader5 Python package
├── market_data.py       # Abstração de bars, ticks, book
├── calendar_client.py   # Calendário económico (ForexFactory API ou scraping)
├── news_client.py       # Headlines macro
└── mock_data.py         # Dados de teste (mover lógica mock dos engines para cá)
```

**`data/mt5_client.py` — estrutura mínima:**

```python
"""
MT5 Data Client — Trade-CLI Phase 2
Wraps MetaTrader5 Python package for bars, ticks, book, account state.
"""
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from typing import Optional

class MT5Client:
    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self._connected = False

    def connect(self) -> bool:
        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            return False
        self._connected = True
        return True

    def disconnect(self):
        mt5.shutdown()
        self._connected = False

    def get_bars(self, symbol: str, timeframe: int, count: int = 500) -> pd.DataFrame:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        return pd.DataFrame(rates)

    def get_ticks(self, symbol: str, count: int = 1000) -> pd.DataFrame:
        ticks = mt5.copy_ticks_from(symbol, datetime.utcnow(), count, mt5.COPY_TICKS_ALL)
        return pd.DataFrame(ticks)

    def get_spread(self, symbol: str) -> float:
        info = mt5.symbol_info(symbol)
        return info.spread / (10 ** info.digits) if info else 0.0

    def get_account_state(self) -> dict:
        acc = mt5.account_info()
        return {
            "balance": acc.balance,
            "equity": acc.equity,
            "profit": acc.profit,
            "margin": acc.margin,
            "margin_free": acc.margin_free,
            "drawdown_pct": ((acc.balance - acc.equity) / acc.balance * 100) if acc.balance > 0 else 0
        }
```

---

### 3.2 Engines em falta

**Engines existentes:** `technical`, `price_action`, `fundamental`  
**Engines a criar para Fase 2:**

```
engines/
├── __init__.py          ✅ ThesisEngine
├── technical.py         ✅ (precisa dados reais)
├── price_action.py      ✅ (precisa dados reais)
├── fundamental.py       ✅ (precisa dados reais)
├── sentiment.py         ❌ CRIAR
├── intermarket.py       ❌ CRIAR
├── volume.py            ❌ CRIAR
├── microstructure.py    ❌ CRIAR (Phase 2)
├── wyckoff.py           ❌ CRIAR (Phase 3)
└── ict_smc.py           ❌ CRIAR (Phase 3)
```

**Contrato obrigatório de cada engine (output):**

```python
EngineOutput(
    engine_name="sentiment",       # nome único
    score=0.0,                     # 0.0 a 1.0
    explanation="...",             # 1-2 frases
    evidence={                     # dados usados
        "key": "value"
    },
    conflict_with_other=False,
    conflict_description=""
)
```

---

### 3.3 Orquestrador LLM (Gemma / Haiku)

**O que falta criar:**

```
orchestrator/
├── __init__.py
├── llm_client.py        # Abstração: Gemma local (Ollama) ou Claude (API)
├── orchestrator.py      # Decide quais engines acionar, sintetiza debate
├── tool_registry.py     # Mapeia tools disponíveis ao LLM
├── visual_engine.py     # Analisa screenshots com modelo multimodal
└── context_builder.py   # Monta o contexto do prompt com memória + engines
```

**`orchestrator/llm_client.py` — estrutura:**

```python
"""
LLM Client — suporta Claude Haiku (API) e Gemma local (Ollama)
"""
import os
import anthropic
from typing import Optional

class LLMClient:
    def __init__(self, backend: str = "claude"):
        self.backend = backend  # "claude" | "gemma"
        if backend == "claude":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-haiku-4-5"
        # Future: Ollama client for local Gemma

    def chat(self, system: str, user: str, tools: list = None) -> str:
        if self.backend == "claude":
            msg = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": user}],
                tools=tools or []
            )
            return msg.content[0].text
        raise NotImplementedError(f"Backend {self.backend} not implemented")
```

---

### 3.4 Sistema de treino (Knowledge Feeding)

Esta é uma das partes mais importantes. "Treinar" neste projeto não é fine-tuning do modelo — é **alimentar a base de conhecimento** com materiais curados que ficam disponíveis via RAG, Obsidian e banco de dados.

**O que criar:**

```
training/
├── __init__.py
├── ingest.py            # Lê PDFs, Markdown, TXTs e normaliza
├── chunker.py           # Divide em chunks semânticos
├── tagger.py            # Aplica tags automáticas (symbol, method, timeframe)
├── kb_writer.py         # Grava no SQLite knowledge_base + Obsidian
└── review_feeder.py     # Processa diário externo e pós-análises
```

**Comando CLI para treino:**

```bash
# Alimentar com PDF de trading
python main.py train --file "ict-concepts.pdf" --topic "ict" --confidence high

# Alimentar com journal de outro trader
python main.py train --file "journal-2024.md" --topic "journal" --symbol EURUSD

# Alimentar com post-mortem manual
python main.py train --from-postmortem "post-mortems/2026-04-30-EURUSD.md"

# Ver o que está na base de conhecimento
python main.py knowledge list --topic wyckoff
python main.py knowledge search "order block EURUSD"
```

**Schema da tabela `knowledge_base` (expandido):**

```sql
CREATE TABLE knowledge_base (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,     -- 'concept', 'rule', 'playbook', 'journal_entry', 'postmortem'
    topic TEXT,                      -- 'ict', 'smc', 'wyckoff', 'price_action', 'fundamental'
    symbol TEXT,                     -- NULL = applies to all
    timeframe TEXT,
    confidence_level TEXT,           -- 'high', 'medium', 'low'
    source TEXT,                     -- filename, URL, or 'manual'
    tags TEXT,                       -- JSON array
    created_at TEXT,
    updated_at TEXT,
    review_status TEXT DEFAULT 'active'  -- 'active', 'deprecated', 'review_needed'
);
```

---

## 4. Obsidian + Graphify — setup completo

### 4.1 Porquê Graphify importa aqui

O Graphify (plugin de visualização de grafo avançado no Obsidian) transforma as ligações entre notas em mapas de conhecimento. Para o projeto funcionar bem, **cada nota precisa de links explícitos** entre ativos, teses, playbooks e post-mortems. Sem links, o grafo fica inútil.

**Regra de ouro:** toda nota no vault deve referenciar pelo menos uma outra nota via `[[link]]`.

---

### 4.2 Estrutura completa do Vault (com Graphify em mente)

```
Trade-CLI-Vault/
├── 00-meta/
│   ├── index.md                     ✅ Hub central — links para tudo
│   ├── template-thesis.md           ✅ Melhorar (ver abaixo)
│   ├── template-postmortem.md       ✅ OK
│   ├── template-playbook.md         ✅ OK
│   ├── template-daily-context.md    ✅ OK
│   ├── template-training-note.md    ❌ CRIAR — para alimentação de conhecimento
│   └── template-asset-hub.md        ❌ CRIAR — hub por ativo
│
├── ativos/
│   ├── EURUSD.md                    ❌ CRIAR
│   ├── USDJPY.md                    ❌ CRIAR
│   ├── USDCAD.md                    ❌ CRIAR
│   ├── US30.md                      ❌ CRIAR
│   └── NAS100.md                    ❌ CRIAR
│
├── metodos/                         ❌ CRIAR PASTA
│   ├── ICT.md                       ❌ Hub ICT
│   ├── SMC.md                       ❌ Hub SMC
│   ├── Wyckoff.md                   ❌ Hub Wyckoff
│   ├── price-action.md              ❌ Hub Price Action
│   ├── volume-profile.md            ❌ Hub Volume/Market Profile
│   └── fundamental.md               ❌ Hub Análise Fundamental
│
├── conceitos/                       ❌ CRIAR PASTA
│   ├── order-block.md               ❌ Conceito com links para teses
│   ├── fair-value-gap.md            ❌
│   ├── liquidity-sweep.md           ❌
│   ├── displacement.md              ❌
│   ├── market-structure-shift.md    ❌
│   ├── accumulation.md              ❌ (Wyckoff)
│   └── killzone.md                  ❌
│
├── teses/
│   └── [YYYY-MM-DD]-[SYMBOL]-[TF].md
│
├── post-mortems/
│   └── [YYYY-MM-DD]-[SYMBOL]-[resultado].md
│
├── playbooks/
│   └── [nome-do-setup].md
│
├── sessions/
│   └── [YYYY-MM-DD]-session.md
│
├── prop-firm/
│   ├── FTMO-rules.md                ✅ (verificar se existe)
│   ├── drawdown-tracker.md          ❌ CRIAR
│   └── consistency-log.md           ❌ CRIAR
│
├── treino/                          ❌ CRIAR PASTA
│   ├── livros/
│   ├── videos-resumos/
│   ├── journals-externos/
│   └── estudos-de-caso/
│
└── revisoes/                        ❌ CRIAR PASTA
    ├── semanal/
    └── mensal/
```

---

### 4.3 Template de nota de treino (para alimentar conhecimento)

**`Trade-CLI-Vault/00-meta/template-training-note.md`:**

```markdown
---
type: training-note
topic: {{topic}}
subtopic: {{subtopic}}
symbol: {{symbol_or_all}}
timeframe: {{timeframe_or_all}}
source: {{source}}
confidence: {{high|medium|low}}
status: active
created: {{date}}
tags: [{{tags}}]
related: [{{related_notes}}]
---

# {{title}}

## Contexto
{{Onde este conhecimento se aplica}}

## Conceito Principal
{{Explicação clara e direta}}

## Condições de Aplicação
- Quando usar: {{condição}}
- Quando NÃO usar: {{condição}}
- Timeframe ideal: {{TF}}
- Símbolo(s): {{symbols}}

## Exemplos
### Exemplo 1: {{breve descrição}}
{{screenshot ou descrição}}
- Resultado: {{o que aconteceu}}
- Lição: {{o que aprender}}

## Ligações
- Método: [[metodos/{{metodo}}]]
- Conceito relacionado: [[conceitos/{{conceito}}]]
- Tese exemplo: [[teses/{{tese}}]]
- Playbook gerado: [[playbooks/{{playbook}}]]

## Score de Confiança no Conhecimento
- Origem: {{livro/video/experiencia}}
- Testado em: {{sim/nao/parcial}}
- Revisão necessária: {{sim/nao}}
```

---

### 4.4 Template de hub por ativo (para Graphify)

**`Trade-CLI-Vault/00-meta/template-asset-hub.md`:**

```markdown
---
type: asset-hub
symbol: {{SYMBOL}}
created: {{date}}
tags: [forex, {{symbol}}, hub]
---

# {{SYMBOL}} — Hub

## Visão Geral
- Par: {{SYMBOL}}
- Grupo: {{usd_major|commodity|index}}
- Sessão principal: {{london|tokyo|new_york}}
- Correlações principais: [[ativos/{{corr1}}]] [[ativos/{{corr2}}]]

## Contexto Macro Atual
> Atualizar semanalmente
- Viés macro: {{bullish/bearish/neutro}}
- Evento próximo: {{evento + data}}
- Tendência D1/H4: {{descrição}}

## Playbooks Ativos
- [[playbooks/{{playbook1}}]]
- [[playbooks/{{playbook2}}]]

## Teses Recentes
- [[teses/{{tese1}}]]
- [[teses/{{tese2}}]]

## Post-mortems
- [[post-mortems/{{pm1}}]]

## Notas de Comportamento
{{Observações sobre o comportamento típico deste ativo}}

## Estatísticas (actualizar com CLI)
- Análises totais: {{n}}
- ALLOWED: {{n}} | WATCH_ONLY: {{n}} | BLOCKED: {{n}}
- Taxa acerto teses: {{%}}
```

---

### 4.5 Melhorias no template de tese existente

**Adicionar ao `template-thesis.md`:**

```markdown
---
type: thesis
symbol: {{SYMBOL}}
timeframe: {{TF}}
bias: {{bullish|bearish|neutral|fragile}}
setup_type: {{setup}}
confidence: {{0-100}}
alignment: {{0-100}}
verdict: {{ALLOWED|WATCH_ONLY|BLOCKED}}
session: {{london|tokyo|new_york|overlap}}
created: {{datetime}}
tags: [{{symbol}}, {{bias}}, {{setup_type}}, {{session}}]
related_methods: [[[metodos/ICT]], [[metodos/SMC]]]
asset_hub: [[ativos/{{SYMBOL}}]]
---

## Links Graphify
- Método: [[metodos/{{metodo_principal}}]]
- Conceito: [[conceitos/{{conceito_principal}}]]
- Playbook: [[playbooks/{{playbook_se_existir}}]]
- Ativo: [[ativos/{{SYMBOL}}]]
```

---

## 5. Template para GitHub Copilot CLI (CLAUDE.md / copilot-instructions)

Cria este ficheiro na raiz do repositório. O Copilot CLI com Claude Haiku usa ele como contexto permanente.

**`.github/copilot-instructions.md`** OU **`CLAUDE.md`** na raiz:

```markdown
# Trade-CLI — Copilot/Claude Instructions

## Project Identity
Trade-CLI is a LOCAL AI analytical copilot for Forex trading decisions.
It NEVER executes real trades. Its sole purpose is analysis, knowledge management, and decision support.

## Architecture Rules (NON-NEGOTIABLE)
1. `RiskGuardian` is ALWAYS the final decision layer — it can only be bypassed by explicit test mode
2. Every engine MUST return `EngineOutput` with: score (0-1), explanation, evidence dict
3. LLM orchestrator NEVER replaces engine calculations — it synthesizes and explains
4. Obsidian Vault is human-readable knowledge — SQLite is structured event log
5. No real MT5 orders — only data reading and state queries

## Current Phase: Transitioning Phase 1 → Phase 2
- Phase 1 (DONE): Schema, RiskGuardian, mock engines, CLI, vault structure
- Phase 2 (ACTIVE): MT5 data integration, real engines, LLM orchestrator
- Phase 3 (FUTURE): TradingView webhooks, advanced engines (Wyckoff, ICT, SMC)

## Code Standards
- Python 3.11+
- Type hints REQUIRED on all functions
- Dataclasses for all data structures (see `core/analysis_schema.py`)
- All engines inherit from base interface: `score`, `explanation`, `evidence`
- Tests go in `tests/test_*.py` — 100% coverage on core/ and engines/
- Never commit: database.db, .env, model files (.gguf, .bin), logs

## File Structure
```
core/          # Schema, RiskGuardian, Scoring — FROZEN Phase 1
engines/       # Analytical motors — Phase 2 integration in progress
data/          # MT5, news, calendar clients — Phase 2 NEW
orchestrator/  # LLM coordination — Phase 2 NEW
training/      # Knowledge ingestion — Phase 2 NEW
cli/           # Typer CLI interface
config/        # YAML config files (ftmo-rules, assets)
db/            # SQLite schema, migrations, models
docs/          # Architecture decisions (frozen for each phase)
Trade-CLI-Vault/ # Obsidian vault (Markdown knowledge base)
tests/         # Pytest coverage
```

## Primary Symbols (Phase 2 target)
- Forex: EURUSD, USDJPY, USDCAD
- Indices: US30, NAS100
- (NZDUSD is Phase 1 test only — replace in new work)

## Analysis Output Contract
Every analysis MUST produce `AnalysisOutput` with:
- symbol, timeframe, bias, setup_type
- confidence_score, alignment_score (0.0-1.0)
- invalidations[] — minimum 1 condition
- risk_notes[]
- verdict: ALLOWED | WATCH_ONLY | BLOCKED
- obsidian_link (auto-generated)

## Obsidian Vault Rules
- Every note MUST have frontmatter with: type, symbol, created, tags
- Every thesis MUST link to: [[ativos/SYMBOL]], [[metodos/METHOD]], [[conceitos/CONCEPT]]
- Post-mortems MUST link back to original thesis
- Training notes go in: treino/ with template-training-note.md

## Knowledge Base Philosophy
- Train with PROCESS, not just content
- Curated > Comprehensive (less noise = better retrieval)
- Every concept needs: when to use, when NOT to use, examples
- Tag schema: [symbol, method, timeframe, confidence_level, setup_type]

## Forbidden Actions
- Do NOT add GUI/web interface in Phase 2 (CLI first)
- Do NOT auto-save every chat message to Obsidian
- Do NOT commit database.db, .env, or model files
- Do NOT modify frozen schema in core/ without migration
- Do NOT hardcode credentials or API keys
- Do NOT open real MT5 orders (read-only in Phase 2)

## When Adding a New Engine
1. Create `engines/{name}.py`
2. Implement `analyze(symbol, timeframe, data) -> EngineOutput`
3. Add to `ThesisEngine` in `engines/__init__.py`
4. Add score field to `AnalysisOutput` in `core/analysis_schema.py`
5. Write tests in `tests/test_{name}_engine.py`
6. Document in `docs/engines/{name}.md`

## When Training the System
1. Run: `python main.py train --file FILE --topic TOPIC`
2. System chunks, tags, and saves to: SQLite knowledge_base + Obsidian treino/
3. Review generated notes before marking as 'active'
4. Link new concepts to existing [[metodos/]] and [[ativos/]] notes
5. Run: `python main.py knowledge list` to verify ingestion

## LLM Backend Priority
1. Local Gemma via Ollama (preferred — privacy, no cost)
2. Claude Haiku 4.5 via API (fallback — set ANTHROPIC_API_KEY in .env)
3. Never use cloud LLM for live trading context without explicit opt-in
```

---

## 6. Sistema de treino — fluxo completo

### 6.1 Tipos de conhecimento a alimentar

| Tipo | Fonte | Destino | Prioridade |
|---|---|---|---|
| Conceitos ICT/SMC | PDFs, vídeos transcritos | `treino/livros/` + `conceitos/` | Alta |
| Conceitos Wyckoff | PDFs | `treino/livros/` + `conceitos/` | Alta |
| Regras FTMO/Prop firm | Documentação oficial | `prop-firm/` + `knowledge_base` | Crítica |
| Journal de trading (teu) | CSV/Markdown | `journals/` + `knowledge_base` | Alta |
| Journal externo | Markdown | `treino/journals-externos/` | Média |
| Post-mortems teus | CLI output | `post-mortems/` + `analysis_outcomes` | Alta |
| Estudos de caso | Manual | `treino/estudos-de-caso/` | Média |
| Comportamento de ativo | Observação | `ativos/SYMBOL.md` | Alta |

---

### 6.2 Fluxo de treino recomendado

```
1. INGERIR
   python main.py train --file "material.pdf" --topic "ict"
   └── chunks semânticos
   └── tags automáticas
   └── salva em SQLite knowledge_base
   └── cria nota em Trade-CLI-Vault/treino/

2. REVISAR
   Abre Obsidian → pasta treino/
   Verifica cada nota gerada
   Adiciona links manuais: [[metodos/ICT]] [[conceitos/order-block]]
   Marca como reviewed: status: reviewed

3. ATIVAR
   python main.py knowledge activate --id NOTE_ID
   └── muda review_status para 'active'
   └── disponível para RAG e orquestrador

4. USAR
   python main.py analyze EURUSD H1
   └── orquestrador consulta knowledge_base relevante
   └── engines usam conceitos ativos
   └── tese gerada com base no contexto vivo

5. APRENDER
   python main.py outcome --analysis-id ID --result "invalidated|correct" --notes "..."
   └── grava em analysis_outcomes
   └── gera post-mortem draft em Obsidian
   └── atualiza playbook se padrão repetido
```

---

### 6.3 Primeiro material a alimentar (sugestão)

1. As regras da tua prop firm (FTMO ou outra) em formato Markdown
2. Um resumo dos conceitos ICT que usas (Killzones, FVG, Order Blocks, MSS)
3. Um resumo dos conceitos SMC que usas
4. Estrutura básica de Wyckoff (acumulação, distribuição, esforço vs resultado)
5. O teu próprio plano de trading (se tiveres)
6. Qualquer journal ou diário de trades anteriores

---

## 7. Novos comandos CLI a adicionar

```bash
# Treino
python main.py train --file FILE [--topic TOPIC] [--symbol SYMBOL] [--confidence high|medium|low]
python main.py train --text "Texto direto" --topic "ict"

# Base de conhecimento
python main.py knowledge list [--topic TOPIC] [--symbol SYMBOL]
python main.py knowledge search "query aqui"
python main.py knowledge show ID
python main.py knowledge activate ID
python main.py knowledge deprecate ID

# Ativos
python main.py assets list
python main.py assets hub EURUSD    # Gera/atualiza hub no Obsidian

# Outcomes (pós-análise)
python main.py outcome --analysis-id ID --result correct|incorrect|invalidated --notes "texto"

# Revisão
python main.py review weekly        # Resumo semanal das análises
python main.py review stats         # Métricas gerais

# Análise com pares corretos
python main.py analyze EURUSD H1
python main.py analyze USDJPY M15
python main.py analyze US30 H1
```

---

## 8. Melhorias no schema existente

### 8.1 `AnalysisOutput` — campos a adicionar (Phase 2)

```python
# Adicionar ao dataclass AnalysisOutput em core/analysis_schema.py

# Engine scores Phase 2
sentiment_score: float = 0.0
intermarket_score: float = 0.0
volume_score: float = 0.0
microstructure_score: float = 0.0

# Context
session: str = ""               # "london", "tokyo", "new_york", "overlap"
market_regime: str = ""         # "trending", "ranging", "volatile", "calm"
macro_risk: str = ""            # "high", "medium", "low"

# Source tracking
data_source: str = "mock"       # "mt5", "mock", "manual"
llm_used: bool = False
llm_model: str = ""

# Graphify links (Obsidian)
method_links: List[str] = field(default_factory=list)   # [[metodos/ICT]]
concept_links: List[str] = field(default_factory=list)  # [[conceitos/order-block]]
```

---

### 8.2 `db_schema.sql` — tabelas a adicionar

```sql
-- Sessão de análise agrupada (para multi-timeframe)
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    session_type TEXT,          -- 'pre_trade', 'educational', 'review'
    analysis_ids TEXT,          -- JSON array of analysis IDs
    summary TEXT,
    created_at TEXT
);

-- Base de conhecimento expandida
CREATE TABLE IF NOT EXISTS knowledge_base (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,
    topic TEXT,
    symbol TEXT,
    timeframe TEXT,
    confidence_level TEXT DEFAULT 'medium',
    source TEXT,
    tags TEXT,                  -- JSON array
    review_status TEXT DEFAULT 'pending',
    created_at TEXT,
    updated_at TEXT
);

-- Revisões periódicas
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    review_type TEXT,           -- 'weekly', 'monthly'
    period_start TEXT,
    period_end TEXT,
    total_analyses INTEGER,
    allowed_count INTEGER,
    blocked_count INTEGER,
    watch_count INTEGER,
    correct_theses INTEGER,
    incorrect_theses INTEGER,
    key_learnings TEXT,         -- JSON array
    obsidian_link TEXT,
    created_at TEXT
);
```

---

## 9. Checklist de commit para Fase 2

Antes de fazer commit de Fase 2, verificar:

- [ ] `.gitignore` cobre database.db, .env, models/, logs
- [ ] `requirements.txt` inclui todas as dependências necessárias
- [ ] `config/assets.yaml` criado com EURUSD, USDJPY, USDCAD, US30
- [ ] `CLAUDE.md` ou `.github/copilot-instructions.md` criado
- [ ] `Trade-CLI-Vault/ativos/` tem hubs para todos os pares activos
- [ ] `Trade-CLI-Vault/metodos/` criado com hubs ICT, SMC, Wyckoff
- [ ] `Trade-CLI-Vault/conceitos/` criado com conceitos-chave
- [ ] `Trade-CLI-Vault/treino/` criado
- [ ] `Trade-CLI-Vault/revisoes/` criado
- [ ] Template `template-training-note.md` criado
- [ ] Template `template-asset-hub.md` criado
- [ ] Todos os templates têm frontmatter com campos para Graphify
- [ ] `data/mt5_client.py` criado (mesmo que mock ainda)
- [ ] `training/ingest.py` criado
- [ ] Novos comandos CLI: `train`, `knowledge`, `outcome`, `review`
- [ ] `docs/decisions-phase2.md` documenta decisões desta fase
- [ ] `Fase 1.md` removido da raiz
- [ ] Todos os testes passam (`pytest tests/ -v`)
- [ ] `python main.py health` passa sem erros
- [ ] `python main.py analyze EURUSD M15 --test` funciona

---

## 10. Ordem de execução recomendada

1. Aplicar `.gitignore` e remover `database.db` do tracking
2. Atualizar `requirements.txt`
3. Criar `CLAUDE.md` na raiz
4. Criar `config/assets.yaml`
5. Criar estrutura de pastas no Vault (metodos, conceitos, treino, revisoes)
6. Criar templates em falta (training-note, asset-hub)
7. Criar hubs de ativos (EURUSD, USDJPY, USDCAD, US30, NAS100)
8. Criar hubs de métodos (ICT, SMC, Wyckoff, price-action)
9. Criar `data/mt5_client.py` com mock mode
10. Criar `training/ingest.py` básico
11. Adicionar comandos `train`, `knowledge`, `outcome` ao CLI
12. Actualizar `AnalysisOutput` com novos campos
13. Adicionar tabelas ao `db_schema.sql`
14. Documentar em `docs/decisions-phase2.md`

---

> **Lembrete de contexto permanente:**  
> Este ficheiro + `CLAUDE.md` + `docs/decisions-phase2.md` são os três documentos  
> que garantem que qualquer sessão de trabalho (com IA ou humano) começa alinhada  
> com o estado real do projeto. Mantê-los actualizados é mais importante do que  
> qualquer feature individual.
