# Trade-CLI — Treino / Material de Estudo

Esta pasta é populada pelo comando:

```bash
python main.py train <ficheiro> --topic <ict|smc|wyckoff> --symbol <EURUSD>
```

## Subpastas

| Pasta | Conteúdo |
|-------|---------|
| `conhecimento/` | PDFs, MDs de métodos e conceitos |
| `estudos-de-caso/` | Análises de trades reais/históricos |
| `backtesting/` | Resultados de backtests |
| `videos/` | Resumos de vídeos/cursos |

## Workflow de Treino

1. Encontrar material (PDF, vídeo, artigo)
2. `python main.py train ficheiro.pdf --topic ict --symbol EURUSD`
3. Sistema chunka, tagueia e guarda no SQLite
4. RAG usa o material nas próximas análises
