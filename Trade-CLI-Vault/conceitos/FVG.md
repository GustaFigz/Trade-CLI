---
type: concept
concept: Fair Value Gap
abbreviation: FVG
aliases: [imbalance, inefficiency, IFVG]
category: ICT-SMC
created: 2026-05-01
tags: [FVG, fair-value-gap, imbalance, fill]
---

# FVG — Fair Value Gap (Imbalance)

## Definição

Um **Fair Value Gap** é um desequilíbrio entre três velas onde a vela do meio criou um gap que não foi preenchido pelos extremos das velas adjacentes:

- **Bullish FVG:** High da vela 1 ← gap → Low da vela 3 (vela 2 é bullish impulsiva)
- **Bearish FVG:** Low da vela 1 ← gap → High da vela 3 (vela 2 é bearish impulsiva)

## Visualização

```
Bullish FVG:
   Vela 1   Vela 2      Vela 3
   [  |  ]  [█████↑]   [  |  ]
         ←  FVG zona  →
   (High v1)           (Low v3)

Bearish FVG:
   [  |  ]  [█████↓]   [  |  ]
   (Low v1)            (High v3)
         ←  FVG zona  →
```

## Como Usar

### FVG como Zona de Entrada
1. Displacement cria FVG
2. Preço retorna para preencher o FVG
3. Confluência com OB ou killzone = entrada de alta probabilidade
4. SL abaixo/acima do FVG (se rejeitar)

### FVG como Alvo
- Um FVG aberto é um alvo de fill para o preço
- **"Price seeks to fill imbalances"** — preço tende a preencher FVGs antes de continuar

## Tipos

| Tipo | Quando | Uso |
|------|--------|-----|
| FVG standard | Após displacement | Entrada no fill |
| Inversion FVG (IFVG) | FVG preenchido e invertido | Nova zona de S/R |
| Daily FVG | No D1 | Alvo macro grande |

## Quando é VÁLIDO

✅ FVG válido quando:
1. Criado por displacement claro (não por doji/small body)
2. Alinhado com HTF bias
3. Não preenchido completamente ainda

❌ FVG inválido quando:
1. Completamente preenchido (price traded through it)
2. Criado em contra-tendência clara

## Ligações

- [[conceitos/order-block]] — OB e FVG frequentemente ocorrem juntos
- [[conceitos/displacement]] — O displacement CRIA o FVG
- [[metodos/ICT]] — Core PD array no sistema ICT

---

*Conceito documentado em: 2026-05-01*
