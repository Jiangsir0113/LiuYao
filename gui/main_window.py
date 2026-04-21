from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from gui.filter_panel import FilterPanel
from gui.result_table import ResultTable
from gui.gua_detail import GuaDetail


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("六爻选股分析工具")
        self.setMinimumSize(1200, 700)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.filter_panel = FilterPanel()
        self.result_table = ResultTable()
        self.gua_detail = GuaDetail()

        splitter.addWidget(self.filter_panel)
        splitter.addWidget(self.result_table)
        splitter.addWidget(self.gua_detail)
        splitter.setSizes([220, 400, 580])

        layout.addWidget(splitter)

        self.filter_panel.search_requested.connect(self.result_table.load_stocks)
        self.result_table.stock_selected.connect(self.gua_detail.show_analysis)
        self.result_table.loading_changed.connect(self.filter_panel.set_loading)
