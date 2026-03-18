"""
Discriminant Function Analysis (DFA) sekmesi.
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
    QTextBrowser,
    QApplication,
    QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from utils import format_number
from gui.tabs.base_analysis_tab import BaseAnalysisTab
from gui.widgets import MplCanvas
from analysis.dfa import run_dfa
from analysis.common import generate_warnings, warnings_to_text
from plots import plot_dfa_scatter
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class DfaTab(BaseAnalysisTab):
    """Discriminant Function Analysis arayüzü."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        self.warning_banner = QLabel("")
        self.warning_banner.setVisible(False)
        self.warning_banner.setWordWrap(True)
        right_container = QWidget()
        right_main_layout = QVBoxLayout(right_container)
        right_main_layout.setContentsMargins(0, 0, 0, 0)
        right_main_layout.addWidget(self.warning_banner)
        
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Grup değişkeni:"))
        self.group_combo = QComboBox()
        left_layout.addWidget(self.group_combo)
        left_layout.addWidget(QLabel("Özellik değişkenleri (çoklu seçim):"))
        self.feature_list = QListWidget()
        self.feature_list.setSelectionMode(self.feature_list.SelectionMode.MultiSelection)
        self.feature_list.setMinimumHeight(140)
        left_layout.addWidget(self.feature_list)
        self.run_btn = QPushButton("Analizi Çalıştır")
        self.run_btn.clicked.connect(self._run_analysis)
        left_layout.addWidget(self.run_btn)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        right = QTabWidget()
        self.summary_browser = QTextBrowser()
        right.addTab(self.summary_browser, "Özet")
        self.confusion_table = QTableView()
        self.confusion_model = QStandardItemModel()
        self.confusion_table.setModel(self.confusion_model)
        right.addTab(self.confusion_table, "Sınıflandırma")
        self.coef_table = QTableView()
        self.coef_model = QStandardItemModel()
        self.coef_table.setModel(self.coef_model)
        right.addTab(self.coef_table, "Katsayılar")
        self.scatter_container = QWidget()
        self.scatter_layout = QVBoxLayout(self.scatter_container)
        self.scatter_layout.addWidget(MplCanvas())
        right.addTab(self.scatter_container, "Skor Grafiği")
        self.warnings_browser = QTextBrowser()
        right.addTab(self.warnings_browser, "Uyarılar")
        right_main_layout.addWidget(right)
        
        left.setMinimumWidth(240)
        scroll = QScrollArea()
        scroll.setWidget(left)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(scroll, 1)
        layout.addWidget(right_container, 3)
    
    def set_data(self, df) -> None:
        super().set_data(df)
        if df is not None and not df.empty:
            all_numeric = df.select_dtypes(include=["number"]).columns.tolist()
            all_cols = list(df.columns)
            cat_cols = [c for c in all_cols if c not in all_numeric or df[c].nunique() < 20]
            if not cat_cols:
                cat_cols = all_cols
            group_default = [c for c in self._column_roles.get("categorical_factors", []) if c in df.columns] if self._column_roles else []
            feature_default = [c for c in self._column_roles.get("numeric_factors", []) if c in df.columns] if self._column_roles else []
            self.group_combo.clear()
            self.group_combo.addItems(cat_cols or ["(yok)"])
            if group_default and group_default[0] in cat_cols:
                self.group_combo.setCurrentText(group_default[0])
            self.feature_list.clear()
            self.feature_list.addItems(all_numeric or all_cols)
            for c in feature_default:
                for i in range(self.feature_list.count()):
                    if self.feature_list.item(i).text() == c:
                        self.feature_list.item(i).setSelected(True)
                        break
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        group_col = self.group_combo.currentText()
        features = [i.text() for i in self.feature_list.selectedItems()]
        if group_col not in self._df.columns:
            self.status_label.setText("Grup kolonu seçin.")
            return
        if not features:
            self.status_label.setText("En az 1 özellik seçin.")
            return
        self.run_btn.setEnabled(False)
        self.status_label.setText("Analiz çalışıyor...")
        QApplication.processEvents()
        try:
            result = run_dfa(self._df, group_col, features)
            self._results = result
            summary_parts = [
                f"DFA: {group_col} ~ {', '.join(features)}",
                f"Doğruluk: {result['accuracy']:.4f}",
                f"Wilks Lambda: {result['wilks_lambda']:.4f}",
                "\nEigenvalue (açıklanan varyans oranı):",
                result["eigenvalues"].to_string(),
                "\nSınıflandırma Raporu:",
                result["classification_report"],
            ]
            self.summary_browser.setText("\n".join(summary_parts))
            self._fill_table(self.confusion_model, result["confusion_matrix"])
            self._fill_table(self.coef_model, result["coefficients"])
            scores_df = result["discriminant_scores"]
            if scores_df is not None and len(scores_df.columns) >= 2:
                fig = plot_dfa_scatter(scores_df, group_col)
                self._set_canvas(self.scatter_layout, fig)
            warnings_list = generate_warnings(n_obs=len(self._df))
            self.warnings_browser.setText(warnings_to_text(warnings_list) if warnings_list else "Uyarı yok.")
            critical = [w for sev, w in warnings_list if sev == "KRITIK"]
            warn = [w for sev, w in warnings_list if sev == "UYARI"]
            if critical:
                self.warning_banner.setText("ANALIZ GECERSIZ: " + "; ".join(critical[:2]))
                self.warning_banner.setStyleSheet("background: #cc0000; color: white; font-weight: bold; padding: 8px; font-size: 13px;")
                self.warning_banner.setVisible(True)
            elif warn:
                self.warning_banner.setText("DIKKAT: " + "; ".join(warn[:2]))
                self.warning_banner.setStyleSheet("background: #ccaa00; color: black; font-weight: bold; padding: 8px; font-size: 13px;")
                self.warning_banner.setVisible(True)
            else:
                self.warning_banner.setVisible(False)
            self.status_label.setText("Analiz tamamlandı.")
            self.status_label.setStyleSheet("color: #008800; font-weight: bold;")
        except Exception as e:
            self.warning_banner.setVisible(False)
            self.status_label.setText(f"Hata: {str(e)[:80]}")
            self.status_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            self.summary_browser.setText(str(e))
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
