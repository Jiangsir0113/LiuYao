from core.data_models import StockInfo, GuaXiang, GuaAnalysis, TrendPrediction, FullReport

_CONCLUSION_MAP = {
    ("宜买", "上涨"): "强烈推荐",
    ("宜买", "横盘"): "可以关注",
    ("宜买", "下跌"): "谨慎观望",
    ("观望", "上涨"): "可以关注",
    ("观望", "横盘"): "继续观望",
    ("观望", "下跌"): "暂不介入",
}


class ReportBuilder:
    def build(
        self,
        stock: StockInfo,
        gua_xiang: GuaXiang,
        gua_analysis: GuaAnalysis,
        trend: TrendPrediction,
    ) -> FullReport:
        if gua_analysis.conclusion == "不宜":
            final = "不宜买入"
        else:
            final = _CONCLUSION_MAP.get(
                (gua_analysis.conclusion, trend.trend), "继续观望"
            )
        return FullReport(
            stock=stock,
            gua_xiang=gua_xiang,
            gua_analysis=gua_analysis,
            trend=trend,
            final_conclusion=final,
        )
