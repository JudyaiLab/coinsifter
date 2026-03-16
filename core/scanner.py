"""
CoinSifter — Full market scanner engine
Fetches all USDT pairs from Binance API, sorted by volume
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
    Scan all USDT pairs and return those above the volume threshold.
    sort_by: "volume" = by volume, "gainers" = top gainers, "losers" = top losers
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
