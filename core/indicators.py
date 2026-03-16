"""
CoinSifter — Technical indicator calculation module
Supports RSI, MACD, EMA, BB, KD, ATR, Volume (pure Python implementation)
"""
import pandas as pd
import ccxt
import numpy as np


def fetch_klines(exchange: ccxt.binance, symbol: str, timeframe: str,
                 limit: int = 500) -> pd.DataFrame:
    """Fetch OHLCV candlestick data from the exchange"""
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    return df


def calc_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate RSI using Wilder's smoothing method"""
    delta = df['c'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Wilder's exponential smoothing for subsequent values
    for i in range(period, len(avg_gain)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_ema(df: pd.DataFrame, period: int = 50) -> pd.Series:
    """Calculate Exponential Moving Average"""
    return df['c'].ewm(span=period, adjust=False).mean()


def calc_sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Calculate Simple Moving Average"""
    return df['c'].rolling(window=period).mean()


def calc_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26,
              signal: int = 9) -> pd.DataFrame:
    """Calculate MACD, returns DataFrame with MACD line, histogram, and signal"""
    ema_fast = df['c'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['c'].ewm(span=slow, adjust=False).mean()

    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal

    result = pd.DataFrame({
        'MACD_12_26_9': macd,
        'MACDh_12_26_9': macd_hist,
        'MACDs_12_26_9': macd_signal
    }, index=df.index)
    return result


def calc_bbands(df: pd.DataFrame, period: int = 20,
                std: float = 2.0) -> pd.DataFrame:
    """Calculate Bollinger Bands, returns DataFrame with lower, middle, upper"""
    sma = df['c'].rolling(window=period).mean()
    std_dev = df['c'].rolling(window=period).std()

    bb_upper = sma + (std_dev * std)
    bb_mid = sma
    bb_lower = sma - (std_dev * std)

    result = pd.DataFrame({
        'BBL_20_2.0': bb_lower,
        'BBM_20_2.0': bb_mid,
        'BBU_20_2.0': bb_upper
    }, index=df.index)
    return result


def calc_kd(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
    """Calculate Stochastic KD oscillator"""
    low_min = df['l'].rolling(window=k_period).min()
    high_max = df['h'].rolling(window=k_period).max()

    k = 100 * (df['c'] - low_min) / (high_max - low_min)
    d = k.rolling(window=d_period).mean()

    result = pd.DataFrame({
        'STOCHk_14_3': k,
        'STOCHd_14_3': d
    }, index=df.index)
    return result


def calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    high_low = df['h'] - df['l']
    high_close = np.abs(df['h'] - df['c'].shift())
    low_close = np.abs(df['l'] - df['c'].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr


def calc_vol_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Calculate volume moving average"""
    return df['v'].rolling(window=period).mean()


def compute_indicators(df: pd.DataFrame, indicators_config: list) -> dict:
    """
    Compute all requested indicators and return latest values as a dict.
    indicators_config: [{'name': 'rsi', 'period': 14}, ...]
    Uses the previous closed candle (iloc[-2]) to prevent false signals
    from incomplete candles.
    """
    results = {}
    # Use the last closed candle (iloc[-2]) to avoid false signals from incomplete candles
    closed_idx = -2 if len(df) >= 2 else -1
    last = df.iloc[closed_idx]
    prev = df.iloc[closed_idx - 1] if len(df) >= abs(closed_idx) + 1 else last

    for cfg in indicators_config:
        name = cfg['name']
        period = cfg.get('period', 14)

        if name == 'rsi':
            series = calc_rsi(df, period)
            val = series.iloc[closed_idx]
            results['rsi'] = round(val, 2) if pd.notna(val) else None

        elif name == 'ema':
            # Check if we have enough candles (need at least period + buffer)
            min_candles = period + 10
            if len(df) < min_candles:
                results[f'ema{period}'] = None
                results[f'ema{period}_prev'] = None
                results[f'ema{period}_slope'] = None
            else:
                series = calc_ema(df, period)
                val = series.iloc[closed_idx]
                prev_val = series.iloc[closed_idx - 1] if len(series) >= abs(closed_idx) + 1 else None
                results[f'ema{period}'] = round(val, 8) if pd.notna(val) else None
                results[f'ema{period}_prev'] = round(prev_val, 8) if prev_val is not None and pd.notna(prev_val) else None
                results[f'ema{period}_slope'] = 'up' if (prev_val is not None and pd.notna(prev_val) and val > prev_val) else 'down'

        elif name == 'macd':
            macd_df = calc_macd(df)
            if macd_df is not None and not macd_df.empty:
                cols = macd_df.columns
                idx = -2 if len(macd_df) >= 2 else -1
                macd_val = macd_df[cols[0]].iloc[idx]
                signal_val = macd_df[cols[2]].iloc[idx]
                hist_val = macd_df[cols[1]].iloc[idx]
                results['macd'] = round(macd_val, 6) if pd.notna(macd_val) else None
                results['macd_signal'] = round(signal_val, 6) if pd.notna(signal_val) else None
                results['macd_hist'] = round(hist_val, 6) if pd.notna(hist_val) else None
                results['macd_bullish'] = bool(pd.notna(macd_val) and pd.notna(signal_val) and macd_val > signal_val)
                results['macd_above_zero'] = bool(pd.notna(macd_val) and macd_val > 0)

        elif name == 'ema_cross':
            ema20 = calc_ema(df, 20)
            ema50 = calc_ema(df, 50)
            # Use closed candle for cross detection
            if len(ema20) >= 3 and len(ema50) >= 3:
                cur_20 = ema20.iloc[-2]   # Last closed candle
                cur_50 = ema50.iloc[-2]
                prev_20 = ema20.iloc[-3]  # Previous closed candle
                prev_50 = ema50.iloc[-3]
            else:
                cur_20 = ema20.iloc[-1]
                cur_50 = ema50.iloc[-1]
                prev_20 = None
                prev_50 = None
            results['ema20'] = round(cur_20, 8) if pd.notna(cur_20) else None
            results['ema50'] = round(cur_50, 8) if pd.notna(cur_50) else None
            results['ema20_above_50'] = bool(pd.notna(cur_20) and pd.notna(cur_50) and cur_20 > cur_50)
            # Golden cross: prev EMA20 <= EMA50 and current EMA20 > EMA50
            # Requires sufficient candles for EMA50 to stabilize
            min_candles = 50
            has_sufficient_data = len(df) >= min_candles
            if prev_20 is not None and prev_50 is not None and pd.notna(prev_20) and pd.notna(prev_50) and has_sufficient_data:
                results['ema_golden_cross'] = bool(prev_20 <= prev_50 and cur_20 > cur_50)
                results['ema_death_cross'] = bool(prev_20 >= prev_50 and cur_20 < cur_50)
            else:
                results['ema_golden_cross'] = False
                results['ema_death_cross'] = False

        elif name == 'bb':
            bb_df = calc_bbands(df, period, cfg.get('std', 2.0))
            if bb_df is not None and not bb_df.empty:
                cols = bb_df.columns
                results['bb_lower'] = round(bb_df[cols[0]].iloc[closed_idx], 8) if pd.notna(bb_df[cols[0]].iloc[closed_idx]) else None
                results['bb_mid'] = round(bb_df[cols[1]].iloc[closed_idx], 8) if pd.notna(bb_df[cols[1]].iloc[closed_idx]) else None
                results['bb_upper'] = round(bb_df[cols[2]].iloc[closed_idx], 8) if pd.notna(bb_df[cols[2]].iloc[closed_idx]) else None

        elif name == 'kd':
            kd_df = calc_kd(df, period, cfg.get('d_period', 3))
            if kd_df is not None and not kd_df.empty:
                cols = kd_df.columns
                results['stoch_k'] = round(kd_df[cols[0]].iloc[closed_idx], 2) if pd.notna(kd_df[cols[0]].iloc[closed_idx]) else None
                results['stoch_d'] = round(kd_df[cols[1]].iloc[closed_idx], 2) if pd.notna(kd_df[cols[1]].iloc[closed_idx]) else None
                # Golden/death cross: compare previous closed vs current closed
                prev_k = kd_df[cols[0]].iloc[closed_idx - 1] if len(kd_df) >= abs(closed_idx) + 1 else None
                prev_d = kd_df[cols[1]].iloc[closed_idx - 1] if len(kd_df) >= abs(closed_idx) + 1 else None
                cur_k = kd_df[cols[0]].iloc[closed_idx]
                cur_d = kd_df[cols[1]].iloc[closed_idx]
                if prev_k is not None and prev_d is not None and pd.notna(prev_k) and pd.notna(prev_d):
                    results['kd_golden_cross'] = bool(prev_k <= prev_d and cur_k > cur_d)
                    results['kd_death_cross'] = bool(prev_k >= prev_d and cur_k < cur_d)
                else:
                    results['kd_golden_cross'] = False
                    results['kd_death_cross'] = False
                results['kd_k_above_d'] = bool(pd.notna(cur_k) and pd.notna(cur_d) and cur_k > cur_d)

        elif name == 'atr':
            series = calc_atr(df, period)
            results['atr'] = round(series.iloc[closed_idx], 8) if pd.notna(series.iloc[closed_idx]) else None

        elif name == 'volume':
            vol_period = cfg.get('period', 20)
            vol_ma = calc_vol_ma(df, vol_period)
            current_vol = last['v']
            avg_vol = vol_ma.iloc[closed_idx] if pd.notna(vol_ma.iloc[closed_idx]) else 0
            results['volume'] = current_vol
            results['volume_avg'] = round(avg_vol, 2) if avg_vol else 0
            results['volume_ratio'] = round(current_vol / avg_vol, 2) if avg_vol > 0 else 0

    results['price'] = last['c']
    return results
