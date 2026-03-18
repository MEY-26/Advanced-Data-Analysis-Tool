"""
Ortak GUI widget'lari.
MplCanvas, FilterBar, CollapsibleSection.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from typing import Optional, List, Dict, Any
import pandas as pd


class MplCanvas(FigureCanvasQTAgg):
    """
    Matplotlib Figure'i Qt widget olarak gosterir.
    """
    
    def __init__(self, figure: Optional[Figure] = None, parent: Optional[QWidget] = None):
        if figure is None:
            figure = Figure(figsize=(5, 4))
        super().__init__(figure)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.figure = figure
    
    def set_figure(self, figure: Figure) -> None:
        """Yeni figure atar ve gunceller."""
        self.figure = figure
        self.setParent(self.parent())
        # Canvas'i yeniden olustur
        self.deleteLater()
        new_canvas = FigureCanvasQTAgg(figure)
        new_canvas.setParent(self.parent())
        new_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Parent'a yeni canvas eklenmeli - bu sinif icinde sadece figure'i guncelleyemiyoruz
        # Bu yuzden draw_idle kullanarak mevcut canvas'ta guncelleme yapalim
        self.figure = figure
    
    def update_figure(self, figure: Figure) -> None:
        """Mevcut canvas'a yeni figure icerigi kopyalanir - basit yaklasim: parent'tan cikar, yeni canvas ekle."""
        pass  # Kullanimda parent layout'tan cikarip yeni MplCanvas eklenir


class CollapsibleSection(QWidget):
    """
    Katlanabilir panel. Basliga tiklaninca icerik gosterilir/gizlenir.
    """
    toggled = Signal(bool)
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._title = title
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        
        self._toggle_btn = QPushButton(f"▼ {title}")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setChecked(True)
        self._toggle_btn.clicked.connect(self._on_toggle)
        font = self._toggle_btn.font()
        font.setBold(True)
        self._toggle_btn.setFont(font)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._toggle_btn)
        layout.addWidget(self._content)
    
    def _on_toggle(self, checked: bool) -> None:
        self._content.setVisible(checked)
        self._toggle_btn.setText(f"{'▼' if checked else '▶'} {self._title}")
        self.toggled.emit(checked)
    
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout
    
    def add_widget(self, widget: QWidget) -> None:
        self._content_layout.addWidget(widget)
    
    def set_title(self, title: str) -> None:
        self._title = title
        self._toggle_btn.setText(f"{'▼' if self._toggle_btn.isChecked() else '▶'} {title}")


class FilterBar(QWidget):
    """
    Veri filtreleme bari. Numune, Delik, Olcum, Devir/Feed/Paso araliklari.
    QGridLayout ile hizalı sütunlar, sabit satır yüksekliği.
    """
    filter_applied = Signal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._filter_column_map = None
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        grid = QGridLayout(self)
        grid.setColumnStretch(1, 1)
        row_h = 0
        
        # Delik
        self.delik_combo = QComboBox()
        self.delik_combo.addItems(["Tümü", "kafa", "flans"])
        self.delik_combo.setMinimumWidth(100)
        grid.addWidget(QLabel("Delik:"), row_h, 0)
        grid.addWidget(self.delik_combo, row_h, 1)
        row_h += 1
        
        # Olcum
        self.olcum_combo = QComboBox()
        self.olcum_combo.addItems(["Tümü", "oval", "silindir", "konik"])
        self.olcum_combo.setMinimumWidth(100)
        grid.addWidget(QLabel("Olcum:"), row_h, 0)
        grid.addWidget(self.olcum_combo, row_h, 1)
        row_h += 1
        
        # Numune araligi
        self.numune_min = QDoubleSpinBox()
        self.numune_min.setRange(-1e9, 1e9)
        self.numune_min.setValue(-1e9)
        self.numune_min.setSpecialValueText("Min")
        self.numune_min.setMinimumWidth(80)
        self.numune_max = QDoubleSpinBox()
        self.numune_max.setRange(-1e9, 1e9)
        self.numune_max.setValue(1e9)
        self.numune_max.setSpecialValueText("Max")
        self.numune_max.setMinimumWidth(80)
        grid.addWidget(QLabel("Numune:"), row_h, 0)
        range_w = QWidget()
        range_layout = QHBoxLayout(range_w)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.addWidget(self.numune_min)
        range_layout.addWidget(QLabel("–"))
        range_layout.addWidget(self.numune_max)
        grid.addWidget(range_w, row_h, 1)
        row_h += 1
        
        # Devir
        self.devir_min = QDoubleSpinBox()
        self.devir_min.setRange(-1e9, 1e9)
        self.devir_min.setValue(-1e9)
        self.devir_min.setSpecialValueText("Min")
        self.devir_min.setMinimumWidth(80)
        self.devir_max = QDoubleSpinBox()
        self.devir_max.setRange(-1e9, 1e9)
        self.devir_max.setValue(1e9)
        self.devir_max.setSpecialValueText("Max")
        self.devir_max.setMinimumWidth(80)
        grid.addWidget(QLabel("Devir:"), row_h, 0)
        range_w2 = QWidget()
        range_layout2 = QHBoxLayout(range_w2)
        range_layout2.setContentsMargins(0, 0, 0, 0)
        range_layout2.addWidget(self.devir_min)
        range_layout2.addWidget(QLabel("–"))
        range_layout2.addWidget(self.devir_max)
        grid.addWidget(range_w2, row_h, 1)
        row_h += 1
        
        # Feed
        self.feed_min = QDoubleSpinBox()
        self.feed_min.setRange(-1e9, 1e9)
        self.feed_min.setValue(-1e9)
        self.feed_min.setSpecialValueText("Min")
        self.feed_min.setMinimumWidth(80)
        self.feed_max = QDoubleSpinBox()
        self.feed_max.setRange(-1e9, 1e9)
        self.feed_max.setValue(1e9)
        self.feed_max.setSpecialValueText("Max")
        self.feed_max.setMinimumWidth(80)
        grid.addWidget(QLabel("Feed:"), row_h, 0)
        range_w3 = QWidget()
        range_layout3 = QHBoxLayout(range_w3)
        range_layout3.setContentsMargins(0, 0, 0, 0)
        range_layout3.addWidget(self.feed_min)
        range_layout3.addWidget(QLabel("–"))
        range_layout3.addWidget(self.feed_max)
        grid.addWidget(range_w3, row_h, 1)
        row_h += 1
        
        # Paso
        self.paso_min = QDoubleSpinBox()
        self.paso_min.setRange(-1e9, 1e9)
        self.paso_min.setValue(-1e9)
        self.paso_min.setSpecialValueText("Min")
        self.paso_min.setMinimumWidth(80)
        self.paso_max = QDoubleSpinBox()
        self.paso_max.setRange(-1e9, 1e9)
        self.paso_max.setValue(1e9)
        self.paso_max.setSpecialValueText("Max")
        self.paso_max.setMinimumWidth(80)
        grid.addWidget(QLabel("Paso:"), row_h, 0)
        range_w4 = QWidget()
        range_layout4 = QHBoxLayout(range_w4)
        range_layout4.setContentsMargins(0, 0, 0, 0)
        range_layout4.addWidget(self.paso_min)
        range_layout4.addWidget(QLabel("–"))
        range_layout4.addWidget(self.paso_max)
        grid.addWidget(range_w4, row_h, 1)
        row_h += 1
        
        self.filter_btn = QPushButton("Filtrele")
        self.filter_btn.clicked.connect(self._emit_filter)
        grid.addWidget(self.filter_btn, row_h, 0, 1, 2)
    
    def _emit_filter(self) -> None:
        self.filter_applied.emit(self.get_filter_dict())
    
    def get_filter_dict(self) -> Dict[str, Any]:
        """Mevcut filtre degerlerini sozluk olarak dondurur."""
        return {
            "delik": self.delik_combo.currentText() if self.delik_combo.currentText() != "Tümü" else None,
            "olcum": self.olcum_combo.currentText() if self.olcum_combo.currentText() != "Tümü" else None,
            "numune_min": self.numune_min.value() if self.numune_min.value() > -1e9 else None,
            "numune_max": self.numune_max.value() if self.numune_max.value() < 1e9 else None,
            "devir_min": self.devir_min.value() if self.devir_min.value() > -1e9 else None,
            "devir_max": self.devir_max.value() if self.devir_max.value() < 1e9 else None,
            "feed_min": self.feed_min.value() if self.feed_min.value() > -1e9 else None,
            "feed_max": self.feed_max.value() if self.feed_max.value() < 1e9 else None,
            "paso_min": self.paso_min.value() if self.paso_min.value() > -1e9 else None,
            "paso_max": self.paso_max.value() if self.paso_max.value() < 1e9 else None,
        }

    def get_filter_column_map(self) -> Optional[Dict[str, str]]:
        """Dinamik sütun eslemesi varsa dondurur."""
        return getattr(self, "_filter_column_map", None)
    
    def set_ranges_from_data(self, df, column_roles=None) -> None:
        """DataFrame'den min/max degerleri alip spinbox'lari gunceller.
        column_roles verilirse dinamik sütun eslemesi kullanilir."""
        if df is None or df.empty:
            return
        if column_roles:
            numeric_cols = column_roles.get("numeric_factors", []) + column_roles.get("block", [])
            cat_cols = column_roles.get("categorical_factors", [])
            numeric_pairs = [
                (self.numune_min, self.numune_max),
                (self.devir_min, self.devir_max),
                (self.feed_min, self.feed_max),
                (self.paso_min, self.paso_max),
            ]
            for i, (min_spin, max_spin) in enumerate(numeric_pairs):
                col = numeric_cols[i] if i < len(numeric_cols) else None
                if col and col in df.columns:
                    vals = _pd_to_numeric(df[col])
                    if len(vals) > 0:
                        min_spin.setRange(vals.min(), vals.max())
                        max_spin.setRange(vals.min(), vals.max())
                        min_spin.setValue(vals.min())
                        max_spin.setValue(vals.max())
            cat_combos = [self.delik_combo, self.olcum_combo]
            for i, combo in enumerate(cat_combos):
                col = cat_cols[i] if i < len(cat_cols) else None
                if col and col in df.columns:
                    opts = ["Tümü"] + sorted(df[col].dropna().unique().astype(str).tolist())
                    combo.clear()
                    combo.addItems(opts)
            self._filter_column_map = self._build_filter_map(column_roles)
        else:
            self._filter_column_map = None
            for col, min_spin, max_spin in [
                ("numune", self.numune_min, self.numune_max),
                ("devir", self.devir_min, self.devir_max),
                ("feed", self.feed_min, self.feed_max),
                ("paso", self.paso_min, self.paso_max),
            ]:
                if col in df.columns:
                    vals = _pd_to_numeric(df[col])
                    if len(vals) > 0:
                        min_spin.setRange(vals.min(), vals.max())
                        max_spin.setRange(vals.min(), vals.max())
                        min_spin.setValue(vals.min())
                        max_spin.setValue(vals.max())
            if "delik" in df.columns:
                opts = ["Tümü"] + sorted(df["delik"].dropna().unique().astype(str).tolist())
                self.delik_combo.clear()
                self.delik_combo.addItems(opts)
            if "olcum" in df.columns:
                opts = ["Tümü"] + sorted(df["olcum"].dropna().unique().astype(str).tolist())
                self.olcum_combo.clear()
                self.olcum_combo.addItems(opts)

    def _build_filter_map(self, column_roles):
        """column_roles'tan filtre widget -> kolon eslemesi olusturur."""
        m = {}
        numeric_cols = column_roles.get("numeric_factors", []) + column_roles.get("block", [])
        cat_cols = column_roles.get("categorical_factors", [])
        m["numune"] = numeric_cols[0] if len(numeric_cols) > 0 else "numune"
        m["devir"] = numeric_cols[1] if len(numeric_cols) > 1 else "devir"
        m["feed"] = numeric_cols[2] if len(numeric_cols) > 2 else "feed"
        m["paso"] = numeric_cols[3] if len(numeric_cols) > 3 else "paso"
        m["delik"] = cat_cols[0] if len(cat_cols) > 0 else "delik"
        m["olcum"] = cat_cols[1] if len(cat_cols) > 1 else "olcum"
        return m


def _pd_to_numeric(series):
    """Pandas series'i numeric'e cevirir, hatalari NaN yapar."""
    return pd.to_numeric(series, errors="coerce").dropna()
