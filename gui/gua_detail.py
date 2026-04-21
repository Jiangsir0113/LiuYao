from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.data_models import StockInfo
from core.liuyao_engine import LiuYaoEngine
from core.gua_analyzer import GuaAnalyzer
from core.trend_predictor import TrendPredictor
from core.report_builder import ReportBuilder

_COLOR_MAP = {
    "强烈推荐": "#c0392b",
    "可以关注": "#e67e22",
    "谨慎观望": "#f39c12",
    "继续观望": "#7f8c8d",
    "暂不介入": "#2980b9",
    "不宜买入": "#27ae60",
}


class GuaDetail(QWidget):
    def __init__(self):
        super().__init__()
        self._engine = LiuYaoEngine()
        self._analyzer = GuaAnalyzer()
        self._predictor = TrendPredictor()
        self._builder = ReportBuilder()
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)

        self._title = QLabel("请从左侧选择股票")
        self._title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self._layout.addWidget(self._title)

        self._gua_text = QTextEdit()
        self._gua_text.setReadOnly(True)
        self._gua_text.setFixedHeight(200)
        self._layout.addWidget(self._gua_text)

        self._trend_text = QTextEdit()
        self._trend_text.setReadOnly(True)
        self._trend_text.setFixedHeight(120)
        self._layout.addWidget(self._trend_text)

        self._conclusion_label = QLabel("")
        self._conclusion_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self._conclusion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._conclusion_label.setFixedHeight(50)
        self._layout.addWidget(self._conclusion_label)
        self._layout.addStretch()

    def show_analysis(self, stock: StockInfo):
        self._title.setText(f"【{stock.code}】{stock.name}")
        self._gua_text.setText("正在起卦分析...")
        self._trend_text.setText("正在计算技术指标...")
        self._conclusion_label.setText("")

        try:
            gua = self._engine.qigua()
            rigan_wuxing = self._engine.get_rigan_wuxing()
            analysis = self._analyzer.analyze(gua, rigan_wuxing)
            trend = self._predictor.predict(stock.code)
            report = self._builder.build(stock, gua, analysis, trend)

            yao_lines = []
            for i in range(5, -1, -1):
                marker = "← 动爻" if (i + 1) == gua.dong_yao else ""
                yao_lines.append(
                    f"  {i+1}爻  {gua.yao_list[i]}  {analysis.liu_qin[i]}  {analysis.liu_shen[i]} {marker}"
                )
            gua_content = (
                f"卦名：{gua.gua_name}\n\n"
                + "\n".join(yao_lines)
                + f"\n\n用神：{analysis.yong_shen}（{analysis.yong_shen_state}）\n"
                + "\n".join(f"  • {r}" for r in analysis.reasons)
                + f"\n\n六爻结论：{analysis.conclusion}"
            )
            self._gua_text.setText(gua_content)

            trend_content = (
                f"MA5: {trend.ma5:.2f}  MA20: {trend.ma20:.2f}  "
                f"MACD: {trend.macd:.4f}  RSI: {trend.rsi:.1f}\n\n"
                + "\n".join(f"  • {s}" for s in trend.signals)
                + f"\n\n趋势判断：{trend.trend}"
            )
            self._trend_text.setText(trend_content)

            color = _COLOR_MAP.get(report.final_conclusion, "#333333")
            self._conclusion_label.setText(f"综合结论：{report.final_conclusion}")
            self._conclusion_label.setStyleSheet(
                f"color: {color}; border: 2px solid {color}; border-radius: 6px;"
            )

        except Exception as e:
            self._gua_text.setText(f"分析失败：{e}")
