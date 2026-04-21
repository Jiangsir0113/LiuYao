from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QColor, QFont
from core.stock_filter import StockFilter
from core.data_models import StockInfo


class _FetchThread(QThread):
    finished = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, min_vol, min_chg, max_chg):
        super().__init__()
        self._min_vol = min_vol
        self._min_chg = min_chg
        self._max_chg = max_chg

    def run(self):
        try:
            stocks = StockFilter().fetch_and_filter(
                self._min_vol, self._min_chg, self._max_chg
            )
            self.finished.emit(stocks)
        except Exception as e:
            self.failed.emit(str(e))


class ResultTable(QWidget):
    stock_selected = pyqtSignal(object)
    loading_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._stocks: list[StockInfo] = []
        self._thread = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        self._status = QLabel("点击「开始筛选」获取候选股票")
        self._status.setFont(QFont("Microsoft YaHei", 11))
        self._status.setStyleSheet("color: #555; padding: 2px 0;")
        layout.addWidget(self._status)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # 不确定进度（滚动条）
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)
        self._progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
                background: #eee;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
            }
        """)
        self._progress.hide()
        layout.addWidget(self._progress)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["代码", "名称", "成交量(万)", "涨幅(%)"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                outline: none;
            }
            QTableWidget::item { padding: 6px 8px; }
            QTableWidget::item:selected {
                background-color: #d6eaf8;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                border: none;
                border-bottom: 1px solid #ddd;
                padding: 6px 8px;
                font-weight: bold;
                color: #555;
            }
            QTableWidget { alternate-background-color: #fafafa; }
        """)
        self._table.itemSelectionChanged.connect(self._on_selection)
        layout.addWidget(self._table)

    def load_stocks(self, min_vol: float, min_chg: float, max_chg: float):
        self._status.setText("正在获取全市场行情数据，请稍候...")
        self._progress.show()
        self._table.setRowCount(0)
        self.loading_changed.emit(True)

        self._thread = _FetchThread(min_vol, min_chg, max_chg)
        self._thread.finished.connect(self._on_fetch_done)
        self._thread.failed.connect(self._on_fetch_failed)
        self._thread.start()

    @pyqtSlot(list)
    def _on_fetch_done(self, stocks: list):
        self._stocks = stocks
        self._progress.hide()
        self.loading_changed.emit(False)
        self._status.setText(f"共筛选出 {len(stocks)} 只候选股票，点击查看六爻分析")
        for row, s in enumerate(stocks):
            self._table.insertRow(row)
            code_item = QTableWidgetItem(s.code)
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, code_item)
            self._table.setItem(row, 1, QTableWidgetItem(s.name))
            vol_item = QTableWidgetItem(f"{s.volume:,.0f}")
            vol_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 2, vol_item)
            chg_item = QTableWidgetItem(f"{s.change_pct:+.2f}%")
            chg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            chg_item.setForeground(QColor("#e74c3c") if s.change_pct > 0 else QColor("#27ae60"))
            self._table.setItem(row, 3, chg_item)

    @pyqtSlot(str)
    def _on_fetch_failed(self, error: str):
        self._progress.hide()
        self.loading_changed.emit(False)
        self._status.setText(f"获取数据失败：{error}")

    def _on_selection(self):
        if not self._table.selectedItems():
            return
        row = self._table.currentRow()
        if 0 <= row < len(self._stocks):
            self.stock_selected.emit(self._stocks[row])
