---
type: conceito
symbol: todos
created: 2026-05-01
tags: [confluence, setup, planning, technical]
confidence: high
---

# Confluence

## Definition

**Confluence** é a sobreposição de múltiplos sinais (técnicos, estruturais, temporais) no mesmo nível ou timeframe. Quanto maior a confluência, maior a probabilidade da setup e menor a necessidade de risk management ajustado.

## Types of Confluence

### 1. Price-Level Confluence
Múltiplos níveis técnicos convergem no mesmo preço.

**Example:**
```
EURUSD H1:
- 200 EMA = 1.0850
- Previous swing high = 1.0850
- [[order-block]] zone = 1.0845–1.0855
- Fibonacci 61.8% retraço = 1.0851
↓
CONFLUÊNCIA ALTA = 1.0850 é nível crítico
```

**Trade Impact:**
- ✅ High conviction entry
- ✅ Tight, logical stop (just below EMA)
- ✅ RR 1:3+ realistic

### 2. Structural Confluence
Múltiplas estruturas suportam a mesma ação.

**Example:**
```
[[BOS]] acima H4 swing high
+ [[order-block]] confirmado no retraço H1
+ [[liquidity-sweep]] anterior = setup aligned
↓
Estrutura converge = compra acima OB likely
```

### 3. Timeframe Confluence
Sinais nos 3+ timeframes alinham na mesma direção.

**Example (Bullish Alignment):**
```
H4: Trending up (higher highs) + RSI > 60
H1: [[BOS]] acima resistência + MA aligned
M15: Entry [[order-block]] + price < 20 EMA
↓
3-timeframe confluence = HIGH CONVICTION
```

**Scoring (Trade-CLI):**
```
H4 bullish score = 0.75
H1 bullish score = 0.80
M15 bullish score = 0.70
→ Average = 0.75 (good alignment)
```

### 4. Time-Based Confluence
Eventos na sessão trading combinam com estrutura.

**Example:**
```
- Sessão London open (liquidity boost)
+ [[liquidity-sweep]] foi fecho da Ásia
+ [[order-block]] na sessão Londres
→ Timing reforça trade
```

## How Trade-CLI Measures Confluence

```python
AnalysisOutput:
    confidence_score = avg(engine_scores)  # 0.0–1.0
    alignment_score = std_dev(engine_scores)  # Lower = more aligned
    
    # High confluence:
    confidence = 0.75, alignment = 0.05  # All engines agree!
    
    # Low confluence:
    confidence = 0.60, alignment = 0.30  # Mixed signals
```

**Verdict Logic:**
```
if alignment > 0.25:
    verdict = "watch_only"  # Wait for more confluence
elif confidence < 0.60:
    verdict = "watch_only"
elif risk_guardian.check():
    verdict = "allowed"
else:
    verdict = "blocked"  # Risk rules violated
```

## Building a Confluence Setup

### Step 1: Find Structure
- Identify [[BOS]], [[order-block]], [[liquidity-sweep]] candidates

### Step 2: Verify Timeframe Alignment
- H4 bias bullish/bearish?
- H1 confluence with H4?
- M15 entry point clear?

### Step 3: Check Price Level
- EMA, Fib levels, previous S/R overlap?
- [[displacement]] + ADX confirm trend?

### Step 4: Time the Entry
- Economic calendar clear?
- Session (London/NY) supports bias?
- [[market-regime]] trending or volatile?

### Step 5: Risk Math
- Entry, stop, target defined?
- RR 1:3 or better?
- FTMO rules respected?

## High vs Low Confluence

| Factor | High Confluence | Low Confluence |
|--------|-----------------|----------------|
| Engines in agreement | 5–6/6 | 2–3/6 |
| Price level overlap | 2+ levels | No overlap |
| Timeframe alignment | H4, H1, M15 all agree | Only 1 timeframe |
| Structure clarity | Clear BOS + OB | Ambiguous |
| Risk/reward | 1:3+ | 1:1 or worse |

**Trade Decision:**
- **High confluence** → Enter full size, tight stop, relax TP
- **Medium confluence** → Scale in, normal RR, active monitoring
- **Low confluence** → Watch only, do not trade

## Common Confluence Traps

❌ **Trap 1:** Too many indicators = noise, not confluence
- Solution: Use 3–5 key confluences max (EMA, structure, Fib)

❌ **Trap 2:** Confirmation bias — force confluence that isn't there
- Solution: If alignment_score > 0.25, wait or skip

❌ **Trap 3:** Ignore [[market-regime]] — ranging market breaks confluences
- Solution: Verify regime before trade

## Connection to ICT

[[metodos/ICT]] + [[metodos/SMC]] both rely on confluence:
- [[order-block]] (structure) + [[BOS]] (pivot) + [[liquidity-sweep]] (validation) = ideal confluence

When Trade-CLI detects high confluence in [[metodos/ICT]] terms, confidence_score rises and RR improves.

---
*Last Updated: 2026-05-01*
