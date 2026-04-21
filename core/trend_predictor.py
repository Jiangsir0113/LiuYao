import os
import akshare as ak
import pandas as pd
import numpy as np
from core.data_models import TrendPrediction

for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ.pop(_k, None)


def _ema(series: pd.Series, span: int) -> pd.Series:
    """计算指数移动平均"""
    return series.ewm(span=span, adjust=False).mean()


def _macd(closes: pd.Series):
    """计算MACD指标（纯pandas实现）"""
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line = ema12 - ema26
    signal_line = _ema(macd_line, 9)
    return macd_line, signal_line


def _rsi(closes: pd.Series, period: int = 14) -> pd.Series:
    """计算RSI指标（纯pandas实现）"""
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


class TrendPredictor:
    def predict(self, stock_code: str) -> TrendPrediction:
        """预测股票技术面走势"""
        df = self._fetch_kline(stock_code)
        return self._calculate(df)

    def _fetch_kline(self, stock_code: str) -> pd.DataFrame:
        # stock_code 已含市场前缀（如 sh600000），直接传入
        # 若不含前缀则按规则补全
        if stock_code[:2] in ("sh", "sz", "bj"):
            symbol = stock_code
        elif stock_code.startswith("6"):
            symbol = f"sh{stock_code}"
        elif stock_code.startswith("8") or stock_code.startswith("4"):
            symbol = f"bj{stock_code}"
        else:
            symbol = f"sz{stock_code}"
        df = ak.stock_zh_a_daily(symbol=symbol, adjust="qfq")
        return df.tail(60).reset_index(drop=True)

    def _calculate(self, df: pd.DataFrame) -> TrendPrediction:
        closes = df["close"].astype(float)

        # 计算移动平均线
        ma5 = float(closes.rolling(5).mean().iloc[-1])
        ma20 = float(closes.rolling(20).mean().iloc[-1])

        # 计算MACD
        macd_line, signal_line = _macd(closes)
        macd_val = float(macd_line.iloc[-1])
        macd_prev = float(macd_line.iloc[-2])
        signal_val = float(signal_line.iloc[-1])
        signal_prev = float(signal_line.iloc[-2])

        # 计算RSI
        rsi_series = _rsi(closes, 14)
        rsi = float(rsi_series.iloc[-1])

        # 生成信号
        signals = []
        score = 0

        # MA信号
        if ma5 > ma20:
            score += 1
            signals.append(f"MA5({ma5:.2f}) > MA20({ma20:.2f})，短期均线向上")
        else:
            score -= 1
            signals.append(f"MA5({ma5:.2f}) < MA20({ma20:.2f})，短期均线向下")

        # MACD信号
        if macd_prev < signal_prev and macd_val > signal_val:
            score += 1
            signals.append("MACD 金叉，动能转强")
        elif macd_prev > signal_prev and macd_val < signal_val:
            score -= 1
            signals.append("MACD 死叉，动能转弱")

        # RSI信号
        if rsi > 70:
            signals.append(f"RSI({rsi:.1f}) 超买，注意回调风险")
        elif rsi < 30:
            signals.append(f"RSI({rsi:.1f}) 超卖，存在反弹机会")
        else:
            signals.append(f"RSI({rsi:.1f}) 处于正常区间")

        # 判断趋势
        if score >= 1:
            trend = "上涨"
        elif score <= -1:
            trend = "下跌"
        else:
            trend = "横盘"

        return TrendPrediction(
            ma5=ma5, ma20=ma20, macd=macd_val, rsi=rsi,
            trend=trend, signals=signals
        )
