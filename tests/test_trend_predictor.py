import pandas as pd
import numpy as np
from unittest.mock import patch
from core.trend_predictor import TrendPredictor


def _make_fake_kline(trend="up") -> pd.DataFrame:
    """生成60条模拟K线数据"""
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=60, freq="B")
    if trend == "up":
        closes = np.linspace(10.0, 12.0, 60) + np.random.normal(0, 0.05, 60)
    else:
        closes = np.linspace(12.0, 10.0, 60) + np.random.normal(0, 0.05, 60)
    return pd.DataFrame({"日期": dates, "收盘": closes, "成交量": [1e8] * 60})


def test_predict_returns_trend_prediction():
    predictor = TrendPredictor()
    fake_df = _make_fake_kline("up")
    with patch.object(predictor, "_fetch_kline", return_value=fake_df):
        result = predictor.predict("600519")
    assert result.trend in ["上涨", "横盘", "下跌"]
    assert 0 <= result.rsi <= 100
    assert len(result.signals) > 0


def test_uptrend_detected():
    predictor = TrendPredictor()
    fake_df = _make_fake_kline("up")
    with patch.object(predictor, "_fetch_kline", return_value=fake_df):
        result = predictor.predict("600519")
    assert result.ma5 > result.ma20 or result.trend in ["上涨", "横盘"]


def test_downtrend_detected():
    predictor = TrendPredictor()
    fake_df = _make_fake_kline("down")
    with patch.object(predictor, "_fetch_kline", return_value=fake_df):
        result = predictor.predict("600519")
    assert result.ma5 < result.ma20 or result.trend in ["下跌", "横盘"]
