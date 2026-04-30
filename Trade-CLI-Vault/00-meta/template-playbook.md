---
name: {{PLAYBOOK_NAME}}
setup_type: {{SETUP_TYPE}}
symbols: {{SYMBOLS}}
timeframe_optimal: {{TIMEFRAMES}}
confidence: {{LEVEL}}
last_updated: {{DATE}}
tags: [playbook, {{SETUP_TYPE}}]
---

# Playbook: {{PLAYBOOK_NAME}}

## O que é?

**Definição:**
{{DESCRIPTION}}

**Visualização:** (ASCII sketch ou referência)
```
[Price action diagram]
```

---

## Setup Mínimo (Checklist)

Todas as condições abaixo devem ser verdadeiras:

- [ ] Condição 1: 
- [ ] Condição 2: 
- [ ] Condição 3: 
- [ ] Confirmação: 

**Se alguma faltar:** Não trade, espera setup melhor.

---

## Checklist Operacional

Antes de entrar:

- [ ] Higher timeframe confirma viés
- [ ] Entry ponto está claro
- [ ] Stop loss definido
- [ ] Target(s) definido(s)
- [ ] Risk/Reward >= 1:2
- [ ] Sem notícia próxima (15min)
- [ ] Spread normal
- [ ] Volume confirma (se aplicável)

**Se qualquer item faltar:** WATCH_ONLY, não opera.

---

## Risk Management

| Parâmetro | Valor | Notas |
|-----------|-------|-------|
| Stop Loss | XX pips | Abaixo do ponto crítico |
| Target 1 | XX pips | (Lucro rápido 1:1) |
| Target 2 | XX pips | (Lucro principal 1:2) |
| Target 3 | XX pips | (Lucro máximo 1:3+) |
| Min RRR | 1:2 | Nunca < isto |
| Max Risk % | 1.0% | FTMO rule |

---

## Timing

**Best Timeframe:**
- Primary: {{TIMEFRAME}}
- Confirmation: {{CONFIRMATION_TIMEFRAME}}
- Entry: {{ENTRY_TIMEFRAME}}

**Best Sessions:**
- Optimal: 
- Acceptable: 
- Avoid: 

**Spread Watch:**
- Typical: XX pips
- Max acceptable: XX pips
- If wider: watch_only

---

## Exemplos Históricos

### ✓ Sucesso
[[YYYY-MM-DD-SYMBOL-TF-success]]
- Setup foi clear
- Executado bem
- Hit target

### ✗ Failure
[[YYYY-MM-DD-SYMBOL-TF-failure]]
- Por que falhou
- Lição aprendida
- Proteção adicionada

---

## Variações e Armadilhas

**Variação 1: Setup mais agressivo**
- Quando usar: 
- Risco: 
- Reward: 

**Trap 1: False breakout**
- Como reconhecer: 
- Como evitar: 
- Stop loss: 

**Trap 2: Rejeitado depois de entry**
- Como reconhecer: 
- Saída rápida: 

---

## Pares que Fundem Bem

- {{SYMBOL1}} — Liquidez boa, setup claro
- {{SYMBOL2}} — Bom align, menos noise
- Evitar: {{SYMBOL3}} — spread wide, choppy

---

## Erros Comuns

- [ ] Entrar sem confirmação do HT (ignorar higher timeframe)
- [ ] Risk > 1% (ambição demais)
- [ ] Entrar durante notícia blackout
- [ ] Ignorar invalidação (seguir trade ruim)
- [ ] Sem target definido (sem plano)

**Proteção:** RiskGuardian bloqueia.

---

## Relacionados

**Playbooks similares:**
- [[playbook-similar-1]]
- [[playbook-similar-2]]

**Complementares:**
- [[risk-management-playbook]]
- [[session-playbook]]

**Erros a evitar:**
- [[mistake-false-breakout]]
- [[mistake-overtrading]]

---

## Review e Validação

**Confiança:** ✓✓✓✓☆ (4/5 stars)

**Testes:**
- [ ] Backtested (Y/N/Pending)
- [ ] Live traded (3+ times, Y/N)
- [ ] Win rate: X%
- [ ] Avg RRR: X

**Last reviewed:** YYYY-MM-DD
**Próxima review:** YYYY-MM-DD +30 dias

---

## Notas

- Melhor em trending markets (não em ranging)
- Adaptar para cada par (spread, volatility)
- Combinar com [[daily-context]] para melhor timing
