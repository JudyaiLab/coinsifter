# Contributing to CoinSifter

Thanks for your interest in contributing to CoinSifter! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/coinsifter.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy config: `cp config.example.yaml config.yaml`

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit config
cp config.example.yaml config.yaml
# Edit config.yaml with your Binance API key (read-only permissions are sufficient)

# Run CLI
python coinsifter.py

# Run in demo mode (no API key needed)
python coinsifter.py --demo

# Run tests
python -m pytest tests/ -v
```

## How to Contribute

### Reporting Bugs

- Use the [Bug Report](../../issues/new?template=bug_report.md) issue template
- Include your Python version, OS, and steps to reproduce

### Suggesting Features

- Use the [Feature Request](../../issues/new?template=feature_request.md) issue template
- Describe the use case and expected behavior

### Submitting Code

1. Make your changes on a feature branch
2. Follow existing code style (PEP 8)
3. Add or update tests for your changes
4. Run `python -m pytest tests/ -v` and ensure all tests pass
5. Submit a Pull Request with a clear description

## Project Structure

```
coinsifter/
├── coinsifter.py          # CLI entry point
├── core/
│   ├── scanner.py         # Binance API scanner (via CCXT)
│   ├── indicators.py      # Technical indicators (RSI, EMA, MACD, BB, KD, ATR)
│   └── filter_engine.py   # Strategy filter logic (AND/OR)
├── strategies/            # YAML strategy configs
├── tests/                 # Unit tests
└── config.example.yaml    # Config template
```

## Adding New Indicators

1. Add calculation function to `core/indicators.py`
2. Register in `filter_engine.py` `check_condition()` function
3. Add to strategy template `strategies/custom_template.yaml`
4. Update the indicator table in `README.md`
5. Add tests in `tests/`

## Adding New Exchange Support

CoinSifter uses [CCXT](https://github.com/ccxt/ccxt) for exchange connectivity. To add a new exchange:

1. Modify `core/scanner.py` to accept exchange parameter
2. Update `config.example.yaml` with exchange options
3. Test with the new exchange's API

## Code Style

- Python 3.10+
- Follow PEP 8
- Use type hints where practical
- Keep functions focused and under 50 lines
- Comments in English

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
