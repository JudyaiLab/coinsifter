"""
CoinSifter — Multi-condition filter engine
Supports AND/OR logic with YAML-based configuration
"""
from .indicators import fetch_klines, compute_indicators


def check_condition(indicator_data: dict, filter_cfg: dict) -> tuple[bool, str]:
    """
    Check if a single filter condition is met.
    Returns (passed, reason_string).
    Note: all comparisons wrapped with bool() to avoid numpy.bool_ serialization issues.
    """
    indicator = filter_cfg['indicator']
    condition = filter_cfg['condition']
    value = filter_cfg.get('value')
    period = filter_cfg.get('period', 14)
    multiplier = filter_cfg.get('multiplier', 1.5)

    if indicator == 'rsi':
        rsi_val = indicator_data.get('rsi')
        if rsi_val is None:
            return False, "RSI data insufficient"

        if condition == 'between':
            low, high = value[0], value[1]
            passed = bool(low <= rsi_val <= high)
            return passed, f"RSI={rsi_val:.1f} {'in' if passed else 'not in'} [{low},{high}]"
        elif condition == 'above':
            passed = bool(rsi_val > value)
            return passed, f"RSI={rsi_val:.1f} {'>' if passed else '<='} {value}"
        elif condition == 'below':
            passed = bool(rsi_val < value)
            return passed, f"RSI={rsi_val:.1f} {'<' if passed else '>='} {value}"

    elif indicator == 'ema':
        ema_key = f'ema{period}'
        ema_val = indicator_data.get(ema_key)
        price = indicator_data.get('price')
        if ema_val is None or price is None:
            return False, f"EMA{period} data insufficient"

        if condition == 'price_above':
            passed = bool(price > ema_val)
            return passed, f"Price={price:.6g} {'>' if passed else '<='} EMA{period}={ema_val:.6g}"
        elif condition == 'price_below':
            passed = bool(price < ema_val)
            return passed, f"Price={price:.6g} {'<' if passed else '>='} EMA{period}={ema_val:.6g}"
        elif condition == 'slope_up':
            slope = indicator_data.get(f'{ema_key}_slope')
            passed = bool(slope == 'up')
            return passed, f"EMA{period} slope {'up' if passed else 'down'}"
        elif condition == 'slope_down':
            slope = indicator_data.get(f'{ema_key}_slope')
            passed = bool(slope == 'down')
            return passed, f"EMA{period} slope {'down' if passed else 'up'}"

    elif indicator == 'macd':
        bullish = indicator_data.get('macd_bullish', False)
        above_zero = indicator_data.get('macd_above_zero', False)
        cross_str = 'bullish' if bullish else 'bearish'
        zero_str = 'MACD > 0' if above_zero else 'MACD < 0'
        if condition == 'bullish':
            passed = bool(bullish)
            return passed, f"MACD {cross_str} | {zero_str}"
        elif condition == 'bearish':
            passed = bool(not bullish)
            return passed, f"MACD {cross_str} | {zero_str}"
        elif condition == 'above_zero':
            passed = bool(above_zero)
            return passed, f"MACD {zero_str} | {cross_str}"
        elif condition == 'below_zero':
            passed = bool(not above_zero)
            return passed, f"MACD {zero_str} | {cross_str}"

    elif indicator == 'ema_cross':
        ema20 = indicator_data.get('ema20')
        ema50 = indicator_data.get('ema50')
        val_str = f"EMA20={ema20:.6g} EMA50={ema50:.6g}" if ema20 and ema50 else "EMA data insufficient"
        if condition == 'golden_cross':
            passed = bool(indicator_data.get('ema_golden_cross', False))
            return passed, f"{val_str} {'golden cross' if passed else 'no cross'}"
        elif condition == 'death_cross':
            passed = bool(indicator_data.get('ema_death_cross', False))
            return passed, f"{val_str} {'death cross' if passed else 'no cross'}"
        elif condition == 'ema20_above_50':
            passed = bool(indicator_data.get('ema20_above_50', False))
            return passed, f"{val_str} EMA20 {'>' if passed else '<='} EMA50"
        elif condition == 'ema20_below_50':
            passed = bool(not indicator_data.get('ema20_above_50', True))
            return passed, f"{val_str} EMA20 {'<' if passed else '>='} EMA50"

    elif indicator == 'bb':
        price = indicator_data.get('price')
        bb_lower = indicator_data.get('bb_lower')
        bb_upper = indicator_data.get('bb_upper')
        if price is None or bb_lower is None or bb_upper is None:
            return False, "Bollinger Bands data insufficient"

        if condition == 'above_lower':
            passed = bool(price > bb_lower)
            return passed, f"Price {'>' if passed else '<='} BB lower"
        elif condition == 'below_upper':
            passed = bool(price < bb_upper)
            return passed, f"Price {'<' if passed else '>='} BB upper"
        elif condition == 'inside':
            passed = bool(bb_lower < price < bb_upper)
            return passed, f"Price {'inside' if passed else 'outside'} BB channel"

    elif indicator == 'kd':
        k_val = indicator_data.get('stoch_k')
        d_val = indicator_data.get('stoch_d')
        if k_val is None:
            return False, "KD data insufficient"

        if condition == 'oversold':
            threshold = value if value else 20
            passed = bool(k_val < threshold)
            return passed, f"K={k_val:.1f} {'<' if passed else '>='} {threshold} (oversold)"
        elif condition == 'overbought':
            threshold = value if value else 80
            passed = bool(k_val > threshold)
            return passed, f"K={k_val:.1f} {'>' if passed else '<='} {threshold} (overbought)"
        elif condition == 'golden_cross':
            passed = bool(indicator_data.get('kd_golden_cross', False))
            return passed, f"KD {'golden cross' if passed else 'no cross'} (K={k_val:.1f})"
        elif condition == 'death_cross':
            passed = bool(indicator_data.get('kd_death_cross', False))
            return passed, f"KD {'death cross' if passed else 'no cross'} (K={k_val:.1f})"
        elif condition == 'k_above_d':
            passed = bool(indicator_data.get('kd_k_above_d', False))
            return passed, f"KD K {'>' if passed else '<='} D (K={k_val:.1f} D={d_val:.1f})"

    elif indicator == 'volume':
        vol_ratio = indicator_data.get('volume_ratio', 0)
        if condition == 'above_average':
            passed = bool(vol_ratio >= multiplier)
            return passed, f"Vol ratio={vol_ratio:.1f}x {'>=' if passed else '<'} {multiplier}x"

    elif indicator == 'atr':
        atr_val = indicator_data.get('atr')
        if atr_val is None:
            return False, "ATR data insufficient"
        if condition == 'above':
            passed = bool(atr_val > value)
            return passed, f"ATR={atr_val:.6g} {'>' if passed else '<='} {value}"

    return False, f"Unknown condition: {indicator}.{condition}"


def evaluate_filters(exchange, symbol: str, filters: list,
                     mode: str = "and") -> tuple[bool, list]:
    """
    Evaluate all filter conditions for a single symbol.
    Returns (overall_passed, detailed_results_list).
    """
    # Group by timeframe to avoid fetching duplicate klines
    tf_groups = {}
    for f in filters:
        tf = f.get('timeframe', '4h')
        if tf not in tf_groups:
            tf_groups[tf] = []
        tf_groups[tf].append(f)

    # Fetch klines and compute indicators for each timeframe
    tf_data = {}
    for tf, tf_filters in tf_groups.items():
        try:
            df = fetch_klines(exchange, symbol, tf)
        except Exception as e:
            return False, [{'filter': f"fetch {tf}", 'passed': False, 'reason': str(e)}]

        # Collect needed indicators for this timeframe
        needed = []
        for f in tf_filters:
            ind = f['indicator']
            entry = {'name': ind}
            if 'period' in f:
                entry['period'] = f['period']
            if 'multiplier' in f:
                entry['multiplier'] = f['multiplier']
            if 'std' in f:
                entry['std'] = f['std']
            needed.append(entry)

        tf_data[tf] = compute_indicators(df, needed)

    # Check each condition
    results = []
    for f in filters:
        tf = f.get('timeframe', '4h')
        data = tf_data.get(tf, {})
        passed, reason = check_condition(data, f)
        results.append({
            'indicator': f['indicator'],
            'timeframe': tf,
            'condition': f['condition'],
            'passed': bool(passed),
            'reason': reason,
        })

    # Determine overall result
    if mode == "and":
        overall = all(r['passed'] for r in results)
    else:  # or
        overall = any(r['passed'] for r in results)

    return overall, results
