# Trade-CLI Vault — Índice Central

Bem-vindo ao Obsidian Vault do Trade-CLI. Este é o hub central de navegação.

---

## 🎯 Começar

1. **Primeira Vez?** Leia: [[00-meta/methodology]]
2. **Entender a Estrutura:** [[00-meta/obsidian-structure]]
3. **Ver Decisões de Fase 1:** [[00-meta/decisions]]

---

## 📑 Estrutura do Vault

### 📋 [[00-meta/]] — Configuração do Vault
- `index.md` (você está aqui)
- `methodology.md` — Como usar o sistema
- `decisions.md` — Decisões arquiteturais (Frozen)
- `templates-guide.md` — Guia de templates

### 💱 [[ativos/]] — Pares e Índices
- [[ativos/NZDUSD]] — Hub do par NZDUSD
- Índices: (adicionar conforme expandir)

### 📊 [[teses/]] — Análises Individuais
- Formato: `YYYY-MM-DD-SYMBOL-TF-DESCRIPTION.md`
- Exemplo: `2025-04-30-NZDUSD-M15-liquidity-sweep.md`
- Buscar: `tag:#NZDUSD`

### 📈 [[post-mortems/]] — Resultados & Lições
- Formato: `YYYY-MM-DD-SYMBOL-TF-POSTMORTEM.md`
- Compara tese original vs realidade
- Buscar: `tag:#success` ou `tag:#failure`

### 📖 [[playbooks/]] — Padrões Reutilizáveis
- Por setup: `liquidity-sweep-reclaim.md`
- Por ativo: `nzdusd-characteristics.md`
- Checklist operacional em cada um

### 📅 [[sessions/]] — Contexto Diário
- Formato: `daily-context-YYYY-MM-DD.md`
- Macro, sentimento, próximos eventos
- Criado no início do dia

### ⚖️ [[prop-firm/]] — Regras FTMO
- `ftmo-rules.md` — Resumo das regras
- `risk-guardian.md` — Como o veto funciona
- Source: `config/ftmo-rules.yaml`

---

## 🔍 Buscas Úteis

```
# Todas as análises NZDUSD
tag:#NZDUSD

# Setups de liquidity sweep
tag:#liquidity_sweep

# Teses aprovadas
tag:#allowed

# Teses em watch_only
tag:#watch_only

# Sucessos e falhas
tag:#success
tag:#failure
```

---

## 📖 Templates Disponíveis

Quando criar uma nova nota:

| Tipo | Template | Use Para |
|------|----------|----------|
| Tese | [[00-meta/template-thesis]] | Nova análise de setup |
| Post-Mortem | [[00-meta/template-postmortem]] | Resultado + lições |
| Playbook | [[00-meta/template-playbook]] | Padrão reutilizável |
| Daily Context | [[00-meta/template-daily-context]] | Snapshot macro |

---

## 🎯 Fluxo de Uso

```
1. Criar/ler [[daily-context-YYYY-MM-DD]]
   ↓
2. Identificar setup em [[ativos/NZDUSD]]
   ↓
3. Consultar playbook relevante: [[liquidity-sweep-reclaim]]
   ↓
4. Criar tese: [[2025-04-30-NZDUSD-M15-liquidity-sweep]]
   ↓
5. RiskGuardian valida (offline)
   ↓
6. Se ALLOWED ou WATCH_ONLY:
   - Operar ou apenas monitorar
   ↓
7. Depois: Criar post-mortem: [[2025-04-30-NZDUSD-M15-postmortem]]
   ↓
8. Atualizar playbook se necessário
```

---

## 📊 Métricas Rápidas

(Estas são consultadas do SQLite, não armazenadas aqui)

- Total teses criadas: XX
- Win rate geral: XX%
- Setup mais confiável: XX
- Playbook mais usado: XX

---

## 🔗 Links para Documentação Externa

- **Projeto Original:** `projeto-ia-trading-forex.md`
- **Planeamento Fase 1:** `Fase 1.md`
- **DB Schema:** `db/db_schema.sql`
- **Config FTMO:** `config/ftmo-rules.yaml`

---

## ⚙️ Manutenção

**Semanal:**
- [ ] Revisar post-mortems da semana
- [ ] Atualizar playbooks conforme padrões

**Mensal:**
- [ ] Cleanup notas muito antigas
- [ ] Review de win rates por setup

---

## ❓ FAQ

**P: Onde coloco um novo par (EURUSD)?**  
A: Cria `ativos/EURUSD.md` com mesmo template de [[ativos/NZDUSD]]

**P: Como adiciono um novo playbook?**  
A: Cria `playbooks/NOME.md` usando [[00-meta/template-playbook]]

**P: Onde rastreio erros repetidos?**  
A: Documenta em post-mortem, depois adiciona a `playbooks/errors/` se padrão

---

## 📝 Próximas Adições (Fase 2+)

- `micro-analysis/` — Estudos profundos
- `errors/` — Base de erros recorrentes
- `research/` — Artigos e estudos
- `archive/` — Teses antigas

---

**Última atualização:** 2025-04-30  
**Status:** Fase 1 ✓
