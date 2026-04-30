---
date: {{DATE}}
symbol: {{SYMBOL}}
timeframe: {{TIMEFRAME}}
related_thesis: [[{{THESIS_DATE}}-{{SYMBOL}}-{{TIMEFRAME}}-{{SETUP}}]]
outcome: {{OUTCOME_TYPE}}
tags: [{{SYMBOL}}, postmortem]
---

# Post-Mortem: {{SYMBOL}} {{TIMEFRAME}} — {{DATE}}

## Tese Original

Link: [[{{THESIS_LINK}}]]

**Que foi proposto:**
- Setup: {{SETUP_TYPE}}
- Viés: {{BIAS}}
- Verdict: {{ORIGINAL_VERDICT}}
- Confidence: {{ORIGINAL_CONFIDENCE}}
- Alignment: {{ORIGINAL_ALIGNMENT}}

---

## O Que Realmente Aconteceu

**Price Action:**
- Abriu em: 
- Foi para: 
- Fechou em: 
- Movimento total: XX pips

**Invalidação Ocorreu?**
- [ ] Sim — Qual? 
- [ ] Não — Setup continuou válido

**Resultado Operacional:**
- [ ] Trade foi feito (execute a tese)
- [ ] Trade NÃO foi feito (apenas observe em watch_only)

Se trade foi feito:
- Entry: 
- Stop Loss: 
- Target hit: 
- Resultado: +XX pips ou -XX pips
- Quality: 
  - [ ] Ideal (executou corretamente)
  - [ ] Acceptable (com slippage)
  - [ ] Poor (entrada ruim)

---

## Análise de Acertos e Erros

### Cada Motor Acertou?

| Motor | Previsão | Realidade | Acertou? | Notas |
|-------|----------|-----------|----------|-------|
| Técnico | | | ✓/✗ | |
| Price Action | | | ✓/✗ | |
| Fundamental | | | ✓/✗ | |

**Padrão observado:** Qual motor foi mais confiável nesta setup?

---

## Lições Aprendidas

### 1. Que Assunção Falhou?
(Se trade foi ruim)

Assumíamos: 
Realidade era: 
Por que erramos: 

### 2. Qual Motor foi Misleading?
(Se um motor deu signal errado)

Motor: 
Por que falhou: 
Melhorias futuras: 

### 3. Que Regra Deveria ter Bloqueado Isto?
(Se tivéssemos aplicado RiskGuardian mais rigorosamente)

Regra que faltou: 
Cenário: 
Proteção adicionada: 

---

## Atualização de Playbooks

**Playbook afetado:** [[playbook-name]]

**Mudanças necessárias:**
- [ ] Adicionar condição de veto
- [ ] Ajustar score mínimo
- [ ] Remover setup (não funciona)
- [ ] Refinar checklist

**Novo padrão observado:**
- Nome: 
- Descrição: 
- Quando usar: 
- Quando EVITAR: 

---

## Classificação Final

**Resultado foi:**
- [ ] **Expected** — Tese acertou conforme previsto
- [ ] **Acceptable** — Acertou, mas com variação
- [ ] **Lucky** — Acertou, mas por razão errada
- [ ] **Failed** — Setup falhou

**Razão da classificação:** 

---

## Tags de Revisão

- [ ] high_confidence_success
- [ ] low_confidence_failure
- [ ] motor_consensus_good
- [ ] motor_consensus_poor
- [ ] avoided_correctly_by_veto
- [ ] should_have_been_vetoed
- [ ] new_pattern_discovered
- [ ] playbook_needs_update
- [ ] edge_confirmed
- [ ] edge_broken

---

## Contribution para Base de Conhecimento

**Este post-mortem contribui para:**
- [ ] Validação de um playbook
- [ ] Descoberta de um novo padrão
- [ ] Confirmação de um erro recorrente
- [ ] Melhoria de um motor

**Documentação gerada:**
- Novo playbook: (link ou criar)
- Atualização playbook: (link)
- Erro adicionado a knowledge base: (link)

---

## Estatísticas

**Antes deste trade:**
- Win rate em setup: X%
- Avg pips por setup: X

**Depois (com este trade incluído):**
- Win rate em setup: X%
- Avg pips por setup: X

**Impact:** 

---

## Reviewer Notes

(Preenchido por revisão manual quando aplicável)

**Analisado por:** 
**Data:** 
**Aprovação:** 

**Comentários:** 
