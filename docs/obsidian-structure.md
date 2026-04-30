# Obsidian Vault Structure - Trade-CLI

## Overview

A memória curada do sistema Trade-CLI é guardada em Obsidian com uma estrutura clara e navegável. Esta documentação descreve a taxonomia, propósito e ligações entre pastas.

**Princípio:** Obsidian nunca é um "despejo" de chats/logs; é memória pensada e reutilizável.

---

## Estrutura Principal

```
Trade-CLI-Vault/
├── 00-meta/                 # Configuração e documentação do vault
├── ativos/                  # Hub de pares/índices
├── teses/                   # Análises individuais (uma tese = uma nota)
├── post-mortems/            # Comparação tese vs resultado + lições
├── playbooks/               # Padrões reaplicáveis e regras
├── sessions/                # Contexto macro diário/semanal
└── prop-firm/               # Regras e documentação FTMO
```

---

## Detalhes por Pasta

### 📁 `00-meta/` — Metadados e Configuração

**Propósito:** Documentação do próprio vault.

**Ficheiros obrigatórios:**
- `index.md` — visão geral do vault e como navegar
- `decisions.md` — decisões arquiteturais da Fase 1 (frozen para referência)
- `methodology.md` — como se usa este sistema
- `templates-guide.md` — guia de uso para cada template

**Ficheiros de suporte:**
- `taxonomy.md` — glossário de termos (bias, setup_type, verdict, etc.)
- `.obsidian/` — configurações locais do Obsidian (auto-gerado)

**Relações:** 
- Links de entrada para todo o vault (hub central)
- Referências cruzadas a playbooks e regras FTMO

---

### 📁 `ativos/` — Pares e Índices

**Propósito:** Hub consolidado por ativo (NZDUSD, EURUSD, etc.). Uma nota por par.

**Estrutura de nota (exemplo: NZDUSD.md):**
```markdown
# NZDUSD

## Visão Consolidada
- Pares correlados: ...
- Características: ...
- Histórico de análises neste par

## Análises Recentes
- Links para 5-10 teses mais recentes

## Playbooks Aplicáveis
- Links para playbooks que aplicam a NZDUSD

## Post-mortems
- Sumário de erros e acertos neste par

## Regras Específicas
- Qual timeframe é "home timeframe"
- Qual timeframe é "confirmation timeframe"
```

**Ficheiros padrão:**
- `NZDUSD.md` (ou EURUSD, USDCAD, etc.)
- `indices/` (subpasta para índices: SPX, DXY, etc.)
- `index.md` — índice de todos os ativos monitorados

**Relações:**
- Referenciada em cada tese (backlink automático)
- Links para playbooks por par
- Links para post-mortems daquele ativo

---

### 📁 `teses/` — Análises Individuais

**Propósito:** Uma tese = uma análise completa de um setup em um ativo/timeframe.

**Convenção de nome:**
```
YYYY-MM-DD-SYMBOL-TF-DESCRIPTION.md
Exemplo: 2025-04-30-NZDUSD-M15-liquidty-sweep-recovery.md
```

**Estrutura de nota (template):**
```markdown
---
date: 2025-04-30
symbol: NZDUSD
timeframe: M15
setup_type: liquidity_sweep_reclaim
confidence: 0.68
analyst: Manual
---

# Tese: [Setup Type] em [Symbol] [Timeframe]

## Contexto
- Timeframe superior (H1): [descrição]
- Timeframe atual (M15): [descrição]
- Intermarket: [correlatos relevantes]

## Viés Principal
- **Bias:** bullish_but_fragile
- **Setup:** Liquidty sweep + reclaim
- **Alignment Score:** 61% (3.5/5 motores)

## Análise por Motor
### Técnico
- Suporte/Resistência: ...
- Score: 0.70

### Price Action
- Padrão observado: ...
- Score: 0.55

### Fundamental
- Contexto macro: ...
- Score: 0.65

## Tese Alternativa
- Cenário bearish se...

## Invalidação
- Close abaixo de X
- Evento de notícia nas próximas 2h

## Observações de Risco
- Spread elevado
- USD mix em intermarket

## Verdict
- **Resultado:** watch_only (não operar ainda)
- **Razão:** Confluência baixa

## Follow-up
- Revisar em 30 minutos se...
- Post-mortem: [[data-resultado]]
```

**Relações:**
- Backlinks automáticos para [[NZDUSD]] (asset hub)
- Backlinks para [[playbook-name]] se baseada em padrão
- Link para [[post-mortem-resultado]] quando trade fechar

**Meta:**
- Buscar por symbol: `tag:#NZDUSD`
- Buscar por setup: `tag:#liquidity_sweep`
- Buscar por resultado: `tag:#watch_only`

---

### 📁 `post-mortems/` — Análise de Resultados

**Propósito:** Comparação tese vs resultado real + lições aprendidas.

**Convenção de nome:**
```
YYYY-MM-DD-SYMBOL-TF-POSTMORTEM.md
Exemplo: 2025-04-30-NZDUSD-M15-postmortem.md
```

**Estrutura de nota:**
```markdown
---
date: 2025-04-30
symbol: NZDUSD
timeframe: M15
related_thesis: [[2025-04-30-NZDUSD-M15-liquidty-sweep-recovery]]
outcome: watch_only_avoided_loss
---

# Post-Mortem: [Symbol] [Timeframe]

## O que foi proposto
- Tese original: [[link tese]]
- Verdict: watch_only
- Setup proposto: ...

## O que realmente aconteceu
- Preço foi para: ...
- Invalidação ocorreu: Sim/Não
- Resultado para trader: +/- X pips

## Análise de Erro / Acerto
- Motor técnico: acertou/errou (explicar)
- Motor price action: ...
- Motor fundamental: ...

## Lições Aprendidas
1. Qual assunção falhou?
2. Qual motor foi misleading?
3. Qual regra deveria bloquear isto?

## Atualização de Playbooks
- Playbook X precisa ajuste em ...
- Novo padrão observado: ...

## Tags de Review
- confidence_was_low ✓
- motor_consensus_poor ✓
- avoided_correctly ✓
```

**Relações:**
- Link para tese original (backlink)
- Link para ativo [[NZDUSD]]
- Link para playbook afetado

---

### 📁 `playbooks/` — Padrões Reutilizáveis

**Propósito:** Regras, checklists e padrões reaplicáveis.

**Tipos de ficheiros:**

#### 1. Playbooks por Setup
```
Exemplo: liquidity-sweep-reclaim.md
```

**Estrutura:**
```markdown
# Playbook: Liquidity Sweep & Reclaim

## O que é
- Definição clara
- Visual reference (screenshot ou descrição)

## Setup Mínimo
- Condição 1: ...
- Condição 2: ...
- Condição 3: ...

## Checklist Operacional
- [ ] Higher timeframe bias alinhado
- [ ] Liquidty zone identificada
- [ ] Price action confirma sweep
- [ ] Entrada definida

## Risk Management
- Stop: X pips
- Target 1/2/3: ...
- RRR mínimo: 1:2

## Exemplos Históricos
- [[2025-04-20-EURUSD-M15-success]]
- [[2025-04-25-NZDUSD-H1-failure]]

## Notas
- Melhor timeframe: M15, H1
- Pares que fundem bem: NZDUSD, EURUSD
- Evitar em: News catalyst, wide spreads
```

#### 2. Playbooks por Ativo
```
Exemplo: nzdusd-characteristics.md
```

**Estrutura:**
```markdown
# Playbook: Trading NZDUSD

## Características do Par
- Volatilidade: ...
- Spread típico: ...
- Correlatos: NZD indices, ...

## Setups que Fundem Bem
- [[liquidity-sweep-reclaim]]
- [[pullback-continuation]]

## Horários Ótimos
- Sessão Tokyo: ...
- Sessão London: ...
- Sessão New York: ...

## Erros Comuns
- [[mistake-wide-spread-entry]]
- [[mistake-overshoot-liquidty]]

## Nota Técnica
- Home timeframe: H1
- Confirmation: M15
- Entry: M5
```

**Relações:**
- Backlinks para teses que aplicam este playbook
- Links para ativos [[NZDUSD]]
- Links para erros recorrentes

---

### 📁 `sessions/` — Contexto Macro Diário

**Propósito:** Snapshot de contexto antes de operar.

**Convenção de nome:**
```
daily-context-YYYY-MM-DD.md
Exemplo: daily-context-2025-04-30.md
```

**Estrutura:**
```markdown
---
date: 2025-04-30
session: Asia-London-NY
volatility: medium
---

# Contexto Diário — 2025-04-30

## Macro
- Eventos esperados: ...
- Fed/ECB: ...
- Inflação, emprego, etc.: ...

## Sentimento de Mercado
- Risk sentiment: on/off
- Positioning: ...
- Consensus: ...

## Intermarket
- DXY: direction + strength
- Equities: SPX, ... direction
- Yields: DXY/JPY, ...

## Próximas 24h
- Janelas de risco: ...
- Setup probável: ...

## Recomendação
- Trade com cuidado se...
- Evitar se...

## Follow-up
- Post-trade summary: (preenchido depois)
```

**Relações:**
- Tags: `#session #NZDUSD` (para filtro)
- Links para teses do dia
- Links para post-mortems do dia

---

### 📁 `prop-firm/` — Regras e Governança FTMO

**Propósito:** Documentação de regras FTMO (frozen para referência).

**Ficheiros obrigatórios:**

#### `ftmo-rules.md`
```markdown
# Regras FTMO

(Versão: Fase 1, Data: 2025-04-30)

## Drawdown
- Daily: 5% máximo
- Total: 10% máximo

## Risco por Trade
- 0.5% — 1.0% do saldo (strict)

## Bloqueios
- News alta: ±15 min blackout
- Correlação > 0.7: bloqueia 2º par

## Qualidade
- Confluence < 50%: watch_only
- Confidence < 0.5: bloqueia

(Completo em config/ftmo-rules.yaml)
```

#### `risk-guardian.md`
```markdown
# Como o RiskGuardian Funciona

1. Recebe análise com scores
2. Aplica regras FTMO
3. Retorna: allowed / watch_only / blocked

Exemplos:
- Confluence 65%, Confidence 0.75 → allowed
- Confluence 45%, Confidence 0.6 → watch_only
- Drawdown 6% → blocked
```

**Relações:**
- Links para config/ftmo-rules.yaml (source of truth)
- Links para teses vetadas

---

## Ligações e Backlinks

### Exemplo de Fluxo:
1. Sessão diária [[daily-context-2025-04-30]] monta contexto
2. Trader identifica setup em [[NZDUSD]]
3. Consulta playbook [[liquidity-sweep-reclaim]]
4. Cria tese [[2025-04-30-NZDUSD-M15-liquidty-sweep-recovery]]
5. RiskGuardian valida (regras em [[prop-firm/ftmo-rules]])
6. Se trade: operação, depois [[post-mortem]] registra resultado
7. Lições atualizadas em [[playbook]] ou [[mistakes/]]

### Tags Usadas:
- `#NZDUSD`, `#EURUSD` — por par
- `#liquidity_sweep`, `#pullback` — por setup
- `#allowed`, `#watch_only`, `#blocked` — por verdict
- `#success`, `#failure` — por resultado

---

## Workflow de Criação de Notas

### 1. Nota de Tese
```bash
# Antes de analisar
1. Cria nota com template: teses/YYYY-MM-DD-SYMBOL-TF-DESCRIPTION.md
2. Preenche: Contexto, motores, tese, invalidação
3. RiskGuardian valida (offline)
4. Tags: #symbol #setup_type #verdict
```

### 2. Nota de Post-Mortem
```bash
# Após trade/análise
1. Cria nota: post-mortems/YYYY-MM-DD-SYMBOL-TF-POSTMORTEM.md
2. Compara tese original vs resultado
3. Documenta lições
4. Backlink para tese original
5. Atualiza playbook se necessário
```

### 3. Nota de Playbook
```bash
# Após 3+ casos do mesmo padrão
1. Se padrão se repete, codifica em: playbooks/PATTERN-NAME.md
2. Documenta: O que é, checklist, RRR, exemplos
3. Links históricos para teses deste padrão
4. Review e versioning
```

---

## Buscas Úteis no Obsidian

```
# Tudo NZDUSD da última semana
tag:#NZDUSD

# Setups de liquidity sweep
tag:#liquidity_sweep

# Teses vetadas
tag:#blocked

# Todas as teses de sucesso
tag:#success

# Post-mortems de failure
tag:#failure

# Teses em watch_only
tag:#watch_only
```

---

## Snapshot Visual (ASCII)

```
┌─────────────────────────────────────────┐
│        00-meta (Configuração)           │
│  - index.md (nav hub)                   │
│  - decisions.md                         │
│  - methodology.md                       │
└─────────┬───────────────────────────────┘
          │
    ┌─────┴──────┬─────────┬──────────┬────────┬──────────┐
    │             │         │          │        │          │
 ┌──▼───┐  ┌──────▼──┐ ┌────▼────┐ ┌──▼─────┐ ┌▼────────┐┌───▼──────┐
 │ativos│  │  teses  │ │post-mort│ │playbook││ sessions││prop-firm │
 │------│  │---------│ │---------│ │--------││ --------││----------│
 │NZDUSD│  │YYYY-MM- │ │YYYY-MM- │ │setup-* ││daily-   ││ftmo-rules│
 │EURUSD│  │DD-SYM-TF│ │DD-SYM-PM│ │pattern ││context  ││          │
 │...   │  │...      │ │...      │ │ativo-* ││...      ││risk-...  │
 └──────┘  └─────────┘ └─────────┘ └────────┘└─────────┘└──────────┘
```

---

## Regras de Manuntenção

1. **Obsidian não é arquivo bruto:** Notas devem ser úteis e navegáveis
2. **Templates fixos:** Usar os templates definidos para consistência
3. **Links obrigatórios:** Cada tese liga-se a ativo + playbook (se aplicável)
4. **Cleanup mensal:** Remover teses muito antigas (guardar em archive)
5. **Review semanal:** Verificar post-mortems e atualizar playbooks com base em padrões

---

## Próximas Adições (Fase 2+)

- `micro-analysis/` — estudos profundos (price action patterns, volume profiles, etc.)
- `errors/` — base de erros recorrentes (evitar repetição)
- `research/` — artigos, estudos, conclusões sobre mercado
- `archive/` — teses antigas (guardadas para referência histórica)
