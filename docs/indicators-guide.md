# Indicator Guide for Beginners

New to technical indicators? This guide explains each indicator CoinSifter supports in plain language.

---

## RSI (Relative Strength Index)

**What it is:** Measures how fast a coin's price has been going up or down recently, on a scale of 0–100.

**How to read it:**
- **Below 30** — The coin has dropped a lot recently. It might be "oversold" and due for a bounce.
- **Above 70** — The coin has risen a lot recently. It might be "overbought" and due for a pullback.
- **Between 50–70** — Generally bullish momentum without being overheated.

**Example filter:**
```yaml
- indicator: rsi
  timeframe: 4h
  condition: between
  value: [50, 70]   # Find coins with healthy upward momentum
```

---

## EMA (Exponential Moving Average)

**What it is:** A smoothed average of recent prices. It shows the general direction (trend) of a coin. Shorter periods (e.g., EMA 20) react faster; longer periods (e.g., EMA 50, 200) show the bigger trend.

**How to read it:**
- **Price above EMA** — The coin is trading above its average, suggesting an uptrend.
- **Price below EMA** — The coin is trading below its average, suggesting a downtrend.
- **Slope up/down** — The average itself is rising or falling.

**Example filter:**
```yaml
- indicator: ema
  timeframe: 4h
  period: 50
  condition: price_above   # Coin is in an uptrend
```

---

## EMA Cross

**What it is:** Compares two EMAs (fast EMA 20 vs slow EMA 50). When the fast one crosses above the slow one, it's a bullish signal — and vice versa.

**How to read it:**
- **Golden Cross** (EMA 20 crosses above EMA 50) — Bullish signal, trend may be turning up.
- **Death Cross** (EMA 20 crosses below EMA 50) — Bearish signal, trend may be turning down.

**Example filter:**
```yaml
- indicator: ema_cross
  timeframe: 4h
  condition: golden_cross   # Bullish trend reversal signal
```

---

## MACD (Moving Average Convergence Divergence)

**What it is:** Shows the relationship between two moving averages. It generates a "MACD line" and a "Signal line". When MACD crosses above the Signal, momentum is turning bullish.

**How to read it:**
- **Bullish** — MACD line is above Signal line (upward momentum).
- **Bearish** — MACD line is below Signal line (downward momentum).
- **Above zero** — Overall trend is up.
- **Below zero** — Overall trend is down.

**Example filter:**
```yaml
- indicator: macd
  timeframe: 1h
  condition: bullish   # Momentum is turning up
```

---

## Bollinger Bands (BB)

**What it is:** Creates an upper and lower band around a moving average. When price is near the lower band, the coin may be cheap relative to recent prices; near the upper band, it may be expensive.

**How to read it:**
- **Above lower band** — Price hasn't dropped to extreme lows (not crashing).
- **Below upper band** — Price hasn't spiked to extreme highs (not overextended).
- **Inside bands** — Price is within a normal range.

**Example filter:**
```yaml
- indicator: bb
  timeframe: 4h
  condition: above_lower   # Not in a crash
```

---

## KD / Stochastic

**What it is:** Similar to RSI but compares the closing price to its price range over a period. It has a K line (fast) and D line (slow).

**How to read it:**
- **Oversold** (K < 20) — The coin may be due for a bounce.
- **Overbought** (K > 80) — The coin may be due for a pullback.
- **Golden Cross** (K crosses above D) — Bullish signal.
- **Death Cross** (K crosses below D) — Bearish signal.

**Example filter:**
```yaml
- indicator: kd
  timeframe: 4h
  condition: golden_cross   # Bullish reversal signal
```

---

## Volume

**What it is:** How much of a coin is being traded. High volume means lots of activity and interest; low volume means fewer people are trading.

**How to read it:**
- **Above average** — More people are trading than usual. This can confirm that a price move is "real" and not just noise.

**Example filter:**
```yaml
- indicator: volume
  timeframe: 1h
  condition: above_average
  multiplier: 1.5   # Volume is 1.5x higher than the 20-period average
```

---

## ATR (Average True Range)

**What it is:** Measures how much a coin's price moves on average (volatility). Higher ATR = more volatile; lower ATR = calmer.

**How to read it:**
- **High ATR** — The coin moves a lot. Good for active traders, but riskier.
- **Low ATR** — The coin is relatively stable.

**Example filter:**
```yaml
- indicator: atr
  timeframe: 4h
  condition: above
  value: 0.5   # Only volatile coins
```

---

## AND vs OR Mode

When you combine multiple filters:

- **AND mode** (`filter_mode: "and"`) — The coin must pass ALL conditions. Stricter, fewer results, higher confidence.
- **OR mode** (`filter_mode: "or"`) — The coin needs to pass ANY one condition. More results, but lower confidence per result.

**Recommendation for beginners:** Start with AND mode and 2–3 conditions. You can always relax your criteria if you get too few results.

---

## Tips for Getting Started

1. **Start with demo mode** — Run `python coinsifter.py --demo` to see how results look.
2. **Copy the template** — `cp strategies/custom_template.yaml strategies/my_strategy.yaml` and edit it.
3. **Keep it simple** — 2–3 conditions is enough. More isn't always better.
4. **Use 4H timeframe** — It filters out short-term noise while still being responsive.
5. **Always manage risk** — CoinSifter finds coins matching technical conditions. It does NOT guarantee profits. Always set stop-losses and never invest more than you can afford to lose.
