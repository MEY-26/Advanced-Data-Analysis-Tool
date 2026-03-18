"""
MANOVA sekmesi.
"""

import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QListWidget,
    QPushButton,
    QTextBrowser,
    QTabWidget,
    QLabel,
    QApplication,
    QScrollArea,
)

from PySide6.QtCore import Qt
from gui.tabs.base_analysis_tab import BaseAnalysisTab
from gui.widgets import MplCanvas
from analysis.manova import run_manova
from analysis.common import generate_warnings, warnings_to_text
from plots import plot_main_effects, plot_distribution_panel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class ManovaTab(BaseAnalysisTab):
    """MANOVA arayüzü."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Response (2+ seçin):"))
        self.response_list = QListWidget()
        self.response_list.setSelectionMode(self.response_list.SelectionMode.MultiSelection)
        self.response_list.setMinimumHeight(140)
        left_layout.addWidget(self.response_list)
        left_layout.addWidget(QLabel("Faktörler:"))
        self.factor_list = QListWidget()
        self.factor_list.setSelectionMode(self.factor_list.SelectionMode.MultiSelection)
        self.factor_list.setMinimumHeight(140)
        left_layout.addWidget(self.factor_list)
        self.run_btn = QPushButton("Analizi Çalıştır")
        self.run_btn.clicked.connect(self._run_analysis)
        left_layout.addWidget(self.run_btn)
        self.status_label = QLabel("")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        self.warning_banner = QLabel("")
        self.warning_banner.setVisible(False)
        self.warning_banner.setWordWrap(True)
        right_container = QWidget()
        right_main_layout = QVBoxLayout(right_container)
        right_main_layout.setContentsMargins(0, 0, 0, 0)
        right_main_layout.addWidget(self.warning_banner)
        right = QTabWidget()
        self.result_browser = QTextBrowser()
        right.addTab(self.result_browser, "Sonuç")
        main_effects_widget = QWidget()
        self.main_effects_layout = QVBoxLayout(main_effects_widget)
        right.addTab(main_effects_widget, "Main Effects")
        self.dist_container = QWidget()
        self.dist_layout = QVBoxLayout(self.dist_container)
        self.dist_layout.addWidget(MplCanvas())
        right.addTab(self.dist_container, "Dağılım")
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
            resp_opts = all_numeric or all_cols
            factor_opts = all_cols
            resp_default = [c for c in self._column_roles.get("response", []) if c in df.columns] if self._column_roles else []
            factor_default = [c for c in (self._column_roles.get("categorical_factors", []) + self._column_roles.get("numeric_factors", [])) if c in df.columns] if self._column_roles else []
            self.response_list.clear()
            self.response_list.addItems(resp_opts or ["(yok)"])
            for c in resp_default:
                for i in range(self.response_list.count()):
                    if self.response_list.item(i).text() == c:
                        self.response_list.item(i).setSelected(True)
                        break
            self.factor_list.clear()
            self.factor_list.addItems(factor_opts or ["(yok)"])
            for c in factor_default:
                for i in range(self.factor_list.count()):
                    if self.factor_list.item(i).text() == c:
                        self.factor_list.item(i).setSelected(True)
                        break
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        responses = [i.text() for i in self.response_list.selectedItems()]
        factors = [i.text() for i in self.factor_list.selectedItems()]
        if len(responses) < 2:
            self.status_label.setText("MANOVA için en az 2 response gerekli.")
            return
        if not factors:
            self.status_label.setText("En az 1 faktör seçin.")
            return
        self.run_btn.setEnabled(False)
        try:
            result = run_manova(self._df, responses, factors)
            self._results = result
            self.result_browser.setText(result.get("summary", str(result)))
            fig_me = plot_main_effects(self._df, factors, responses[0])
            self._set_canvas(self.main_effects_layout, fig_me)
            fig_dist = plot_distribution_panel(self._df[responses[0]], f"Dağılım: {responses[0]}")
            self._set_canvas(self.dist_layout, fig_dist)
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
        except Exception as e:
            self.warning_banner.setVisible(False)
            self.status_label.setText(f"Hata: {str(e)}")
            self.result_browser.setText(str(e))
        finally:
            self.run_btn.setEnabled(True)
    
    def _set_canvas(self, layout, fig) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout.addWidget(FigureCanvasQTAgg(fig))
