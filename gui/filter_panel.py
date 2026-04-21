from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QDoubleSpinBox,
    QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import pyqtSignal


class FilterPanel(QWidget):
    search_requested = pyqtSignal(float, float, float)  # min_vol, min_chg, max_chg

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        group = QGroupBox("筛选条件")
        form = QFormLayout(group)

        self._vol_spin = QDoubleSpinBox()
        self._vol_spin.setRange(0, 999999)
        self._vol_spin.setValue(5000)
        self._vol_spin.setSuffix(" 万")
        self._vol_spin.setDecimals(0)
        form.addRow("成交量 ≥", self._vol_spin)

        self._min_chg = QDoubleSpinBox()
        self._min_chg.setRange(-20, 0)
        self._min_chg.setValue(-3.0)
        self._min_chg.setSuffix(" %")
        form.addRow("涨幅下限", self._min_chg)

        self._max_chg = QDoubleSpinBox()
        self._max_chg.setRange(0, 20)
        self._max_chg.setValue(7.0)
        self._max_chg.setSuffix(" %")
        form.addRow("涨幅上限", self._max_chg)

        layout.addWidget(group)

        self._btn = QPushButton("开始筛选")
        self._btn.setFixedHeight(36)
        self._btn.clicked.connect(self._on_search)
        layout.addWidget(self._btn)
        layout.addStretch()

    def _on_search(self):
        self.search_requested.emit(
            self._vol_spin.value(),
            self._min_chg.value(),
            self._max_chg.value(),
        )
