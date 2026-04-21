from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from core.stock_filter import StockFilter
from core.data_models import StockInfo


class ResultTable(QWidget):
    stock_selected = pyqtSignal(object)  # StockInfo

    def __init__(self):
        super().__init__()
        self._stocks: list[StockInfo] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._status = QLabel("点击「开始筛选」获取候选股票")
        layout.addWidget(self._status)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["代码", "名称", "成交量(万)", "涨幅(%)"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.itemSelectionChanged.connect(self._on_selection)
        layout.addWidget(self._table)

    def load_stocks(self, min_vol: float, min_chg: float, max_chg: float):
        self._status.setText("正在获取数据...")
        self._table.setRowCount(0)
        try:
            f = StockFilter()
            self._stocks = f.fetch_and_filter(min_vol, min_chg, max_chg)
            self._status.setText(f"共 {len(self._stocks)} 只候选股票，点击查看六爻分析")
            for row, s in enumerate(self._stocks):
                self._table.insertRow(row)
                self._table.setItem(row, 0, QTableWidgetItem(s.code))
                self._table.setItem(row, 1, QTableWidgetItem(s.name))
                self._table.setItem(row, 2, QTableWidgetItem(f"{s.volume:.0f}"))
                chg_item = QTableWidgetItem(f"{s.change_pct:+.2f}")
                chg_item.setForeground(QColor("red") if s.change_pct > 0 else QColor("green"))
                self._table.setItem(row, 3, chg_item)
        except Exception as e:
            self._status.setText(f"获取数据失败：{e}")

    def _on_selection(self):
        rows = self._table.selectedItems()
        if not rows:
            return
        row = self._table.currentRow()
        if 0 <= row < len(self._stocks):
            self.stock_selected.emit(self._stocks[row])
