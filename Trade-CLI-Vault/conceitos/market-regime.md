---
type: conceito
symbol: todos
created: 2026-05-01
tags: [market-regime, technical, planning]
confidence: high
---

# Market Regime

## Definition

**Market Regime** é o estado macro do mercado num determinado timeframe: **Trending**, **Ranging**, ou **Volatile**. Determina qual método de análise é mais relevante e reduz falsas sinais.

## Three Regimes

### 1. Trending Regime
Mercado faz progressão clara em uma direção com estrutura consistente de higher highs/lows (uptrend) ou lower highs/lows (downtrend).

**Indicators:**
- [[displacement]] significativo (>30 pips em H4 sem retraço significativo)
- Média móvel inclinada (20 EMA > 50 EMA > 200 EMA em uptrend)
- ADX > 25 (strong trend)

**Setup Priority:**
1. [[order-block]] no retraço da tendência
2. [[BOS]] acima resistência anterior
3. [[liquidity-sweep]] antes de retest

**Risk Management:**
- Stop no extremo anterior ou estrutura quebrada
- RR 1:3 mínimo

### 2. Ranging Regime
Mercado consolida entre nível suporte e resistência. Preço oscila sem direção clara.

**Indicators:**
- Price ≈ média móvel (congestionamento)
- ADX < 20 (weak trend)
- RSI 40–60 ou osciladores em meio-campo

**Setup Priority:**
1. Entrada no suporte/resistência com retração pequena
2. Scalp de oscilação (buy support, sell resistance)
3. Breakout falso = reversão rápida → stop loss ativo

**Risk Management:**
- Stops muito próximos (não aguenta range oscilação)
- Scaling em (não all-in em ranging)
- Saída rápida se break falhar

### 3. Volatile Regime
Preço move agressivamente em ambas as direções, spikes inesperados, gaps sem confirmação estrutural.

**Triggers:**
- Economic calendar evento grande (NFP, ECB, earnings)
- Gap overnight após notícia
- Cambistas hedging em massa

**Setup Priority:**
1. ❌ Não trade — aguarde clareza de regime
2. ✅ Apenas trades de high convicção com wide stops
3. ✅ Liquidação de posições antes de notícia

**Risk Management:**
- NUNCA all-in volatility regime
- Stops mínimo 50 pips (ou % equivalente)
- Saída se preço move contra de forma inesperada

## How Trade-CLI Integrates

```
Orchestrator.analyze(symbol, timeframe, bars)
    ↓
TechnicalEngine detects ADX, displacement → infers regime
    ↓
ThesisEngine.synthesize():
    - Trending: favor [[order-block]] setups
    - Ranging: favor mean reversion
    - Volatile: reduce conviction, widen stops
    ↓
RiskGuardian.should_block():
    - Volatile → may flag BLOCKED if conviction < 0.6
```

## Confluencing with Timeframes

| Timeframe | Regime | Setup | RR Goal |
|-----------|--------|-------|---------|
| H4 | Trending | BOS + OB | 1:3 |
| H1 | Ranging | Support/Resistance | 1:1.5 |
| M15 | Volatile | Exit existing | Minimize loss |

## Connection to ICT

[[metodos/ICT]] assumes a **trending regime** for order block trading. If regime is ranging or volatile, ICT setups have higher false break rate. Always verify regime before [[metodos/ICT]] execution.

---
*Last Updated: 2026-05-01*
