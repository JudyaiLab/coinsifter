---
name: coinsifter
description: Scan Binance for cryptocurrencies matching technical indicator conditions (RSI, MACD, EMA, BB, KD, Volume). Self-hosted, strategy-based CLI screening tool.
metadata:
  version: "1.8.0"
  author: "Judy AI Lab"
  tags: ["crypto", "trading", "binance", "technical-analysis", "screening"]
  license: "MIT"
---

# CoinSifter

**You set the rules. It finds the coins.**

CoinSifter is an open-source cryptocurrency screening tool that automatically scans Binance for coins matching your custom technical conditions.

## Capabilities

- **8 Technical Indicators**: RSI, EMA, EMA Cross, MACD, Bollinger Bands, KD Stochastic, Volume, ATR
- **Multi-Timeframe**: Screen across 4H, 1H, 15m, 1D simultaneously
- **Strategy System**: YAML-based screening strategies — combine any indicators
- **CLI Mode**: Headless scanning for automation and cron jobs
- **Closed Candle Logic**: Uses previous closed candle (`iloc[-2]`) to prevent false signals

## Installation

```bash
git clone https://github.com/JudyaiLab/coinsifter.git
cd coinsifter
pip install -r requirements.txt
cp config.example.yaml config.yaml
# Edit config.yaml — add your Binance API key (read-only permission is enough)
```

### Dependencies

```
ccxt>=4.0.0
pandas>=2.0.0
pyyaml>=6.0
```

## Strategy Format

Strategies are YAML files in the `strategies/` directory:

```yaml
name: "Bullish Trend"
description: "Multi-timeframe trend confirmation"
direction: "long"
filter_mode: "and"

filters:
  - indicator: ema
    timeframe: 4h
    period: 50
    condition: price_above

  - indicator: rsi
    timeframe: 4h
    period: 14
    condition: between
    value: [50, 70]

  - indicator: macd
    timeframe: 1h
    condition: bullish

  - indicator: volume
    timeframe: 1h
    condition: above_average
    multiplier: 1.2
```

### Supported Indicators & Conditions

| Indicator | Conditions | Parameters |
|-----------|-----------|------------|
| `rsi` | `above`, `below`, `between` | `period` (default: 14), `value` |
| `ema` | `price_above`, `price_below`, `slope_up`, `slope_down` | `period` (default: 20) |
| `macd` | `bullish`, `bearish`, `above_zero`, `below_zero` | — |
| `bb` | `above_lower`, `below_upper`, `inside` | `period` (default: 20), `std` (default: 2.0) |
| `kd` | `golden_cross`, `death_cross`, `oversold`, `overbought`, `k_above_d` | `period` (default: 14) |
| `volume` | `above_average` | `multiplier` (default: 1.5) |
| `ema_cross` | `golden_cross`, `death_cross`, `ema20_above_50`, `ema20_below_50` | — |
| `atr` | `above` | `period` (default: 14), `value` |

### Filter Modes

- `"and"` — All conditions must pass (strict screening)
- `"or"` — Any condition passes (broad screening)

## CLI Usage

```bash
# Default scan using config.yaml
python coinsifter.py

# Use a specific strategy file
python coinsifter.py --strategy strategies/custom_template.yaml

# Verbose output with indicator details
python coinsifter.py -v

# Loop mode — scan every 4 hours
python coinsifter.py --loop --interval 240

# Full options
python coinsifter.py -c config.yaml -s strategies/custom_template.yaml -v --loop --interval 60
```

## Output Example

```
==================================================
🔮 CoinSifter v1.8.0 — You set the rules. It finds the coins.
==================================================
📋 Strategy: Bullish Trend (long)
🔍 Scanning Binance USDT pairs (min volume: 50M)...
📊 Found 50 candidates, screening...

🎯 3 coins passed all filters:

  1. BTC/USDT
     Price: 84250.5 | 24h Vol: 2500.3M | Change: 2.4%
     ✅ RSI=65.3 in [50,70]
     ✅ Price 84250.5 > EMA50 82100.2
     ✅ MACD bullish (MACD > Signal)
     ✅ Volume 1.8x >= 1.5x
==================================================
```

## AI Agent Integration

CoinSifter can be invoked by AI agents for automated market screening workflows.

### CLI Invocation (Recommended)

```bash
# Agent runs a scan and captures output
python coinsifter.py -s strategies/custom_template.yaml -v
```

### Strategy Generation

Agents can create custom strategies programmatically:

```python
import yaml

strategy = {
    "name": "Agent Custom Screen",
    "filter_mode": "and",
    "filters": [
        {"indicator": "rsi", "timeframe": "4h", "period": 14, "condition": "between", "value": [40, 60]},
        {"indicator": "volume", "timeframe": "1h", "condition": "above_average", "multiplier": 2.0}
    ]
}

with open("strategies/agent_custom.yaml", "w") as f:
    yaml.dump(strategy, f)
```

### Typical Agent Workflow

1. **Create strategy** — Generate YAML based on market thesis
2. **Run scan** — Execute via CLI
3. **Parse results** — Extract passed symbols with indicator values
4. **Make decisions** — Use filter reasons for trade logic

## CoinSifter Pro

Want more? **CoinSifter Pro** includes Web UI, scheduled scans, Telegram alerts, pre-built backtested strategies, and one-click launchers.

👉 [Get CoinSifter Pro](https://judyailab.com/shop/)

## Requirements

- Python 3.10+
- Binance account with API key (read-only permission sufficient)
- Internet connection

## Links

- GitHub: [github.com/judyailab/coinsifter](https://github.com/JudyaiLab/coinsifter)
- Blog: [judyailab.com](https://judyailab.com)
- X: [@JudyaiLab](https://x.com/judyailab)
