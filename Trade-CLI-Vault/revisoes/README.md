# Trade-CLI — Revisões de Performance

Esta pasta é populada pelo comando:

```bash
python main.py review week   # revisão semanal
python main.py review month  # revisão mensal
```

## Subpastas

| Pasta | Conteúdo |
|-------|---------|
| `semanais/` | Relatórios semanais gerados pelo CLI |
| `mensais/` | Relatórios mensais gerados pelo CLI |

## Formato do Relatório

Cada revisão inclui:
- Total de análises no período
- Breakdown por verdict (ALLOWED / WATCH_ONLY / BLOCKED)
- Taxa de acerto das análises ALLOWED
- Lições aprendidas (preenchido manualmente)
- Próximas melhorias

## Nota

Os relatórios são gerados automaticamente mas **devem ser revistos manualmente** antes de guardar no vault. Nunca guardar lixo automático.
