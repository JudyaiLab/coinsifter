# CoinSifter

[English](README.md) | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md)

**You set the rules. It finds the coins.**

CoinSifter is an open-source cryptocurrency screening tool that automatically scans Binance for coins matching your custom technical conditions.

## Features

- **8 Technical Indicators**: RSI, EMA, EMA Cross, MACD, Bollinger Bands, KD (Stochastic), Volume, ATR
- **Multi-Timeframe**: Screen across 4H, 1H, 15m, 1D simultaneously
- **Strategy System**: Save and load screening strategies via YAML
- **Cross-Platform**: Windows, Mac, Linux

## Quick Start

### 1. Install

```bash
git clone https://github.com/JudyaiLab/coinsifter.git
cd coinsifter
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your Binance API key (read-only permission is enough)
```

### 3. Run

```bash
# Try demo mode first (no API key needed)
python coinsifter.py --demo

# Use default config
python coinsifter.py

# Use a specific strategy
python coinsifter.py -s strategies/custom_template.yaml

# Verbose mode — see indicator details
python coinsifter.py -v

# Loop mode (scan every 4 hours, interval in minutes)
python coinsifter.py --loop --interval 240
```

## Strategy Files

Strategies are simple YAML files. See `strategies/custom_template.yaml` for the full template:

```yaml
name: "My Strategy"
filter_mode: "and"
filters:
  - indicator: rsi
    timeframe: 4h
    period: 14
    condition: between
    value: [50, 70]
  - indicator: ema
    timeframe: 4h
    period: 50
    condition: price_above
  - indicator: volume
    timeframe: 1h
    condition: above_average
    multiplier: 1.5
```

**Supported indicators** ([beginner guide](docs/indicators-guide.md)):

| Indicator | Conditions | Parameters |
|-----------|-----------|------------|
| RSI | `above`, `below`, `between` | `period` (default: 14) |
| EMA | `price_above`, `price_below`, `slope_up`, `slope_down` | `period` (default: 20) |
| MACD | `bullish`, `bearish`, `above_zero`, `below_zero` | — |
| Bollinger | `above_lower`, `below_upper`, `inside` | `period` (default: 20), `std` |
| KD | `golden_cross`, `death_cross`, `oversold`, `overbought`, `k_above_d` | `period` (default: 14) |
| Volume | `above_average` | `multiplier` (default: 1.5) |
| EMA Cross | `golden_cross`, `death_cross`, `ema20_above_50`, `ema20_below_50` | — |
| ATR | `above` | `period` (default: 14), `value` |

## Requirements

- Python 3.10+
- Binance account with API key (read-only permission) — [Create a free Binance account](https://accounts.binance.com/register?ref=956950981)
- Internet connection
- Dependencies: ccxt, numpy, pandas, pyyaml (see `requirements.txt`)

## Free vs Pro

| Feature | Free | Pro |
|---------|:----:|:---:|
| 8 Technical Indicators (RSI, EMA, MACD, BB, KD, ATR...) | ✅ | ✅ |
| Multi-Timeframe Screening | ✅ | ✅ |
| Custom Strategy (YAML) | ✅ | ✅ |
| Demo Mode | ✅ | ✅ |
| CLI Interface | ✅ | ✅ |
| Web UI (Browser Dashboard) | — | ✅ |
| Pre-built Strategies (75%+ OOS win rate) | — | ✅ |
| Telegram Notifications | — | ✅ |
| Scheduled Auto-Scan | — | ✅ |
| Docker One-Click Deploy | — | ✅ |
| Windows & Mac Launchers | — | ✅ |
| Trilingual UI (EN / 中文 / 한국어) | — | ✅ |
| Interactive Manual (HTML) | — | ✅ |

👉 [Get CoinSifter Pro](https://judyailab.com/shop/)

## License

MIT — see [LICENSE](LICENSE)

## Links

- Blog: [judyailab.com](https://judyailab.com)
- Twitter/X: [@JudyaiLab](https://x.com/judyailab)
