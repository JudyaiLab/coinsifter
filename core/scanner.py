"""
CoinSifter — 全幣種掃描引擎
從 Binance API 獲取所有 USDT 交易對，按成交量排序篩選
"""
import ccxt
import pandas as pd

STABLECOINS = {
    'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP', 'FDUSD', 'USDD',
    'PYUSD', 'EURI', 'UST', 'FRAX', 'LUSD', 'GUSD', 'SUSD', 'CUSD',
    'USTC', 'EURC', 'USDS', 'USD1', 'AEUR', 'BEUR', 'USDE', 'RLUSD',
    'USDJ', 'TRIBE',
}


def create_exchange(api_key: str = "", api_secret: str = "") -> ccxt.binance:
    config = {'enableRateLimit': True}
    if api_key and api_secret and not api_key.startswith("YOUR_"):
        config['apiKey'] = api_key
        config['secret'] = api_secret
    return ccxt.binance(config)


def scan_all_usdt(exchange: ccxt.binance, min_volume: float = 50_000_000,
                  top_n: int = 50, quote: str = "USDT",
                  sort_by: str = "volume") -> pd.DataFrame:
    """
    掃描所有 USDT 交易對，回傳符合門檻的幣種列表
    sort_by: "volume" = 成交量排行, "gainers" = 漲幅排行, "losers" = 跌幅排行
    """
    tickers = exchange.fetch_tickers()

    pairs = []
    for symbol, ticker in tickers.items():
        if f'/{quote}' not in symbol:
            continue
        base = symbol.split('/')[0]
        if base in STABLECOINS:
            continue
        vol = ticker.get('quoteVolume') or 0
        pairs.append({
            'symbol': symbol,
            'base': base,
            'price': ticker.get('last', 0),
            'volume_24h': vol,
            'change_pct': ticker.get('percentage', 0) or 0,
        })

    df = pd.DataFrame(pairs)
    if df.empty:
        return df

    df = df[df['volume_24h'] >= min_volume]

    if sort_by == "gainers":
        df = df.sort_values('change_pct', ascending=False).head(top_n)
    elif sort_by == "losers":
        df = df.sort_values('change_pct', ascending=True).head(top_n)
    else:
        df = df.sort_values('volume_24h', ascending=False).head(top_n)

    df = df.reset_index(drop=True)
    return df
