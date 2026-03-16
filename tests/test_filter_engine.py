"""Tests for core/filter_engine.py — condition checking logic"""
import pytest
from core.filter_engine import check_condition


class TestRSIConditions:
    def test_rsi_between_pass(self):
        data = {'rsi': 55.0}
        passed, reason = check_condition(data, {
            'indicator': 'rsi', 'condition': 'between', 'value': [50, 70]
        })
        assert passed is True
        assert '55.0' in reason

    def test_rsi_between_fail(self):
        data = {'rsi': 80.0}
        passed, _ = check_condition(data, {
            'indicator': 'rsi', 'condition': 'between', 'value': [50, 70]
        })
        assert passed is False

    def test_rsi_above(self):
        data = {'rsi': 75.0}
        passed, _ = check_condition(data, {
            'indicator': 'rsi', 'condition': 'above', 'value': 70
        })
        assert passed is True

    def test_rsi_below(self):
        data = {'rsi': 25.0}
        passed, _ = check_condition(data, {
            'indicator': 'rsi', 'condition': 'below', 'value': 30
        })
        assert passed is True

    def test_rsi_none(self):
        data = {'rsi': None}
        passed, _ = check_condition(data, {
            'indicator': 'rsi', 'condition': 'above', 'value': 50
        })
        assert passed is False


class TestEMAConditions:
    def test_price_above_ema(self):
        data = {'ema50': 100.0, 'price': 110.0}
        passed, _ = check_condition(data, {
            'indicator': 'ema', 'condition': 'price_above', 'period': 50
        })
        assert passed is True

    def test_price_below_ema(self):
        data = {'ema50': 100.0, 'price': 90.0}
        passed, _ = check_condition(data, {
            'indicator': 'ema', 'condition': 'price_below', 'period': 50
        })
        assert passed is True

    def test_slope_up(self):
        data = {'ema20': 105.0, 'ema20_slope': 'up', 'price': 110.0}
        passed, _ = check_condition(data, {
            'indicator': 'ema', 'condition': 'slope_up', 'period': 20
        })
        assert passed is True

    def test_slope_down(self):
        data = {'ema20': 105.0, 'ema20_slope': 'down', 'price': 100.0}
        passed, _ = check_condition(data, {
            'indicator': 'ema', 'condition': 'slope_down', 'period': 20
        })
        assert passed is True

    def test_ema_none(self):
        data = {'ema50': None, 'price': 100.0}
        passed, _ = check_condition(data, {
            'indicator': 'ema', 'condition': 'price_above', 'period': 50
        })
        assert passed is False


class TestMACDConditions:
    def test_bullish(self):
        data = {'macd_bullish': True, 'macd_above_zero': True}
        passed, _ = check_condition(data, {
            'indicator': 'macd', 'condition': 'bullish'
        })
        assert passed is True

    def test_bearish(self):
        data = {'macd_bullish': False, 'macd_above_zero': False}
        passed, _ = check_condition(data, {
            'indicator': 'macd', 'condition': 'bearish'
        })
        assert passed is True

    def test_above_zero(self):
        data = {'macd_bullish': True, 'macd_above_zero': True}
        passed, _ = check_condition(data, {
            'indicator': 'macd', 'condition': 'above_zero'
        })
        assert passed is True

    def test_below_zero(self):
        data = {'macd_bullish': False, 'macd_above_zero': False}
        passed, _ = check_condition(data, {
            'indicator': 'macd', 'condition': 'below_zero'
        })
        assert passed is True


class TestBBConditions:
    def test_above_lower(self):
        data = {'price': 105.0, 'bb_lower': 95.0, 'bb_upper': 110.0}
        passed, _ = check_condition(data, {
            'indicator': 'bb', 'condition': 'above_lower'
        })
        assert passed is True

    def test_below_upper(self):
        data = {'price': 105.0, 'bb_lower': 95.0, 'bb_upper': 110.0}
        passed, _ = check_condition(data, {
            'indicator': 'bb', 'condition': 'below_upper'
        })
        assert passed is True

    def test_inside(self):
        data = {'price': 105.0, 'bb_lower': 95.0, 'bb_upper': 110.0}
        passed, _ = check_condition(data, {
            'indicator': 'bb', 'condition': 'inside'
        })
        assert passed is True

    def test_outside(self):
        data = {'price': 120.0, 'bb_lower': 95.0, 'bb_upper': 110.0}
        passed, _ = check_condition(data, {
            'indicator': 'bb', 'condition': 'inside'
        })
        assert passed is False

    def test_bb_none(self):
        data = {'price': None, 'bb_lower': None, 'bb_upper': None}
        passed, _ = check_condition(data, {
            'indicator': 'bb', 'condition': 'inside'
        })
        assert passed is False


class TestKDConditions:
    def test_oversold(self):
        data = {'stoch_k': 15.0, 'stoch_d': 18.0}
        passed, _ = check_condition(data, {
            'indicator': 'kd', 'condition': 'oversold'
        })
        assert passed is True

    def test_overbought(self):
        data = {'stoch_k': 85.0, 'stoch_d': 82.0}
        passed, _ = check_condition(data, {
            'indicator': 'kd', 'condition': 'overbought'
        })
        assert passed is True

    def test_golden_cross(self):
        data = {'stoch_k': 30.0, 'stoch_d': 28.0, 'kd_golden_cross': True, 'kd_death_cross': False}
        passed, _ = check_condition(data, {
            'indicator': 'kd', 'condition': 'golden_cross'
        })
        assert passed is True

    def test_k_above_d(self):
        data = {'stoch_k': 60.0, 'stoch_d': 55.0, 'kd_k_above_d': True}
        passed, _ = check_condition(data, {
            'indicator': 'kd', 'condition': 'k_above_d'
        })
        assert passed is True


class TestVolumeConditions:
    def test_above_average(self):
        data = {'volume_ratio': 2.0}
        passed, _ = check_condition(data, {
            'indicator': 'volume', 'condition': 'above_average', 'multiplier': 1.5
        })
        assert passed is True

    def test_below_average(self):
        data = {'volume_ratio': 1.0}
        passed, _ = check_condition(data, {
            'indicator': 'volume', 'condition': 'above_average', 'multiplier': 1.5
        })
        assert passed is False


class TestEMACrossConditions:
    def test_golden_cross(self):
        data = {'ema20': 110.0, 'ema50': 100.0, 'ema_golden_cross': True}
        passed, _ = check_condition(data, {
            'indicator': 'ema_cross', 'condition': 'golden_cross'
        })
        assert passed is True

    def test_ema20_above_50(self):
        data = {'ema20': 110.0, 'ema50': 100.0, 'ema20_above_50': True}
        passed, _ = check_condition(data, {
            'indicator': 'ema_cross', 'condition': 'ema20_above_50'
        })
        assert passed is True

    def test_ema20_below_50(self):
        data = {'ema20': 90.0, 'ema50': 100.0, 'ema20_above_50': False}
        passed, _ = check_condition(data, {
            'indicator': 'ema_cross', 'condition': 'ema20_below_50'
        })
        assert passed is True


class TestATRConditions:
    def test_above(self):
        data = {'atr': 5.0}
        passed, _ = check_condition(data, {
            'indicator': 'atr', 'condition': 'above', 'value': 3.0
        })
        assert passed is True

    def test_atr_none(self):
        data = {'atr': None}
        passed, _ = check_condition(data, {
            'indicator': 'atr', 'condition': 'above', 'value': 3.0
        })
        assert passed is False


class TestUnknownCondition:
    def test_unknown_indicator(self):
        passed, reason = check_condition({}, {
            'indicator': 'fake', 'condition': 'whatever'
        })
        assert passed is False
        assert 'Unknown' in reason

    def test_unknown_condition_on_valid_indicator(self):
        data = {'rsi': 50.0}
        passed, reason = check_condition(data, {
            'indicator': 'rsi', 'condition': 'nonexistent', 'value': 50
        })
        # Falls through all conditions, returns Unknown
        assert passed is False
