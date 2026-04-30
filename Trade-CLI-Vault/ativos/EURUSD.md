---
type: asset-hub
symbol: EURUSD
pair: EUR/USD
category: forex-major
pip_value: 0.0001
sessions: [london, new_york]
correlations: [USDCAD, USDJPY, DXY, US30]
created: 2026-05-01
tags: [forex, major, EUR, USD, ECB, Fed]
---

# EURUSD — Hub Consolidado

## Visão Geral do Ativo

- **Par:** EUR/USD
- **Tipo:** Forex Major — par mais líquido do mundo
- **Pip value:** 0.0001 (4 casas decimais)
- **Spread típico:** 0.5–1.5 pips (London/NY overlap)
- **Sessão principal:** London + New York (melhor liquidez no overlap 12:00–16:00 UTC)

### Correlações Principais
- **Positiva forte:** [[ativos/USDCAD]] (inversa), [[ativos/US30]] (parcial)
- **Negativa forte:** DXY (Dollar Index)
- Se USD se fortalece → EURUSD desce
- Se risk-off → USD safe-haven → EURUSD tende a cair

## Contexto Macro

> Atualizar semanalmente com drivers actuais

### Drivers Económicos
1. **BCE (European Central Bank)** — taxa de juro, declarações de política
2. **Fed (Federal Reserve)** — taxa de juro, CPI, NFP
3. **DXY (Dollar Index)** — correlated inverse

### Sessões de Trading
| Sessão | UTC | Características |
|--------|-----|----------------|
| London Open | 08:00–11:00 | Alta liquidez, breakouts frequentes |
| NY Open | 13:00–16:00 | Volume máximo, alta volatilidade |
| London/NY Overlap | 12:00–16:00 | Melhor janela para entradas ICT |
| Asian | 23:00–07:00 | Baixa liquidez, tendência a consolidar |

## Teses Activas

*Populado pelo CLI: `python main.py analyze EURUSD H1`*

## Playbooks

*Populado ao longo do tempo. Ver [[playbooks/]]*

## Métodos Analíticos

- [[metodos/ICT]] — Killzones London/NY, order blocks em H4/H1
- [[metodos/SMC]] — BOS/ChoCH para confirmar direction bias
- [[metodos/Price-Action]] — Candle patterns para entradas precisas
- [[metodos/Wyckoff]] — Acumulação/distribuição em D1

## Conceitos-Chave

- [[conceitos/order-block]] — OBs em H4 são muito respeitados no EURUSD
- [[conceitos/FVG]] — Fair Value Gaps pós-displacement são frequentes
- [[conceitos/liquidity-sweep]] — Sweeps de equal highs/lows antes de reversões
- [[conceitos/MSS]] — Market Structure Shift após sweep confirma entrada
- [[conceitos/killzone]] — London open e NY open são as melhores janelas
- [[conceitos/displacement]] — Movimentos impulsivos em ambas as sessões

## Estatísticas

| Métrica | Valor |
|---------|-------|
| Análises totais | 0 |
| Teses ALLOWED | 0 |
| Teses WATCH_ONLY | 0 |
| Teses BLOCKED | 0 |

---

*Hub criado em: 2026-05-01 | Ativo principal do projecto Trade-CLI Fase 2*
