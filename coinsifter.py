#!/usr/bin/env python3
"""
CoinSifter — You set the rules. It finds the coins.
CLI entry point
"""
import argparse
import sys
import time
import yaml
from pathlib import Path

from core.scanner import create_exchange, scan_all_usdt
from core.filter_engine import evaluate_filters


def load_config(path: str) -> dict:
    """Load YAML config file"""
    p = Path(path)
    if not p.exists():
        print(f"❌ Config file not found: {path}")
        print("Please copy config.example.yaml to config.yaml and fill in your info")
        sys.exit(1)
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_strategy(path: str) -> dict:
    """Load strategy file"""
    p = Path(path)
    if not p.exists():
        print(f"❌ Strategy file not found: {path}")
        sys.exit(1)
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_scan(config: dict, strategy: dict = None, verbose: bool = False) -> list:
    """Run a full screening scan"""
    # Create exchange connection
    api_key = config.get('binance', {}).get('api_key', '')
    api_secret = config.get('binance', {}).get('api_secret', '')
    exchange = create_exchange(api_key, api_secret)

    # Scan settings
    scan_cfg = config.get('scan', {})
    min_vol = scan_cfg.get('min_volume_24h', 50_000_000)
    top_n = scan_cfg.get('top_n', 50)
    quote = scan_cfg.get('quote_currency', 'USDT')

    # Filter conditions (strategy takes priority over config)
    if strategy:
        filters = strategy.get('filters', [])
        filter_mode = strategy.get('filter_mode', 'and')
        direction = strategy.get('direction', '')
        print(f"📋 Strategy: {strategy.get('name', 'Custom')} ({direction})")
    else:
        filters = config.get('filters', [])
        filter_mode = config.get('filter_mode', 'and')
        direction = ''

    if not filters:
        print("❌ No filter conditions defined. Set filters in config.yaml or a strategy file.")
        return []

    print(f"🔍 Scanning Binance {quote} pairs (min volume: {min_vol/1e6:.0f}M)...")
    candidates = scan_all_usdt(exchange, min_vol, top_n, quote)

    if candidates.empty:
        print("⚠️ No pairs found above the volume threshold")
        return []

    print(f"📊 Found {len(candidates)} candidates, screening...\n")

    # Screen each candidate
    passed_list = []
    for _, row in candidates.iterrows():
        symbol = row['symbol']
        if verbose:
            print(f"  Analyzing {symbol}...", end=" ")

        try:
            passed, details = evaluate_filters(exchange, symbol, filters, filter_mode)
        except Exception as e:
            if verbose:
                print(f"❌ Error: {e}")
            continue

        if passed:
            if verbose:
                print("✅ Passed")
                for d in details:
                    status = "✅" if d['passed'] else "❌"
                    print(f"    {status} {d['reason']}")
            passed_list.append({
                'symbol': symbol,
                'price': row['price'],
                'volume_24h': row['volume_24h'],
                'change_pct': row['change_pct'],
                'details': details,
            })
        else:
            if verbose:
                reasons = [d['reason'] for d in details if not d['passed']]
                print(f"❌ {', '.join(reasons[:2])}")

        # Rate limit buffer
        time.sleep(0.5)

    # Output results
    print(f"\n{'='*50}")
    if passed_list:
        print(f"🎯 {len(passed_list)} coins passed all filters:\n")
        for i, r in enumerate(passed_list, 1):
            print(f"  {i}. {r['symbol']}")
            print(f"     Price: {r['price']:.6g} | 24h Vol: {r['volume_24h']/1e6:.1f}M | Change: {r['change_pct']:.1f}%")
            for d in r['details']:
                if d['passed']:
                    print(f"     ✅ {d['reason']}")
    else:
        print("😔 No coins passed all filter conditions")
    print(f"{'='*50}")

    return passed_list


def run_demo() -> None:
    """Demo mode with sample data — no API key needed"""
    print("\n📋 Demo Mode — Sample scan results\n")

    demo_results = [
        {"symbol": "BTC/USDT", "price": 84250.5, "volume_24h": 2500_300_000,
         "change_pct": 2.4, "details": [
             {"passed": True, "reason": "RSI=65.3 in [50,70]"},
             {"passed": True, "reason": "Price 84250.5 > EMA50 82100.2"},
             {"passed": True, "reason": "MACD bullish (MACD > Signal)"},
             {"passed": True, "reason": "Volume 1.8x >= 1.5x"},
         ]},
        {"symbol": "ETH/USDT", "price": 3180.2, "volume_24h": 1200_500_000,
         "change_pct": 1.8, "details": [
             {"passed": True, "reason": "RSI=58.7 in [50,70]"},
             {"passed": True, "reason": "Price 3180.2 > EMA50 3050.8"},
             {"passed": True, "reason": "MACD bullish (MACD > Signal)"},
             {"passed": True, "reason": "Volume 2.1x >= 1.5x"},
         ]},
        {"symbol": "SOL/USDT", "price": 142.5, "volume_24h": 890_000_000,
         "change_pct": 3.2, "details": [
             {"passed": True, "reason": "RSI=62.1 in [50,70]"},
             {"passed": True, "reason": "Price 142.5 > EMA50 135.3"},
             {"passed": True, "reason": "MACD bullish (MACD > Signal)"},
             {"passed": True, "reason": "Volume 1.6x >= 1.5x"},
         ]},
    ]

    print(f"🔍 [Demo] Scanning Binance USDT pairs (min volume: 50M)...")
    print(f"📊 [Demo] Found 50 candidates, screening...\n")
    print(f"{'='*50}")
    print(f"🎯 3 coins passed all filters:\n")
    for i, r in enumerate(demo_results, 1):
        print(f"  {i}. {r['symbol']}")
        print(f"     Price: {r['price']:.6g} | 24h Vol: {r['volume_24h']/1e6:.1f}M | Change: {r['change_pct']:.1f}%")
        for d in r['details']:
            print(f"     ✅ {d['reason']}")
        print()
    print(f"{'='*50}")
    print("\n💡 To run with real data, set up config.yaml with your Binance API key.")
    print("   cp config.example.yaml config.yaml")
    print("   python coinsifter.py -v\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='CoinSifter — You set the rules. It finds the coins.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python coinsifter.py                                     # Use config.yaml
  python coinsifter.py -s strategies/custom_template.yaml  # Use custom strategy
  python coinsifter.py -v                                  # Verbose mode
  python coinsifter.py --demo                              # Demo with sample data
  python coinsifter.py --loop --interval 240               # Scan every 4 hours
        """)
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='Config file path (default: config.yaml)')
    parser.add_argument('-s', '--strategy', default=None,
                        help='Strategy file path (overrides config filters)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed indicator analysis')
    parser.add_argument('--demo', action='store_true',
                        help='Demo mode — run with sample data, no API key needed')
    parser.add_argument('--loop', action='store_true',
                        help='Continuous scan mode (runs at set intervals)')
    parser.add_argument('--interval', type=int, default=None,
                        help='Scan interval in minutes (default: 240 = 4 hours)')

    args = parser.parse_args()

    version = "1.8.0"
    try:
        vfile = Path(__file__).parent / "VERSION"
        if vfile.exists():
            version = vfile.read_text().strip()
    except Exception:
        pass

    print("=" * 50)
    print(f"🔮 CoinSifter v{version} — You set the rules. It finds the coins.")
    print("=" * 50)

    if args.demo:
        run_demo()
        return

    config = load_config(args.config)
    strategy = load_strategy(args.strategy) if args.strategy else None

    if args.loop:
        interval = args.interval or 240  # Default 4 hours
        print(f"🔄 Continuous scan mode (every {interval} minutes)")
        print("Press Ctrl+C to stop\n")
        try:
            while True:
                run_scan(config, strategy, args.verbose)
                print(f"\n⏰ Next scan in {interval} minutes...\n")
                time.sleep(interval * 60)
        except KeyboardInterrupt:
            print("\n👋 Scanning stopped")
    else:
        run_scan(config, strategy, args.verbose)


if __name__ == '__main__':
    main()
