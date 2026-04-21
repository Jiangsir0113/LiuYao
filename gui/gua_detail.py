from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QColor
from core.data_models import StockInfo, FullReport
from core.liuyao_engine import LiuYaoEngine
from core.gua_analyzer import GuaAnalyzer
from core.trend_predictor import TrendPredictor
from core.report_builder import ReportBuilder

_CONCLUSION_COLOR = {
    "强烈推荐": ("#e74c3c", "#fdecea"),
    "可以关注": ("#e67e22", "#fef3e2"),
    "谨慎观望": ("#f39c12", "#fef9e7"),
    "继续观望": ("#7f8c8d", "#f2f3f4"),
    "暂不介入": ("#2980b9", "#eaf4fb"),
    "不宜买入": ("#27ae60", "#eafaf1"),
}

_CARD_STYLE = """
    QFrame {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
"""

_SECTION_TITLE_STYLE = "color: #2c3e50; font-size: 13px; font-weight: bold; padding: 4px 0;"


class _AnalysisThread(QThread):
    finished = pyqtSignal(object)  # FullReport
    failed = pyqtSignal(str)

    def __init__(self, stock, engine, analyzer, predictor, builder):
        super().__init__()
        self._stock = stock
        self._engine = engine
        self._analyzer = analyzer
        self._predictor = predictor
        self._builder = builder

    def run(self):
        try:
            gua = self._engine.qigua(self._stock.code)
            rigan_wuxing = self._engine.get_rigan_wuxing()
            analysis = self._analyzer.analyze(gua, rigan_wuxing)
            trend = self._predictor.predict(self._stock.code)
            report = self._builder.build(self._stock, gua, analysis, trend)
            self.finished.emit(report)
        except Exception as e:
            self.failed.emit(str(e))


def _make_card(parent_layout: QVBoxLayout) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setStyleSheet(_CARD_STYLE)
    inner = QVBoxLayout(card)
    inner.setContentsMargins(14, 12, 14, 12)
    inner.setSpacing(8)
    parent_layout.addWidget(card)
    return card, inner


def _section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
    lbl.setStyleSheet(_SECTION_TITLE_STYLE)
    return lbl


class GuaDetail(QWidget):
    def __init__(self):
        super().__init__()
        self._engine = LiuYaoEngine()
        self._analyzer = GuaAnalyzer()
        self._predictor = TrendPredictor()
        self._builder = ReportBuilder()
        self._thread = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f5f6fa; }")
        outer.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet("background: #f5f6fa;")
        scroll.setWidget(container)

        self._main_layout = QVBoxLayout(container)
        self._main_layout.setContentsMargins(12, 12, 12, 12)
        self._main_layout.setSpacing(10)

        # 标题区
        self._title = QLabel("请从左侧选择股票")
        self._title.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        self._title.setStyleSheet("color: #2c3e50; padding: 4px 2px;")
        self._main_layout.addWidget(self._title)

        # 状态提示
        self._hint = QLabel("")
        self._hint.setFont(QFont("Microsoft YaHei", 11))
        self._hint.setStyleSheet("color: #888;")
        self._main_layout.addWidget(self._hint)

        # 六爻卦象卡片
        _, gua_inner = _make_card(self._main_layout)
        gua_inner.addWidget(_section_title("六爻卦象"))

        self._gua_name_label = QLabel("")
        self._gua_name_label.setFont(QFont("Microsoft YaHei", 13))
        self._gua_name_label.setStyleSheet("color: #8e44ad; font-weight: bold;")
        gua_inner.addWidget(self._gua_name_label)

        self._yao_table = QTableWidget(6, 4)
        self._yao_table.setHorizontalHeaderLabels(["爻位", "爻象", "六亲", "六神"])
        self._yao_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._yao_table.verticalHeader().setVisible(False)
        self._yao_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._yao_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._yao_table.setShowGrid(False)
        self._yao_table.setAlternatingRowColors(True)
        self._yao_table.setFixedHeight(210)
        self._yao_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e8e8e8;
                border-radius: 6px;
                font-family: 'Consolas', 'Microsoft YaHei';
                font-size: 13px;
                outline: none;
            }
            QTableWidget::item { padding: 5px 10px; }
            QHeaderView::section {
                background: #f0f0f0;
                border: none;
                border-bottom: 1px solid #ddd;
                padding: 5px 10px;
                font-family: 'Microsoft YaHei';
                font-weight: bold;
                color: #555;
            }
            QTableWidget { alternate-background-color: #fafafa; }
        """)
        gua_inner.addWidget(self._yao_table)

        self._yong_shen_label = QLabel("")
        self._yong_shen_label.setFont(QFont("Microsoft YaHei", 11))
        self._yong_shen_label.setStyleSheet("color: #555; padding-top: 2px;")
        gua_inner.addWidget(self._yong_shen_label)

        self._reasons_label = QLabel("")
        self._reasons_label.setFont(QFont("Microsoft YaHei", 11))
        self._reasons_label.setStyleSheet("color: #666; line-height: 1.6;")
        self._reasons_label.setWordWrap(True)
        gua_inner.addWidget(self._reasons_label)

        self._liuyao_conclusion = QLabel("")
        self._liuyao_conclusion.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self._liuyao_conclusion.setStyleSheet("color: #2c3e50; padding-top: 2px;")
        gua_inner.addWidget(self._liuyao_conclusion)

        # 技术面卡片
        _, trend_inner = _make_card(self._main_layout)
        trend_inner.addWidget(_section_title("技术面分析"))

        self._indicator_label = QLabel("")
        self._indicator_label.setFont(QFont("Consolas", 11))
        self._indicator_label.setStyleSheet("color: #555; background: #f8f9fa; border-radius: 4px; padding: 6px 8px;")
        trend_inner.addWidget(self._indicator_label)

        self._signals_label = QLabel("")
        self._signals_label.setFont(QFont("Microsoft YaHei", 11))
        self._signals_label.setStyleSheet("color: #555;")
        self._signals_label.setWordWrap(True)
        trend_inner.addWidget(self._signals_label)

        self._trend_conclusion = QLabel("")
        self._trend_conclusion.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self._trend_conclusion.setStyleSheet("color: #2c3e50; padding-top: 2px;")
        trend_inner.addWidget(self._trend_conclusion)

        # 综合结论卡片
        _, conc_inner = _make_card(self._main_layout)
        conc_inner.addWidget(_section_title("综合结论"))
        self._conclusion_label = QLabel("")
        self._conclusion_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self._conclusion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._conclusion_label.setFixedHeight(56)
        self._conclusion_label.setStyleSheet("border-radius: 8px;")
        conc_inner.addWidget(self._conclusion_label)

        self._main_layout.addStretch()

    def show_analysis(self, stock: StockInfo):
        self._title.setText(f"{stock.name}  {stock.code}")
        self._hint.setText("正在起卦并计算技术指标，请稍候...")
        self._gua_name_label.setText("")
        self._yong_shen_label.setText("")
        self._reasons_label.setText("")
        self._liuyao_conclusion.setText("")
        self._indicator_label.setText("")
        self._signals_label.setText("")
        self._trend_conclusion.setText("")
        self._conclusion_label.setText("")
        self._conclusion_label.setStyleSheet("border-radius: 8px;")
        for row in range(6):
            for col in range(4):
                self._yao_table.setItem(row, col, QTableWidgetItem(""))

        self._thread = _AnalysisThread(
            stock, self._engine, self._analyzer, self._predictor, self._builder
        )
        self._thread.finished.connect(self._on_analysis_done)
        self._thread.failed.connect(self._on_analysis_failed)
        self._thread.start()

    @pyqtSlot(object)
    def _on_analysis_done(self, report: FullReport):
        self._hint.setText("")
        gua = report.gua_xiang
        analysis = report.gua_analysis
        trend = report.trend

        self._gua_name_label.setText(f"【{gua.gua_name}】")

        # 爻表格，从上爻到初爻显示
        yao_symbol = {"阳": "━━━━━━", "阴": "━━  ━━"}
        yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        for display_row, i in enumerate(range(5, -1, -1)):
            is_dong = (i + 1) == gua.dong_yao
            symbol = yao_symbol.get(gua.yao_list[i], gua.yao_list[i])
            name_text = yao_names[i] + ("  ◀动" if is_dong else "")

            items = [
                QTableWidgetItem(name_text),
                QTableWidgetItem(symbol),
                QTableWidgetItem(analysis.liu_qin[i]),
                QTableWidgetItem(analysis.liu_shen[i]),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if is_dong:
                    item.setForeground(QColor("#e74c3c"))
                    item.setFont(QFont("Consolas", 12, QFont.Weight.Bold) if col == 1
                                 else QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
                else:
                    item.setFont(QFont("Consolas", 12) if col == 1
                                 else QFont("Microsoft YaHei", 11))
                self._yao_table.setItem(display_row, col, item)

        self._yong_shen_label.setText(f"用神：{analysis.yong_shen}（{analysis.yong_shen_state}）")
        self._reasons_label.setText("\n".join(f"• {r}" for r in analysis.reasons))

        conclusion_color = {"宜买": "#e74c3c", "观望": "#e67e22", "不宜": "#27ae60"}
        c_color = conclusion_color.get(analysis.conclusion, "#2c3e50")
        self._liuyao_conclusion.setText(f"六爻结论：{analysis.conclusion}")
        self._liuyao_conclusion.setStyleSheet(f"color: {c_color}; font-weight: bold; padding-top: 2px;")

        # 技术面
        self._indicator_label.setText(
            f"MA5: {trend.ma5:.2f}   MA20: {trend.ma20:.2f}   "
            f"MACD: {trend.macd:+.4f}   RSI: {trend.rsi:.1f}"
        )
        self._signals_label.setText("\n".join(f"• {s}" for s in trend.signals))
        trend_color = {"上涨": "#e74c3c", "下跌": "#27ae60", "横盘": "#888"}
        t_color = trend_color.get(trend.trend, "#2c3e50")
        self._trend_conclusion.setText(f"趋势判断：{trend.trend}")
        self._trend_conclusion.setStyleSheet(f"color: {t_color}; font-weight: bold; padding-top: 2px;")

        # 综合结论
        colors = _CONCLUSION_COLOR.get(report.final_conclusion, ("#333", "#f5f5f5"))
        self._conclusion_label.setText(report.final_conclusion)
        self._conclusion_label.setStyleSheet(
            f"color: {colors[0]}; background: {colors[1]}; "
            f"border: 2px solid {colors[0]}; border-radius: 8px; font-weight: bold;"
        )

    @pyqtSlot(str)
    def _on_analysis_failed(self, error: str):
        self._hint.setText(f"分析失败：{error}")
