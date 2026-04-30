---
type: concept
concept: Displacement
aliases: [impulsive-move, expansion, impulse]
category: ICT-SMC
created: 2026-05-01
tags: [displacement, impulse, expansion, momentum, candle]
---

# Displacement — Movimento Impulsivo

## Definição

Um **Displacement** é um movimento de preço **forte e direccional** que:
1. Quebra estrutura de mercado (BOS ou MSS)
2. Deixa imbalances no gráfico ([[conceitos/FVG]])
3. Cria ou valida [[conceitos/order-block]]
4. Representa **execução institucional massiva**

**Em termos simples:** Um displacement é a "assinatura" de uma grande ordem institucional a ser executada. O preço move-se rápido e em linha recta, deixando um rasto de FVGs.

## Características Visuais

```
Bullish Displacement:
   ↑↑↑↑↑
   ████  ← corpo grande, wick pequeno
   ████  ← vela 2 continua
   ████  ← vela 3 continua (FVG entre v1 e v3)
   (3+ velas bullish consecutivas, pouco overlap)

Bearish Displacement:
   ████  ← início
   ████  ← vela 2
   ████  ← vela 3
   ↓↓↓↓↓
```

## Critérios para Displacement "Real"

| Critério | O que procurar |
|---------|---------------|
| Velocidade | 3+ velas sem retrace |
| Corpo vs Wick | Corpo > 70% da range da vela |
| Volume | Spike de volume (se disponível) |
| Spread | Spread aumenta durante o move |
| FVG | Pelo menos 1 FVG criado |

## Displacement vs Movimentos Comuns

| Tipo | Características | Fiabilidade |
|------|----------------|-------------|
| Displacement institucional | Rápido, sem overlap, FVG, volume spike | Alta |
| Move retail | Lento, overlapping candles | Baixa |
| News spike | Muito rápido, reverte | Cuidado — pode ser falso |

## Como Usar

### O Displacement como Contexto
1. Identificar displacement (move impulsivo)
2. Marcar o [[conceitos/FVG]] e [[conceitos/order-block]] criados
3. Aguardar pullback para estas zonas
4. Entrar na confluência OB + FVG

### O Displacement como Confirmação
- Após sweep de liquidez + MSS → displacement na nova direcção confirma entrada
- Displacement sem OB ou FVG → entrada mais arriscada

## Ligações

- [[conceitos/FVG]] — Displacement CRIA Fair Value Gaps
- [[conceitos/order-block]] — OB é a última vela antes do displacement
- [[conceitos/MSS]] — Displacement frequentemente acompanha o MSS

---

*Conceito documentado em: 2026-05-01*
