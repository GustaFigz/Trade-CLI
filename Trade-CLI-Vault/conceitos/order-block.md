---
type: concept
concept: Order Block
abbreviation: OB
category: ICT-SMC
related_methods: [ICT, SMC]
created: 2026-05-01
tags: [order-block, OB, institutional, supply, demand]
---

# Order Block (OB) — Bloco de Ordens Institucional

## Definição

Um **Order Block** é a última vela de movimento oposto **antes de um movimento impulsivo** (displacement). Representa onde as instituições colocaram ordens em lote, criando um desequilíbrio que o preço tende a revisitar.

**Em termos simples:** É a "impressão digital" de onde um banco ou hedge fund comprou/vendeu massivamente.

## Tipos

### Bullish Order Block
- Última vela bearish antes de displacement bullish
- Zona de interesse para LONG
- Preço retorna ao OB → possível bounce para cima

```
   ↑ Displacement bullish
   |
[████] ← Bullish OB (última vela bearish antes do impulso)
```

### Bearish Order Block
- Última vela bullish antes de displacement bearish  
- Zona de interesse para SHORT
- Preço retorna ao OB → possível drop

```
[████] ← Bearish OB (última vela bullish antes do impulso)
   |
   ↓ Displacement bearish
```

## Quando é VÁLIDO

✅ Um OB é válido quando:
1. Criado por deslocamento impulsivo (displacement claro)
2. Ainda não mitigado (preço não passou por dentro do OB)
3. Está na direcção do HTF bias
4. Existe liquidez acima/abaixo para atrair o preço

## Quando é INVÁLIDO (mitigado)

❌ O OB está inválido quando:
1. Preço atravessou completamente o OB
2. HTF bias mudou de direcção (BOS oposto)
3. Passou por mais de 2 rejeições sem funcionar

## Sequência de Setup

```
1. Identificar OB (última vela oposta antes de impulso)
2. Aguardar pullback para o OB
3. Confirmar entrada com LTF (pin bar, engulfing, FVG fill)
4. SL abaixo/acima do OB
5. TP: próximo nível de liquidez / FVG / OB oposto
```

## Ligações

- [[metodos/ICT]] — ICT define OB como core PD array
- [[metodos/SMC]] — SMC usa OB como zona de entrada principal
- [[conceitos/FVG]] — Frequentemente criado junto com OB
- [[conceitos/displacement]] — OB é criado PELO displacement

## Ativos Onde Funciona Melhor

- [[ativos/EURUSD]] — H4 e H1 OBs muito respeitados
- [[ativos/USDJPY]] — H1 OBs em Tokyo killzone
- [[ativos/US30]] — H1 OBs antes de NY open

---

*Conceito documentado em: 2026-05-01*
