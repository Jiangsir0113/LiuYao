from dataclasses import dataclass


@dataclass
class StockInfo:
    code: str
    name: str
    volume: float
    change_pct: float


@dataclass
class GuaXiang:
    upper_gua: int
    lower_gua: int
    dong_yao: int
    yao_list: list[str]
    gua_name: str


@dataclass
class GuaAnalysis:
    liu_qin: list[str]
    liu_shen: list[str]
    yong_shen: str
    yong_shen_state: str
    reasons: list[str]
    conclusion: str


@dataclass
class TrendPrediction:
    ma5: float
    ma20: float
    macd: float
    rsi: float
    trend: str
    signals: list[str]


@dataclass
class FullReport:
    stock: StockInfo
    gua_xiang: GuaXiang
    gua_analysis: GuaAnalysis
    trend: TrendPrediction
    final_conclusion: str
