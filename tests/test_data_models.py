# tests/test_data_models.py
from core.data_models import StockInfo, GuaXiang, GuaAnalysis, TrendPrediction, FullReport

def test_stock_info_creation():
    s = StockInfo(code="600519", name="贵州茅台", volume=50000.0, change_pct=2.3)
    assert s.code == "600519"
    assert s.volume == 50000.0

def test_gua_xiang_creation():
    g = GuaXiang(
        upper_gua=6, lower_gua=3, dong_yao=3,
        yao_list=["阳","阴","阳","阴","阳","阴"],
        gua_name="水火既济"
    )
    assert len(g.yao_list) == 6
    assert g.dong_yao == 3

def test_full_report_creation():
    stock = StockInfo("000001", "平安银行", 80000.0, 1.5)
    gua = GuaXiang(1, 8, 2, ["阳","阴","阳","阴","阳","阳"], "天地否")
    analysis = GuaAnalysis(
        liu_qin=["父母","兄弟","妻财","子孙","官鬼","父母"],
        liu_shen=["青龙","朱雀","勾陈","腾蛇","白虎","玄武"],
        yong_shen="三爻",
        yong_shen_state="旺",
        reasons=["妻财爻临月令，旺相"],
        conclusion="宜买"
    )
    trend = TrendPrediction(ma5=10.5, ma20=10.0, macd=0.12, rsi=52.0,
                            trend="上涨", signals=["MA金叉"])
    report = FullReport(stock=stock, gua_xiang=gua, gua_analysis=analysis,
                        trend=trend, final_conclusion="强烈推荐")
    assert report.final_conclusion == "强烈推荐"
