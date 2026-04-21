from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QDoubleSpinBox,
    QPushButton, QGroupBox, QFormLayout, QLabel
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class FilterPanel(QWidget):
    search_requested = pyqtSignal(float, float, float)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(230)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        title = QLabel("六爻选股")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding-bottom: 4px;")
        layout.addWidget(title)

        group = QGroupBox("筛选条件")
        group.setStyleSheet("""
            QGroupBox {
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                font-weight: bold;
                color: #555;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
        """)
        form = QFormLayout(group)
        form.setSpacing(10)
        form.setContentsMargins(10, 14, 10, 10)

        spin_style = """
            QDoubleSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 12px;
            }
            QDoubleSpinBox:focus { border-color: #3498db; }
        """

        self._vol_spin = QDoubleSpinBox()
        self._vol_spin.setRange(0, 999999)
        self._vol_spin.setValue(5000)
        self._vol_spin.setSuffix(" 万")
        self._vol_spin.setDecimals(0)
        self._vol_spin.setStyleSheet(spin_style)
        form.addRow("成交量 ≥", self._vol_spin)

        self._min_chg = QDoubleSpinBox()
        self._min_chg.setRange(-20, 0)
        self._min_chg.setValue(-3.0)
        self._min_chg.setSuffix(" %")
        self._min_chg.setStyleSheet(spin_style)
        form.addRow("涨幅下限", self._min_chg)

        self._max_chg = QDoubleSpinBox()
        self._max_chg.setRange(0, 20)
        self._max_chg.setValue(7.0)
        self._max_chg.setSuffix(" %")
        self._max_chg.setStyleSheet(spin_style)
        form.addRow("涨幅上限", self._max_chg)

        layout.addWidget(group)

        self._btn = QPushButton("开始筛选")
        self._btn.setFixedHeight(40)
        self._btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 6px;
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3498db; }
            QPushButton:pressed { background-color: #1a6a9a; }
            QPushButton:disabled { background-color: #aaa; }
        """)
        self._btn.clicked.connect(self._on_search)
        layout.addWidget(self._btn)
        layout.addStretch()

    def set_loading(self, loading: bool):
        self._btn.setEnabled(not loading)
        self._btn.setText("获取中..." if loading else "开始筛选")

    def _on_search(self):
        self.search_requested.emit(
            self._vol_spin.value(),
            self._min_chg.value(),
            self._max_chg.value(),
        )
