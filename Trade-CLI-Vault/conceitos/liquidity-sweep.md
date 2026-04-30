---
type: concept
concept: Liquidity Sweep
aliases: [stop-hunt, liquidity-raid, turtle-soup, BSL, SSL]
category: ICT-SMC
created: 2026-05-01
tags: [liquidity, sweep, stop-hunt, BSL, SSL]
---

# Liquidity Sweep — Varredura de Liquidez

## Definição

Um **Liquidity Sweep** é quando o preço penetra acima de equal highs (BSL — Buy-Side Liquidity) ou abaixo de equal lows (SSL — Sell-Side Liquidity) para **recolher os stops** dos traders retail, antes de se reverter na direcção oposta.

**Em termos simples:** As instituições "roubam" os stops para acumular posições opostas.

## Tipos

### BSL — Buy-Side Liquidity
- Equal highs / previous highs = magneto de liquidez
- Stops de shorts ficam **acima** dos highs
- Sweep: preço sobe para recolher esses stops
- Após sweep BSL → possível drop (instituições vendem)

### SSL — Sell-Side Liquidity
- Equal lows / previous lows = magneto de liquidez
- Stops de longs ficam **abaixo** dos lows
- Sweep: preço desce para recolher esses stops
- Após sweep SSL → possível rally (instituições compram)

## Visualização

```
BSL Sweep:
   ═══════ Equal Highs (BSL) ════
   ↑ Sweep (preço sobe para recolher stops)
   ↓ Reversal (preço cai com nova liquidez)

SSL Sweep:
   ↓ Sweep (preço desce para recolher stops)
   ↑ Reversal (preço sobe com nova liquidez)
   ═══════ Equal Lows (SSL) ════
```

## Quando um Sweep é um Setup

✅ Setup de alta probabilidade quando:
1. Sweep durante uma killzone (London/NY open)
2. Confirmação com [[conceitos/MSS]] (Market Structure Shift) após sweep
3. HTF bias alinhado com direcção do reversal
4. Sweep de nível significativo (daily/weekly highs ou lows)

❌ Não é setup quando:
1. Sweep sem MSS (pode continuar na mesma direcção)
2. Contra HTF bias forte
3. Em evento de notícias alto impacto

## Sequência de Setup

```
1. Identificar zona de liquidez (equal highs/lows, previous highs/lows)
2. Aguardar killzone
3. Observar sweep do nível
4. Confirmar MSS no LTF (H1 → M15 → M5)
5. Identificar OB ou FVG para entrada
6. Entrar com SL acima/abaixo do swing do sweep
```

## Ligações

- [[conceitos/MSS]] — Confirmação obrigatória após sweep
- [[conceitos/order-block]] — Entrada frequente em OB após sweep
- [[metodos/ICT]] — Core do sistema ICT (turtle soup concept)
- [[metodos/SMC]] — ChoCH após sweep = confirmação SMC

---

*Conceito documentado em: 2026-05-01*
