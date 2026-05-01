---
type: metodo
symbol: todos
created: 2026-05-01
tags: [sentiment, analysis, framework]
confidence: medium
---

# Sentiment Analysis Method

## Definition

**Sentiment Analysis** in Forex evaluates trader behavior and market mood through public data sources (RSS feeds, news, market surveys) to confirm or contradict technical/structural signals. Sentiment acts as a **confluencing indicator** — high technical confluence + positive sentiment = premium setup.

## Data Sources (No Cloud API)

### 1. Public RSS Feeds
- **FX News:** ForexFactory economic calendar + central bank announcements
- **Market News:** Bloomberg, Reuters, CNBC headlines (via feed aggregators like feedparser)
- **Sentiment Proxies:** VIX (risk-off), DXY (USD strength), equity indices (risk-on/risk-off)

### 2. Market Positioning Proxies
- **Commitment of Traders (CoT):** CFTC reports (weekly, public) on spec/hedge positioning
- **Flow Indicators:** Order flow imbalance (TradingView, locally computed from data)

### 3. Technical Sentiment Heuristics
- **Price Action:** Reversal candles, momentum divergences suggest sentiment shift
- **Volume Pattern:** High volume rallies = conviction; low volume drifts = sentiment weakness

## Sentiment Scoring (0.0–1.0)

### Bullish Sentiment Signals
- ✅ DXY declining (USD weakening, risk-on)
- ✅ Equities rallying (positive macro mood)
- ✅ Positive news on major pair (e.g., ECB hawkish → EURUSD bullish)
- ✅ Momentum candles + volume confirmation
- ✅ CoT: net longs increasing in base currency

**Score += 0.15** per signal (max 0.90)

### Bearish Sentiment Signals
- ✅ DXY rising (USD strengthening, risk-off)
- ✅ Equities declining (negative macro mood)
- ✅ Negative news on major pair (e.g., BoE dovish → GBPUSD bearish)
- ✅ Rejection candles + high volume down
- ✅ CoT: net shorts increasing in base currency

**Score -= 0.15** per signal (min 0.10)

### Neutral Sentiment
- 📊 No clear macro catalyst
- 📊 Equities flat/consolidating
- 📊 CoT positioning mixed

**Score = 0.50**

## Integration with Technical Analysis

### High Confluence Setup

```
Technical: [[order-block]] bullish, [[BOS]] above resistance
Sentiment: DXY down, equities up, positive EUR news
↓
Alignment score HIGH (technical + sentiment agree)
Entry: Full size, tight stop
```

### Divergence Setup (Trade Contradiction)

```
Technical: [[BOS]] down (bearish)
Sentiment: DXY up, equities down (also bearish)
↓
Alignment score HIGH (technical + sentiment BOTH bearish)
Entry: Sell with confidence
```

### Contested Setup (Low Alignment)

```
Technical: [[BOS]] up (bullish structure)
Sentiment: DXY up (risk-off, USD strength)
↓
Alignment score LOW (technical bullish, sentiment bearish)
Trade: WATCH ONLY — wait for clarity
```

## Trade-CLI Implementation

`SentimentEngine` in Trade-CLI:

```python
def analyze(self, symbol: str, timeframe: str, bars=None) -> EngineOutput:
    # Deterministic sentiment score based on symbol + timeframe
    # Phase 2.4: will integrate real RSS feeds + DXY proxy
    
    score = compute_sentiment_heuristic(symbol, timeframe)
    
    return EngineOutput(
        engine_name="sentiment",
        score=score,  # 0.0 (bearish) to 1.0 (bullish)
        explanation=f"Sentiment for {symbol} {timeframe}: ...",
        evidence={"dxy_trend": ..., "news_bias": ..., "positioning": ...}
    )
```

## Limitations

❌ **Lagging Signal:** News breaks during market hours; sentiment updates are delayed
❌ **Noise:** Opinions ≠ facts; sentiment can be irrational
❌ **Crowded Positioning:** When CoT longs spike, reversal risk increases
❌ **No Account-Specific Data:** Cannot see retail flow from your broker

✅ **Confluencing:** Works best with structure + technicals as primary, sentiment as secondary

## When Sentiment Matters Most

### Crisis/Event-Driven Trading
- Geopolitical tensions → sharp sentiment swings
- Central bank pivot → immediate DXY reaction
- Major data print (NFP) → macro repricing

### Trend Confirmation
- [[market-regime]] trending + sentiment aligned = stay in trade
- Trend exhaustion often preceded by sentiment deterioration

### Setup Timing
- Entry with sentiment confluence = higher win rate
- Exit before sentiment reversal = reduce drawdown

## When Sentiment Fails

❌ Flash crashes (algorithm cascade)
❌ Thin liquidity sessions (Asian hours on minor pairs)
❌ High-frequency scalping (sentiment too slow)

## Sentiment Watchlist for Trade-CLI

| Symbol | Key Sentiment Driver | News Frequency |
|--------|----------------------|-----------------|
| EURUSD | ECB policy + euro zone inflation | Daily (ECB calendar) |
| USDJPY | BoJ policy + JPY carry trade | Daily (BoJ calendar) |
| USDCAD | Oil price + BoC policy | Daily (energy news) |
| US30, NAS100 | Fed policy + earnings season | Weekly (earnings, FOMC) |

## Connection to [[metodos/ICT]]

ICT structure + sentiment confluence = **premium setup:**

```
[[order-block]] (ICT structure)
+ [[BOS]] confirmation (ICT pivot)
+ Positive sentiment (macro alignment)
→ Entry with 1:3 RR likely
```

Without sentiment alignment, [[metodos/ICT]] setups can be true structurally but catch reversals on macro news.

---
*Last Updated: 2026-05-01*
*Trade-CLI Integration: SentimentEngine (Phase 2.4)*
