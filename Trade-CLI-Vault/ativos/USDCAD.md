---
type: asset-hub
symbol: USDCAD
pair: USD/CAD
category: forex-major
pip_value: 0.0001
sessions: [new_york, london-close]
correlations: [EURUSD, crude-oil, DXY]
created: 2026-05-01
tags: [forex, major, CAD, USD, BoC, oil-correlation]
---

# USDCAD — Hub Consolidado

## Visão Geral do Ativo

- **Par:** USD/CAD
- **Tipo:** Forex Major — fortemente correlacionado com crude oil
- **Pip value:** 0.0001
- **Spread típico:** 1.0–2.5 pips
- **Sessão principal:** New York (overlap com London close)

### Correlações Principais
- **Crude Oil:** Correlação negativa — se oil sobe → CAD forte → USDCAD desce
- **DXY:** Correlação positiva (par USD)
- **[[ativos/EURUSD]]:** Correlação moderada (ambos são pares USD)
- Dados económicos canadenses (BoC, CPI, employment) impactam directamente

## Sessões de Trading

| Sessão | UTC | Características |
|--------|-----|----------------|
| London Close | 16:00–17:00 | Frequentes reversões e squeezes |
| NY Session | 13:00–20:00 | Principal janela, USD e oil news |

## Teses Activas

*Populado pelo CLI: `python main.py analyze USDCAD H1`*

## Métodos Analíticos

- [[metodos/ICT]] — NY open killzone principal
- [[metodos/SMC]] — BOS/ChoCH para confirmar direcção
- [[metodos/Price-Action]] — Oil correlação requer contexto macro

## Conceitos-Chave

- [[conceitos/order-block]] — H4 OBs em zonas de intervenção BoC
- [[conceitos/liquidity-sweep]] — Equal lows/highs antes de NY open
- [[conceitos/MSS]] — Confirma após sweep
- [[conceitos/FVG]] — Imbalances pós news frequentes
- [[conceitos/displacement]] — USD news causa moves rápidos

## Estatísticas

| Métrica | Valor |
|---------|-------|
| Análises totais | 0 |

---

*Hub criado em: 2026-05-01*
