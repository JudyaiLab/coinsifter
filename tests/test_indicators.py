"""Tests for core/indicators.py — technical indicator calculations"""
import pandas as pd
import numpy as np
import pytest
from core.indicators import (
    calc_rsi, calc_ema, calc_sma, calc_macd,
    calc_bbands, calc_kd, calc_atr, calc_vol_ma,
    compute_indicators,
)


def _make_df(prices, volumes=None):
    """Helper: create a DataFrame matching fetch_klines output"""
    n = len(prices)
    if volumes is None:
        volumes = [1000.0] * n
    return pd.DataFrame({
        't': pd.date_range('2026-01-01', periods=n, freq='h'),
        'o': prices,
        'h': [p * 1.01 for p in prices],
        'l': [p * 0.99 for p in prices],
        'c': prices,
        'v': volumes,
    })


class TestRSI:
    def test_rsi_range(self):
        prices = [100 + i * 0.5 for i in range(50)]
        df = _make_df(prices)
        rsi = calc_rsi(df, 14)
        last = rsi.iloc[-1]
        assert 0 <= last <= 100

    def test_rsi_uptrend_above_50(self):
        prices = [100 + i for i in range(50)]
        df = _make_df(prices)
        rsi = calc_rsi(df, 14)
        assert rsi.iloc[-1] > 50

    def test_rsi_downtrend_below_50(self):
        prices = [200 - i for i in range(50)]
        df = _make_df(prices)
        rsi = calc_rsi(df, 14)
        assert rsi.iloc[-1] < 50

    def test_rsi_custom_period(self):
        prices = [100 + i * 0.3 for i in range(50)]
        df = _make_df(prices)
        rsi7 = calc_rsi(df, 7)
        rsi21 = calc_rsi(df, 21)
        # Shorter period = more reactive
        assert not rsi7.equals(rsi21)


class TestEMA:
    def test_ema_follows_price(self):
        prices = [100 + i for i in range(50)]
        df = _make_df(prices)
        ema = calc_ema(df, 20)
        assert ema.iloc[-1] < prices[-1]  # EMA lags uptrend

    def test_ema_length(self):
        prices = [100] * 30
        df = _make_df(prices)
        ema = calc_ema(df, 10)
        assert len(ema) == 30


class TestSMA:
    def test_sma_flat(self):
        prices = [100.0] * 30
        df = _make_df(prices)
        sma = calc_sma(df, 20)
        assert abs(sma.iloc[-1] - 100.0) < 0.01


class TestMACD:
    def test_macd_columns(self):
        prices = [100 + i * 0.5 for i in range(50)]
        df = _make_df(prices)
        result = calc_macd(df)
        assert 'MACD_12_26_9' in result.columns
        assert 'MACDh_12_26_9' in result.columns
        assert 'MACDs_12_26_9' in result.columns

    def test_macd_uptrend_positive(self):
        prices = [100 + i * 2 for i in range(60)]
        df = _make_df(prices)
        result = calc_macd(df)
        assert result['MACD_12_26_9'].iloc[-1] > 0


class TestBollingerBands:
    def test_bb_columns(self):
        prices = [100 + (i % 5) for i in range(50)]
        df = _make_df(prices)
        result = calc_bbands(df, 20, 2.0)
        assert len(result.columns) == 3

    def test_bb_upper_above_lower(self):
        prices = [100 + (i % 10) for i in range(50)]
        df = _make_df(prices)
        result = calc_bbands(df, 20, 2.0)
        cols = result.columns
        assert result[cols[2]].iloc[-1] > result[cols[0]].iloc[-1]


class TestKD:
    def test_kd_range(self):
        prices = [100 + (i % 20) - 10 for i in range(50)]
        df = _make_df(prices)
        result = calc_kd(df)
        k = result.iloc[-1, 0]
        assert 0 <= k <= 100

    def test_kd_columns(self):
        prices = [100] * 30
        df = _make_df(prices)
        result = calc_kd(df)
        assert 'STOCHk_14_3' in result.columns
        assert 'STOCHd_14_3' in result.columns


class TestATR:
    def test_atr_positive(self):
        prices = [100 + (i % 10) for i in range(50)]
        df = _make_df(prices)
        atr = calc_atr(df)
        assert atr.iloc[-1] > 0


class TestVolMA:
    def test_vol_ma_flat(self):
        prices = [100] * 30
        volumes = [1000.0] * 30
        df = _make_df(prices, volumes)
        vol_ma = calc_vol_ma(df, 20)
        assert abs(vol_ma.iloc[-1] - 1000.0) < 0.01


class TestComputeIndicators:
    def test_returns_price(self):
        prices = [100 + i for i in range(50)]
        df = _make_df(prices)
        result = compute_indicators(df, [])
        assert 'price' in result

    def test_rsi_in_result(self):
        prices = [100 + i * 0.5 for i in range(50)]
        df = _make_df(prices)
        result = compute_indicators(df, [{'name': 'rsi', 'period': 14}])
        assert 'rsi' in result
        assert result['rsi'] is not None

    def test_ema_in_result(self):
        prices = [100 + i for i in range(100)]
        df = _make_df(prices)
        result = compute_indicators(df, [{'name': 'ema', 'period': 20}])
        assert 'ema20' in result

    def test_macd_in_result(self):
        prices = [100 + i * 0.5 for i in range(60)]
        df = _make_df(prices)
        result = compute_indicators(df, [{'name': 'macd'}])
        assert 'macd' in result
        assert 'macd_bullish' in result

    def test_bb_in_result(self):
        prices = [100 + (i % 5) for i in range(50)]
        df = _make_df(prices)
        result = compute_indicators(df, [{'name': 'bb', 'period': 20}])
        assert 'bb_lower' in result
        assert 'bb_upper' in result

    def test_kd_in_result(self):
        prices = [100 + (i % 20) - 10 for i in range(50)]
        df = _make_df(prices)
        result = compute_indicators(df, [{'name': 'kd'}])
        assert 'stoch_k' in result
        assert 'stoch_d' in result

    def test_volume_in_result(self):
        prices = [100] * 50
        volumes = [1000 + i * 10 for i in range(50)]
        df = _make_df(prices, volumes)
        result = compute_indicators(df, [{'name': 'volume'}])
        assert 'volume_ratio' in result

    def test_atr_in_result(self):
        prices = [100 + (i % 10) for i in range(50)]
        df = _make_df(prices)
        result = compute_indicators(df, [{'name': 'atr'}])
        assert 'atr' in result

    def test_ema_cross_in_result(self):
        prices = [100 + i for i in range(100)]
        df = _make_df(prices)
        result = compute_indicators(df, [{'name': 'ema_cross'}])
        assert 'ema20' in result
        assert 'ema50' in result
        assert 'ema20_above_50' in result
