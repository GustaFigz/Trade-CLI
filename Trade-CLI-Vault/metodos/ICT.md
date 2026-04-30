---
type: method-hub
method: ICT
full_name: Inner Circle Trader
creator: Michael J. Huddleston
category: smart-money
created: 2026-05-01
tags: [ICT, smart-money, order-block, FVG, killzone, OTE, PD-array]
---

# ICT — Inner Circle Trader

## O que é o ICT?

ICT (Inner Circle Trader) é uma metodologia desenvolvida por **Michael J. Huddleston** que foca na leitura do fluxo de ordens institucionais. O conceito central é que os market makers e bancos criam liquidez antes de mover o preço na direcção oposta.

**Premissa fundamental:** O preço vai sempre onde a liquidez está — acima de equal highs ou abaixo de equal lows — antes de se mover para o seu destino real.

## Conceitos Centrais

### PD Arrays (Premium/Discount Arrays)
Níveis onde instituições compram (discount) e vendem (premium):

| Nível | Tipo | Utilização |
|-------|------|-----------|
| Order Blocks | Premium/Discount | Zonas de entrada |
| Fair Value Gaps | Imbalance | Alvos de fill |
| Breaker Blocks | Ex-OB invalidado | Reversões |
| Mitigation Blocks | Incompleto | Fills parciais |

### Killzones (Janelas de Alta Probabilidade)
Ver: [[conceitos/killzone]]

| Killzone | UTC | Ativo Principal |
|----------|-----|----------------|
| London Open | 08:00–11:00 | [[ativos/EURUSD]], [[ativos/USDJPY]] |
| NY Open | 13:00–16:00 | Todos os ativos |
| NY Close | 19:00–20:00 | Reversões |
| Asian | 23:00–02:00 | [[ativos/USDJPY]] |

## Quando Usar ICT

✅ **Usar quando:**
- Há uma killzone activa (London/NY open)
- Existe liquidez clara acima/abaixo de equal highs/lows
- Tendência D1 ou H4 confirmada
- Sweep de liquidez + MSS confirmado

❌ **NÃO usar quando:**
- Dentro de 15 minutos de notícias de alto impacto
- Fora das killzones (random times)
- Spread muito elevado
- Sem tendência clara em higher timeframe

## Sequência de Setup ICT (OTE)

```
1. Identificar HTF bias (D1/H4)
2. Aguardar killzone
3. Observar sweep de liquidez (BSL ou SSL)
4. Confirmar MSS (Market Structure Shift)
5. Identificar OB ou FVG no LTF
6. Entrar no OTE (Optimal Trade Entry) — 61.8%–78.6% retrace
7. Target: previous liquidity or opposing PD array
```

## Ligações aos Conceitos

- [[conceitos/order-block]] — Core de qualquer setup ICT
- [[conceitos/FVG]] — Imbalances criados por displacement
- [[conceitos/killzone]] — Janelas temporais de setup
- [[conceitos/liquidity-sweep]] — Gatilho do setup
- [[conceitos/MSS]] — Confirmação após sweep
- [[conceitos/displacement]] — Movimento impulsivo que cria FVG/OB

## Ativos Favoritos

- [[ativos/EURUSD]] — Melhor correlação com London/NY killzones
- [[ativos/USDJPY]] — Tokyo killzone muito forte
- [[ativos/US30]] — NY open killzone muito claro

## Ligações Cruzadas

- [[metodos/SMC]] — SMC é derivado do ICT com terminologia simplificada

---

*Método documentado em: 2026-05-01*
