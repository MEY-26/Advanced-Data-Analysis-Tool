"""
Multiple Regression Analysis (MRA) sekmesi.
"""

import html
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
    QCheckBox,
    QTextBrowser,
    QApplication,
    QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont

from utils import format_number, replace_scientific_notation
from gui.tabs.base_analysis_tab import BaseAnalysisTab
from gui.widgets import MplCanvas
from analysis.mra import run_mra
from analysis.common import generate_warnings, warnings_to_text
from plots import plot_distribution_panel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
from scipy import stats as scipy_stats


class MraTab(BaseAnalysisTab):
    """Multiple Regression Analysis arayüzü."""
    
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
        left_layout.addWidget(QLabel("Response:"))
        self.response_combo = QComboBox()
        left_layout.addWidget(self.response_combo)
        left_layout.addWidget(QLabel("Predictor'lar (çoklu seçim):"))
        self.predictor_list = QListWidget()
        self.predictor_list.setSelectionMode(self.predictor_list.SelectionMode.MultiSelection)
        self.predictor_list.setMinimumHeight(140)
        left_layout.addWidget(self.predictor_list)
        self.cb_interactions = QCheckBox("Etkileşimler")
        self.cb_interactions.setChecked(False)
        left_layout.addWidget(self.cb_interactions)
        self.run_btn = QPushButton("Analizi Çalıştır")
        self.run_btn.clicked.connect(self._run_analysis)
        left_layout.addWidget(self.run_btn)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        right = QTabWidget()
        self.summary_browser = QTextBrowser()
        self.summary_browser.setFont(QFont("Consolas", 9))
        right.addTab(self.summary_browser, "Model Özeti")
        self.anova_table = QTableView()
        self.anova_model = QStandardItemModel()
        self.anova_table.setModel(self.anova_model)
        right.addTab(self.anova_table, "ANOVA")
        self.coef_table = QTableView()
        self.coef_model = QStandardItemModel()
        self.coef_table.setModel(self.coef_model)
        right.addTab(self.coef_table, "Katsayılar")
        self.vif_table = QTableView()
        self.vif_model = QStandardItemModel()
        self.vif_table.setModel(self.vif_model)
        right.addTab(self.vif_table, "VIF")
        self.residual_container = QWidget()
        self.residual_layout = QVBoxLayout(self.residual_container)
        self.residual_layout.addWidget(MplCanvas())
        right.addTab(self.residual_container, "Residual Plots")
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
            pred_opts = all_numeric or all_cols
            resp_default = (self._column_roles.get("response", []) if self._column_roles else [])[:1]
            pred_default = [c for c in self._column_roles.get("numeric_factors", []) if c in df.columns] if self._column_roles else []
            self.response_combo.clear()
            self.response_combo.addItems(resp_opts or ["(yok)"])
            if resp_default and resp_default[0] in resp_opts:
                self.response_combo.setCurrentText(resp_default[0])
            self.predictor_list.clear()
            self.predictor_list.addItems(pred_opts or ["(yok)"])
            for c in pred_default:
                for i in range(self.predictor_list.count()):
                    if self.predictor_list.item(i).text() == c:
                        self.predictor_list.item(i).setSelected(True)
                        break
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        response = self.response_combo.currentText()
        predictors = [i.text() for i in self.predictor_list.selectedItems()]
        if response not in self._df.columns:
            self.status_label.setText("Response kolonu seçin.")
            return
        if not predictors or response in predictors:
            predictors = [c for c in predictors if c != response and c in self._df.columns]
        if not predictors:
            self.status_label.setText("En az 1 predictor seçin (response hariç).")
            return
        self.run_btn.setEnabled(False)
        self.status_label.setText("Analiz çalışıyor...")
        QApplication.processEvents()
        try:
            result = run_mra(
                self._df,
                response,
                predictors,
                include_interactions=self.cb_interactions.isChecked(),
            )
            self._results = result
            model = result["model"]
            summary_text = replace_scientific_notation(result["summary_text"])
            html_content = f'<pre style="font-family: Consolas, \'Courier New\', monospace; font-size: 10pt;">{html.escape(summary_text)}</pre>'
            self.summary_browser.setHtml(html_content)
            self._fill_table(self.anova_model, result["anova_df"].reset_index())
            self._fill_table(self.coef_model, result["coefficients"])
            self._fill_table(self.vif_model, result["vif"])
            fig_res = plt.figure(figsize=(10, 4))
            ax1 = fig_res.add_subplot(121)
            ax1.scatter(model.fittedvalues, model.resid, alpha=0.6)
            ax1.axhline(0, color="red", linestyle="--")
            ax1.set_xlabel("Fitted")
            ax1.set_ylabel("Residuals")
            ax1.set_title("Residual vs Fitted")
            ax2 = fig_res.add_subplot(122)
            scipy_stats.probplot(model.resid, dist="norm", plot=ax2)
            ax2.set_title("Q-Q Plot")
            fig_res.tight_layout()
            self._set_canvas(self.residual_layout, fig_res)
            fig_dist = plot_distribution_panel(self._df[response], f"Dağılım: {response}")
            self._set_canvas(self.dist_layout, fig_dist)
            warnings_list = generate_warnings(
                model=model,
                anova_df=result["anova_df"],
                vif_df=result["vif"],
                n_obs=len(self._df),
            )
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
