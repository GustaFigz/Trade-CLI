---
type: asset-hub
symbol: {{SYMBOL}}
created: {{date}}
tags: [forex, {{symbol}}, hub, {{correlation_group}}]
---

# {{SYMBOL}} — Hub Consolidado

## Visão Geral do Ativo

- **Par:** {{SYMBOL}}
- **Tipo:** Forex Major / Commodity / Índice
- **Grupo de correlação:** {{usd_major|usd_commodity|us_equity}}
- **Spread típico:** {{X}} pips
- **Sessão principal:** {{london|tokyo|new_york}}

### Correlações Principais
- Correlacionado com: [[ativos/{{corr1}}]], [[ativos/{{corr2}}]]
- Se {{SYMBOL}} sobe → {{correlado}} {{sobe|desce}}
- Se {{SYMBOL}} desce → {{correlado}} {{sobe|desce}}

## Contexto Macro Atual

> Atualizar semanalmente

### Viés Macro
- **Tendência D1:** {{bullish|bearish|neutral}}
- **Tendência H4:** {{bullish|bearish|neutral}}
- **Regime:** {{trending|ranging|volatile|calm}}

### Drivers Econômicos Ativos
1. {{Driver 1}} — {{próximo evento + data}}
2. {{Driver 2}} — {{próximo evento + data}}
3. {{Driver 3}} — {{próximo evento + data}}

### Próximos Eventos Críticos
- {{Data}}: {{Evento}} (impacto: {{baixo|médio|alto}})
- {{Data}}: {{Evento}} (impacto: {{baixo|médio|alto}})

## Playbooks Ativos para {{SYMBOL}}

Padrões que funcionam bem neste ativo:

- [[playbooks/{{playbook1}}]] — {{breve descrição}}
- [[playbooks/{{playbook2}}]] — {{breve descrição}}
- [[playbooks/{{playbook3}}]] — {{breve descrição}}

## Teses Recentes

### Teses ALLOWED (executadas)
- [[teses/{{tese1}}]] — {{data}}, {{resultado}}
- [[teses/{{tese2}}]] — {{data}}, {{resultado}}

### Teses WATCH_ONLY (monitoradas)
- [[teses/{{tese3}}]] — {{data}}, {{motivo da espera}}

### Teses BLOCKED (vetadas)
- [[teses/{{tese4}}]] — {{data}}, {{razão do veto}}

## Post-mortems (Aprendizados)

### Sucessos
- [[post-mortems/{{pm1}}]] — {{data}}, {{resultado}}: {{breve lição}}

### Falhas
- [[post-mortems/{{pm2}}]] — {{data}}, {{resultado}}: {{breve lição}}

## Notas de Comportamento Característico

### Padrões Observados
- {{SYMBOL}} tende a {{comportamento}} em {{condição}}
- {{SYMBOL}} responde melhor a {{tipo de notícia}} durante {{sessão}}
- {{SYMBOL}} mostra {{padrão}} quando {{condição}}

### Spread & Liquidez
- **Horário melhor:** {{horário UTC}} (menor spread)
- **Horário pior:** {{horário UTC}} (maior spread)
- **Liquidez:** {{boa|adequada|fraca}}

### Correlações Intra-dia
- {{SYMBOL}} vs {{índice relacionado}}: {{descrição}}

## Métodos Analíticos Principais para {{SYMBOL}}

- [[metodos/{{metodo1}}]] — Funciona bem aqui porque {{razão}}
- [[metodos/{{metodo2}}]] — Menos efetivo porque {{razão}}

## Conceitos-Chave

- [[conceitos/{{conceito1}}]]
- [[conceitos/{{conceito2}}]]
- [[conceitos/{{conceito3}}]]

## Estatísticas (Atualizar com CLI)

```
python main.py assets hub {{SYMBOL}} --stats
```

| Métrica | Valor |
|---------|-------|
| Análises totais | {{n}} |
| Teses ALLOWED | {{n}} |
| Teses WATCH_ONLY | {{n}} |
| Teses BLOCKED | {{n}} |
| Taxa acerto (ALLOWED) | {{%}} |
| Média de confiança | {{score}} |
| Média de alinhamento | {{score}} |

## Úlimas Atualizações

- {{Data}}: {{Mudança no contexto}}
- {{Data}}: {{Mudança no contexto}}
- {{Data}}: {{Mudança no contexto}}

---

*Hub atualizado em: {{data}}*  
*Próxima revisão: {{data}}*
