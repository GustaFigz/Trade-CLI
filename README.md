# Trade-CLI

> Local AI Copilot para decisões de trading em Forex — 100% offline, zero cloud.

[![CI](https://github.com/GustaFigz/Trade-CLI/actions/workflows/ci.yml/badge.svg)](https://github.com/GustaFigz/Trade-CLI/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Filosofia:** A IA suporta decisões. Nunca executa trades. Nunca envia dados para a nuvem.

---

## Funcionalidades

- **Análise Multi-Engine** — Technical, Price Action e Fundamental com scores independentes
- **RiskGuardian** — Camada de veto determinística. Se o risco é alto, bloqueia. Sem override.
- **LLM Local** — Gemma via Ollama para síntese e raciocínio. Zero custo, zero privacidade.
- **Knowledge Base** — RAG com embeddings locais (sentence-transformers + FAISS)
- **Obsidian Vault** — Todas as análises, post-mortems e conceitos num grafo de conhecimento
- **FTMO Compliant** — Regras de prop firm integradas no RiskGuardian
- **Interface Profissional** — Launcher interactivo com splash animado, REPL e painel de estado

---

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/GustaFigz/Trade-CLI
cd Trade-CLI

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar comando global (opcional)
pip install -e .

# 4. Inicializar vault + base de dados
python main.py init
```

### Ollama (LLM Local)

```bash
# Instalar: https://ollama.ai
ollama serve          # deixar a correr em background
ollama pull gemma:7b  # descarregar o modelo (~4GB)
```

---

## Usar

### Modo Interactivo (recomendado)

```bash
tradecli
# ou
python main.py
```

Abre um launcher com:
- Splash animado com logo ASCII
- Painel de estado (Ollama, DB, Vault)
- REPL com prompt `tradecli >`
- Todos os comandos disponíveis com `help`

### Modo Comando Directo

```bash
tradecli analyze EURUSD H1          # análise completa
tradecli analyze USDJPY M15         # timeframe diferente
tradecli analyze US30 H1 --no-llm   # sem LLM (mais rápido)
tradecli analyze EURUSD H1 --test   # modo teste (mock data)
tradecli health                     # estado dos serviços
tradecli assets                     # listar ativos configurados
tradecli version                    # versão do Trade-CLI
```

### Treino e Conhecimento

```bash
tradecli train material.pdf --topic ict          # ingerir PDF
tradecli knowledge list                          # listar entries
tradecli knowledge search --query "order block"  # pesquisar
```

### Pós-Análise

```bash
tradecli outcome T20260501-001 25.5 --notes "Entry no FVG"  # registar resultado
tradecli review week                                         # revisão semanal
```

---

## Arquitectura

```
Trade-CLI/
├── core/                     # Schema + RiskGuardian (FROZEN)
│   ├── analysis_schema.py    # Dataclasses (AnalysisOutput, EngineOutput)
│   └── risk_guardian.py      # Veto layer — NUNCA bypass
│
├── engines/                  # Engines analíticos
│   └── __init__.py           # Technical, PriceAction, Fundamental, ThesisEngine
│
├── orchestrator/             # Coordenação
│   ├── orchestrator.py       # Pipeline completo de análise
│   └── llm_client.py         # Ollama via httpx (sem cloud APIs)
│
├── data/                     # Dados de mercado
│   ├── mt5_client.py         # MetaTrader5 read-only wrapper
│   └── mock_data.py          # MockDataProvider para dev/testes
│
├── knowledge/                # RAG System
│   ├── obsidian_reader.py    # Lê vault Obsidian
│   ├── chunk_vectorizer.py   # Texto → embeddings
│   ├── rag_retriever.py      # FAISS search
│   └── context_builder.py    # Constrói contexto para LLM
│
├── training/                 # Ingestão de conhecimento
│   ├── ingest.py             # PDF/Markdown/TXT parsing
│   ├── chunker.py            # Semantic chunking
│   ├── tagger.py             # Auto-tagging
│   └── kb_writer.py          # Escreve em SQLite + Obsidian
│
├── cli/                      # Interface
│   ├── main.py               # Comandos Typer
│   └── launcher.py           # Launcher interactivo + REPL
│
├── config/                   # Configuração
│   ├── assets.yaml           # Ativos, timeframes, sessões
│   └── ftmo-rules.yaml       # Regras FTMO
│
├── Trade-CLI-Vault/          # Obsidian Knowledge Graph
│   ├── 00-meta/              # Templates, sessões, índice
│   ├── ativos/               # Hubs: EURUSD, USDJPY, USDCAD, US30, NAS100
│   ├── metodos/              # ICT, SMC, Wyckoff, Price Action
│   ├── conceitos/            # Order Block, FVG, MSS, Killzone
│   ├── teses/                # Análises geradas
│   ├── post-mortems/         # Resultados pós-trade
│   ├── playbooks/            # Estratégias documentadas
│   └── treino/               # Material de estudo ingerido
│
├── tests/                    # Testes
├── main.py                   # Entry point principal
├── CLAUDE.md                 # Contexto permanente para agentes
├── pyproject.toml            # Config: ruff, mypy, pytest, entry points
└── requirements.txt          # Dependências
```

---

## Ativos Suportados

| Símbolo | Tipo | Sessão Principal | Spread Típico |
|---------|------|-----------------|---------------|
| EURUSD | Forex Major | London, New York | 0.8 pips |
| USDJPY | Forex Major | Tokyo, London, NY | 1.0 pips |
| USDCAD | Forex Major | New York | 1.2 pips |
| US30 | Índice | New York | 3.0 pts |
| NAS100 | Índice | New York | 2.5 pts |

---

## Contrato de Análise

Cada `tradecli analyze SYMBOL TF` produz:

```python
AnalysisOutput(
    symbol="EURUSD",
    timeframe="H1",
    bias="bullish|bearish|neutral|fragile",
    confidence_score=0.0-1.0,      # confiança global
    alignment_score=0.0-1.0,       # concordância entre engines
    technical_score=0.0-1.0,       # engine técnico
    price_action_score=0.0-1.0,    # engine price action
    fundamental_score=0.0-1.0,     # engine fundamental
    verdict="allowed|watch_only|blocked",  # decisão do RiskGuardian
    invalidations=["..."],         # condições que invalidam a tese
    risk_notes=["..."],            # notas de risco
)
```

---

## Stack Tecnológico

| Componente | Tecnologia | Custo |
|-----------|-----------|-------|
| LLM | Gemma 7B via Ollama | Grátis |
| Embeddings | sentence-transformers (MiniLM) | Grátis |
| Vector DB | FAISS (local) | Grátis |
| Knowledge | Obsidian + SQLite | Grátis |
| Terminal | Rich + Typer | Grátis |
| CI/CD | GitHub Actions | Grátis |

**Total: €0/mês. 100% offline. 100% privado.**

---

## Desenvolvimento

```bash
# Correr testes
pytest tests/ -v

# Lint
ruff check .

# Type check
mypy core/ engines/ --ignore-missing-imports

# Health check
python main.py health
```

---

## Regras Não-Negociáveis

1. **NUNCA** executar ordens reais — MT5 read-only apenas
2. **NUNCA** enviar dados para cloud APIs — Ollama local é o padrão
3. **NUNCA** bypass ao RiskGuardian — é a camada final
4. **NUNCA** commitar database.db, .env, .obsidian/
5. **SEMPRE** type hints em funções novas
6. **SEMPRE** testes com >80% coverage em core/ e engines/

---

**Fase actual:** 2.3 (Data Plane + Interface)  
**Próxima fase:** 2.4 (RAG funcional + Engines reais com TA)  
**Objectivo final:** `tradecli analyze EURUSD H1` → análise completa em <30s, 100% offline

---

*Trade-CLI — Phase 2 | 2026-05-01*
