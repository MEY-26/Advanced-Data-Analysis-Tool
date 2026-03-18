"""
Gray Relational Analysis sekmesi.
"""

import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QComboBox,
    QListWidget,
    QPushButton,
    QTableView,
    QTabWidget,
    QLabel,
    QDoubleSpinBox,
    QRadioButton,
    QApplication,
    QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from utils import format_number
from gui.tabs.base_analysis_tab import BaseAnalysisTab
from gui.widgets import MplCanvas
from analysis.gra import run_gra
from plots import plot_gra_ranking
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class GraTab(BaseAnalysisTab):
    """Gray Relational Analysis arayüzü."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Referans seri:"))
        self.reference_combo = QComboBox()
        left_layout.addWidget(self.reference_combo)
        left_layout.addWidget(QLabel("Karşılaştırma serileri (çoklu seçim):"))
        self.comparison_list = QListWidget()
        self.comparison_list.setSelectionMode(self.comparison_list.SelectionMode.MultiSelection)
        self.comparison_list.setMinimumHeight(140)
        left_layout.addWidget(self.comparison_list)
        dir_group = QGroupBox("Yön")
        dir_layout = QVBoxLayout(dir_group)
        self.rb_larger = QRadioButton("Büyük daha iyi")
        self.rb_smaller = QRadioButton("Küçük daha iyi")
        self.rb_larger.setChecked(True)
        dir_layout.addWidget(self.rb_larger)
        dir_layout.addWidget(self.rb_smaller)
        left_layout.addWidget(dir_group)
        left_layout.addWidget(QLabel("Distinguishing coefficient (0-1):"))
        self.rho_spin = QDoubleSpinBox()
        self.rho_spin.setRange(0.01, 1.0)
        self.rho_spin.setValue(0.5)
        left_layout.addWidget(self.rho_spin)
        self.run_btn = QPushButton("Analizi Çalıştır")
        self.run_btn.clicked.connect(self._run_analysis)
        left_layout.addWidget(self.run_btn)
        self.status_label = QLabel("")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        right = QTabWidget()
        self.ranking_table = QTableView()
        self.ranking_model = QStandardItemModel()
        self.ranking_table.setModel(self.ranking_model)
        right.addTab(self.ranking_table, "Sıralama")
        self.grade_chart_container = QWidget()
        self.grade_chart_layout = QVBoxLayout(self.grade_chart_container)
        self.grade_chart_layout.addWidget(MplCanvas())
        right.addTab(self.grade_chart_container, "Grade Grafiği")
        self.norm_table = QTableView()
        self.norm_model = QStandardItemModel()
        self.norm_table.setModel(self.norm_model)
        right.addTab(self.norm_table, "Normalize Veri")
        self.coeff_table = QTableView()
        self.coeff_model = QStandardItemModel()
        self.coeff_table.setModel(self.coeff_model)
        right.addTab(self.coeff_table, "Katsayi Matrisi")
        left.setMinimumWidth(240)
        scroll = QScrollArea()
        scroll.setWidget(left)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(scroll, 1)
        layout.addWidget(right, 3)
    
    def set_data(self, df) -> None:
        super().set_data(df)
        if df is not None and not df.empty:
            all_numeric = df.select_dtypes(include=["number"]).columns.tolist()
            all_cols = list(df.columns)
            ref_opts = all_numeric or all_cols
            comp_opts = all_cols
            ref_default = (self._column_roles.get("response", []) + self._column_roles.get("numeric_factors", []))[:1] if self._column_roles else []
            comp_default = [c for c in self._column_roles.get("numeric_factors", []) if c in df.columns] if self._column_roles else []
            self.reference_combo.clear()
            self.reference_combo.addItems(ref_opts or list(df.columns))
            if ref_default and ref_default[0] in ref_opts:
                self.reference_combo.setCurrentText(ref_default[0])
            self.comparison_list.clear()
            self.comparison_list.addItems(comp_opts or list(df.columns))
            for c in comp_default:
                for i in range(self.comparison_list.count()):
                    if self.comparison_list.item(i).text() == c:
                        self.comparison_list.item(i).setSelected(True)
                        break
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        ref = self.reference_combo.currentText()
        comparisons = [i.text() for i in self.comparison_list.selectedItems()]
        if ref not in self._df.columns:
            self.status_label.setText("Referans kolonu seçin.")
            return
        if not comparisons or ref in comparisons:
            comparisons = [c for c in comparisons if c != ref and c in self._df.columns]
        if not comparisons:
            self.status_label.setText("Karşılaştırma serileri seçin (referans hariç).")
            return
        self.run_btn.setEnabled(False)
        try:
            direction = "larger_better" if self.rb_larger.isChecked() else "smaller_better"
            result = run_gra(
                self._df,
                ref,
                comparisons,
                distinguishing_coef=self.rho_spin.value(),
                direction=direction,
            )
            self._results = result
            ranking = result.get("ranking", pd.DataFrame())
            if not ranking.empty:
                self.ranking_model.setRowCount(len(ranking))
                self.ranking_model.setColumnCount(len(ranking.columns))
                self.ranking_model.setHorizontalHeaderLabels([str(c) for c in ranking.columns])
                for i in range(len(ranking)):
                    for j, c in enumerate(ranking.columns):
                        val = ranking.iloc[i, j]
                        self.ranking_model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else str(val)))
            grades = result.get("grades")
            if grades is not None and not grades.empty:
                fig = plot_gra_ranking(grades, "GRA Dereceleri")
                self._set_canvas(self.grade_chart_layout, fig)
            norm_df = result.get("normalized_df")
            if norm_df is not None and not norm_df.empty:
                self._fill_table(self.norm_model, norm_df)
            coeff_df = result.get("coefficient_matrix")
            if coeff_df is not None and not coeff_df.empty:
                self._fill_table(self.coeff_model, coeff_df)
            self.status_label.setText("Analiz tamamlandı.")
        except Exception as e:
            self.status_label.setText(f"Hata: {str(e)}")
        finally:
            self.run_btn.setEnabled(True)
    
    def _fill_table(self, model: QStandardItemModel, df: pd.DataFrame) -> None:
        model.setRowCount(len(df))
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels([str(c) for c in df.columns])
        for i in range(len(df)):
            for j, c in enumerate(df.columns):
                val = df.iloc[i, j]
                model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else str(val)))
    
    def _set_canvas(self, layout, fig) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout.addWidget(FigureCanvasQTAgg(fig))
