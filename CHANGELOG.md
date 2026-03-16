# Changelog

All notable changes to CoinSifter will be documented in this file.

## [1.8.0] - 2026-03-16

### Added
- Demo mode (`--demo`) — try CoinSifter without a Binance API key
- ATR (Average True Range) indicator support
- EMA Cross indicator with golden/death cross detection
- EMA slope conditions (`slope_up`, `slope_down`)
- MACD zero-line conditions (`above_zero`, `below_zero`)
- KD `k_above_d` condition
- Unit tests for all indicators and filter conditions
- Dynamic version reading from VERSION file

### Changed
- Updated indicator documentation to match all implemented conditions
- Strategy template now lists all available indicators and conditions accurately
- `--interval` parameter is in minutes (e.g., `--interval 240` for 4 hours)

## [1.7.0] - 2026-03-10

### Added
- Multi-timeframe scanning (15m, 1h, 4h, 1d)
- YAML-based strategy system
- Volume indicator with configurable multiplier
- KD (Stochastic) indicator with golden/death cross
- Bollinger Bands indicator
- Verbose mode (`-v`) with detailed indicator output

### Changed
- Switched to closed candle logic (`iloc[-2]`) to prevent false signals
- Improved rate limiting between API calls

## [1.6.0] - 2026-03-01

### Added
- Initial open-source release
- RSI, EMA, MACD indicators
- AND/OR filter mode
- Binance USDT pair scanning with volume threshold
- Config file support (YAML)
- Stablecoin exclusion list
