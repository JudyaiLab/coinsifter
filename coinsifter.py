#!/usr/bin/env python3
"""
CoinSifter — 你設條件，自動抓幣
主程式入口
"""
import argparse
import sys
import time
import yaml
from pathlib import Path

from core.scanner import create_exchange, scan_all_usdt
from core.filter_engine import evaluate_filters


def load_config(path: str) -> dict:
    """載入 YAML 設定檔"""
    p = Path(path)
    if not p.exists():
        print(f"❌ 找不到設定檔: {path}")
        print("請複製 config.example.yaml 為 config.yaml 並填入你的資訊")
        sys.exit(1)
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_strategy(path: str) -> dict:
    """載入策略檔"""
    p = Path(path)
    if not p.exists():
        print(f"❌ 找不到策略檔: {path}")
        sys.exit(1)
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_scan(config: dict, strategy: dict = None, verbose: bool = False):
    """執行一次完整掃描"""
    # 建立交易所連線
    api_key = config.get('binance', {}).get('api_key', '')
    api_secret = config.get('binance', {}).get('api_secret', '')
    exchange = create_exchange(api_key, api_secret)

    # 掃描設定
    scan_cfg = config.get('scan', {})
    min_vol = scan_cfg.get('min_volume_24h', 50_000_000)
    top_n = scan_cfg.get('top_n', 50)
    quote = scan_cfg.get('quote_currency', 'USDT')

    # 篩選條件（策略優先，否則用 config）
    if strategy:
        filters = strategy.get('filters', [])
        filter_mode = strategy.get('filter_mode', 'and')
        direction = strategy.get('direction', '')
        print(f"📋 策略: {strategy.get('name', '自訂')} ({direction})")
    else:
        filters = config.get('filters', [])
        filter_mode = config.get('filter_mode', 'and')
        direction = ''

    if not filters:
        print("❌ 沒有定義篩選條件，請在 config.yaml 或策略檔中設定 filters")
        return []

    print(f"🔍 掃描 Binance {quote} 交易對（最低成交量: {min_vol/1e6:.0f}M）...")
    candidates = scan_all_usdt(exchange, min_vol, top_n, quote)

    if candidates.empty:
        print("⚠️ 沒有找到符合成交量門檻的交易對")
        return []

    print(f"📊 找到 {len(candidates)} 個候選幣種，開始篩選...\n")

    # 逐一篩選
    passed_list = []
    for _, row in candidates.iterrows():
        symbol = row['symbol']
        if verbose:
            print(f"  分析 {symbol}...", end=" ")

        try:
            passed, details = evaluate_filters(exchange, symbol, filters, filter_mode)
        except Exception as e:
            if verbose:
                print(f"❌ 錯誤: {e}")
            continue

        if passed:
            if verbose:
                print("✅ 通過")
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

        # Rate limit 緩衝
        time.sleep(0.5)

    # 輸出結果
    print(f"\n{'='*50}")
    if passed_list:
        print(f"🎯 共 {len(passed_list)} 個幣種通過篩選:\n")
        for i, r in enumerate(passed_list, 1):
            print(f"  {i}. {r['symbol']}")
            print(f"     價格: {r['price']:.6g} | 24h量: {r['volume_24h']/1e6:.1f}M | 漲跌: {r['change_pct']:.1f}%")
            for d in r['details']:
                if d['passed']:
                    print(f"     ✅ {d['reason']}")
    else:
        print("😔 沒有幣種通過所有篩選條件")
    print(f"{'='*50}")

    return passed_list


def run_demo():
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


def main():
    parser = argparse.ArgumentParser(
        description='CoinSifter — 你設條件，自動抓幣',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python coinsifter.py                          # 使用 config.yaml 掃描
  python coinsifter.py -s strategies/custom_template.yaml  # 使用自訂策略
  python coinsifter.py -v                       # 詳細模式
  python coinsifter.py --loop                   # 持續掃描模式
        """)
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='設定檔路徑（預設: config.yaml）')
    parser.add_argument('-s', '--strategy', default=None,
                        help='策略檔路徑（覆蓋 config 中的 filters）')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='顯示詳細分析過程')
    parser.add_argument('--demo', action='store_true',
                        help='Demo mode — run with sample data, no API key needed')
    parser.add_argument('--loop', action='store_true',
                        help='持續掃描模式（按 config 中的排程間隔）')
    parser.add_argument('--interval', type=int, default=None,
                        help='掃描間隔（分鐘），覆蓋 config 設定')

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
        interval = args.interval or 240  # 預設 4 小時
        print(f"🔄 持續掃描模式（每 {interval} 分鐘）")
        print("按 Ctrl+C 停止\n")
        try:
            while True:
                run_scan(config, strategy, args.verbose)
                print(f"\n⏰ 下次掃描: {interval} 分鐘後...\n")
                time.sleep(interval * 60)
        except KeyboardInterrupt:
            print("\n👋 已停止掃描")
    else:
        run_scan(config, strategy, args.verbose)


if __name__ == '__main__':
    main()
