# Métodos Analíticos — Hub

Biblioteca de métodos, técnicas e frameworks de análise usados no Trade-CLI.

## Métodos Implementados

### [[metodos/ICT]] — Inner Circle Trading
- Conceitos: Killzones, Fair Value Gaps (FVG), Order Blocks
- Timeframe: H4, H1, M15
- Aplicação: Setup de entrada em zonas de liquidez

### [[metodos/SMC]] — Smart Money Concepts
- Conceitos: Market structure, Breaker blocks, Displacement
- Timeframe: H4, H1
- Aplicação: Análise de movimento de smart money

### [[metodos/Wyckoff]] — Wyckoff Method
- Conceitos: Accumulation, Distribution, Effort vs Result
- Timeframe: D1, H4
- Aplicação: Identificação de fases de mercado

### [[metodos/price-action]] — Price Action
- Conceitos: Candle patterns, Confluence, Support/Resistance
- Timeframe: Todos
- Aplicação: Entry/Exit points com mínimo de indicadores

### [[metodos/volume-profile]] — Volume & Market Profile
- Conceitos: POC (Point of Control), VPOC, Value Area
- Timeframe: H1, M15
- Aplicação: Identificar níveis de liquidez

### [[metodos/fundamental]] — Análise Fundamental
- Conceitos: Economic calendar, Interest rates, Inflation
- Timeframe: D1 (macro context)
- Aplicação: Contexto macroeconômico para bias

## Decisões de Método

| Método | Ativo Principal | Taxa de Sucesso | Status |
|--------|-----------------|-----------------|--------|
| ICT | EURUSD, USDJPY | {{%}} | {{ativo|experimental}} |
| SMC | EURUSD | {{%}} | {{ativo|experimental}} |
| Wyckoff | EURUSD, US30 | {{%}} | {{ativo|experimental}} |
| Price Action | Todos | {{%}} | ✓ Ativo |
| Volume | EURUSD, US30 | {{%}} | {{experimental}} |
| Fundamental | Todos | {{%}} | ✓ Ativo |

## Combinações Recomendadas

### Setup Inicial (H4)
1. [[metodos/Wyckoff]] — Identificar fase
2. [[metodos/price-action]] — Padrão
3. [[metodos/fundamental]] — Contexto macro

### Confirmação (H1)
1. [[metodos/ICT|ICT]] — Liquidez
2. [[metodos/SMC]] — Smart money
3. [[metodos/volume-profile]] — Volume

### Entry (M15)
1. [[metodos/price-action]] — Padrão exato
2. [[metodos/volume-profile]] — Suporte volume
3. Invalidação clara

## Comparação de Métodos

### ICT vs SMC
- **ICT:** Mais específico em killzones, melhor para swing
- **SMC:** Mais amplo em estrutura, melhor para contexto

### Wyckoff vs Price Action
- **Wyckoff:** Foco em fases, melhor para timing
- **Price Action:** Foco em padrões, melhor para entry

## Referências

- [[treino/livros]] — Materiais sobre cada método
- [[conceitos]] — Conceitos-chave associados a cada método

---

*Atualizado: {{data}}*  
*Próxima revisão: {{data}}*
