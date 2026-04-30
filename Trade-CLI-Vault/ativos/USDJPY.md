---
type: asset-hub
symbol: USDJPY
pair: USD/JPY
category: forex-major
pip_value: 0.01
sessions: [tokyo, new_york]
correlations: [EURUSD, US30, NAS100, gold]
created: 2026-05-01
tags: [forex, major, JPY, USD, BoJ, Fed, risk-on-off]
---

# USDJPY — Hub Consolidado

## Visão Geral do Ativo

- **Par:** USD/JPY
- **Tipo:** Forex Major — par risk-on/risk-off por excelência
- **Pip value:** 0.01 (2 casas decimais)
- **Spread típico:** 0.5–2.0 pips
- **Sessão principal:** Tokyo (Asian) + New York

### Correlações Principais
- **Positiva:** [[ativos/US30]], [[ativos/NAS100]] (risk-on correlação)
- **Negativa:** Gold, JPY bonds
- Se risk-on → USDJPY sobe (JPY vende, USD compra)
- Se risk-off → USDJPY desce (JPY safe-haven bid)

## Sessões de Trading

| Sessão | UTC | Características |
|--------|-----|----------------|
| Tokyo Open | 23:00–02:00 | Principal sessão JPY, spreads elevados às vezes |
| London Open | 08:00–11:00 | Continuação de Tokyo moves |
| NY Open | 13:00–16:00 | USD news drive, alta volatilidade |

## Teses Activas

*Populado pelo CLI: `python main.py analyze USDJPY H1`*

## Playbooks

*Ver [[playbooks/]]*

## Métodos Analíticos

- [[metodos/ICT]] — Tokyo killzone para entradas JPY
- [[metodos/SMC]] — Liquidity sweeps antes de NY open frequentes
- [[metodos/Price-Action]] — Doji patterns em consolidações
- [[metodos/Wyckoff]] — Risk-on/off cycles visíveis em D1

## Conceitos-Chave

- [[conceitos/liquidity-sweep]] — Equal highs antes de NY open são alvos frequentes
- [[conceitos/order-block]] — H4 OBs respeitados em tendência
- [[conceitos/MSS]] — Confirma reversão após sweep de liquidez
- [[conceitos/displacement]] — Movimentos rápidos no NY open
- [[conceitos/killzone]] — Tokyo e NY killzones mais relevantes

## Estatísticas

| Métrica | Valor |
|---------|-------|
| Análises totais | 0 |
| Teses ALLOWED | 0 |

---

*Hub criado em: 2026-05-01*
