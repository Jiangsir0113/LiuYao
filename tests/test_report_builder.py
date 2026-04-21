from core.report_builder import ReportBuilder
from core.data_models import StockInfo, GuaXiang, GuaAnalysis, TrendPrediction

def _make_analysis(conclusion: str) -> GuaAnalysis:
    return GuaAnalysis(
        liu_qin=["父母","妻财","子孙","官鬼","兄弟","父母"],
        liu_shen=["青龙","朱雀","勾陈","腾蛇","白虎","玄武"],
        yong_shen="2爻（妻财）", yong_shen_state="旺",
        reasons=["测试"], conclusion=conclusion
    )

def _make_trend(trend: str) -> TrendPrediction:
    return TrendPrediction(ma5=10.5, ma20=10.0, macd=0.1, rsi=50.0,
                           trend=trend, signals=["测试信号"])

def test_yimai_shangzhang():
    builder = ReportBuilder()
    stock = StockInfo("000001", "测试", 10000.0, 1.0)
    gua = GuaXiang(1, 8, 2, ["阳"]*6, "乾坤")
    report = builder.build(stock, gua, _make_analysis("宜买"), _make_trend("上涨"))
    assert report.final_conclusion == "强烈推荐"

def test_yimai_hengpan():
    builder = ReportBuilder()
    stock = StockInfo("000001", "测试", 10000.0, 1.0)
    gua = GuaXiang(1, 8, 2, ["阳"]*6, "乾坤")
    report = builder.build(stock, gua, _make_analysis("宜买"), _make_trend("横盘"))
    assert report.final_conclusion == "可以关注"

def test_buyi_any():
    builder = ReportBuilder()
    stock = StockInfo("000001", "测试", 10000.0, 1.0)
    gua = GuaXiang(1, 8, 2, ["阳"]*6, "乾坤")
    for trend in ["上涨", "横盘", "下跌"]:
        report = builder.build(stock, gua, _make_analysis("不宜"), _make_trend(trend))
        assert report.final_conclusion == "不宜买入"

def test_guanwang_xiazha():
    builder = ReportBuilder()
    stock = StockInfo("000001", "测试", 10000.0, 1.0)
    gua = GuaXiang(1, 8, 2, ["阳"]*6, "乾坤")
    report = builder.build(stock, gua, _make_analysis("观望"), _make_trend("下跌"))
    assert report.final_conclusion == "暂不介入"
