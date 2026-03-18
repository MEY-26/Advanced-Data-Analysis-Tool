"""
Two-Way ANOVA sekmesi.
"""

import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QComboBox,
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
from PySide6.QtGui import QStandardItemModel, QStandardItem

from gui.widgets import MplCanvas
from utils import format_number
from analysis.two_way_anova import run_two_way_anova
from analysis.common import format_significance, generate_warnings, warnings_to_text
from analysis.posthoc import tukey_hsd, levene_test
from gui.tabs.base_analysis_tab import BaseAnalysisTab
from plots import plot_main_effects, plot_distribution_panel
from gui.widgets import MplCanvas

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class TwoWayTab(BaseAnalysisTab):
    """Two-Way ANOVA arayüzü."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        resp_group = QGroupBox("Response")
        resp_layout = QVBoxLayout(resp_group)
        self.response_combo = QComboBox()
        resp_layout.addWidget(self.response_combo)
        left_layout.addWidget(resp_group)
        
        factor_group = QGroupBox("Faktörler")
        factor_layout = QVBoxLayout(factor_group)
        factor_layout.addWidget(QLabel("Faktör 1:"))
        self.factor1_combo = QComboBox()
        factor_layout.addWidget(self.factor1_combo)
        factor_layout.addWidget(QLabel("Faktör 2:"))
        self.factor2_combo = QComboBox()
        factor_layout.addWidget(self.factor2_combo)
        self.cb_interaction = QCheckBox("Etkileşim")
        self.cb_interaction.setChecked(True)
        factor_layout.addWidget(self.cb_interaction)
        left_layout.addWidget(factor_group)
        
        posthoc_group = QGroupBox("Post-Hoc")
        ph_layout = QVBoxLayout(posthoc_group)
        self.cb_tukey = QCheckBox("Tukey HSD")
        self.cb_levene = QCheckBox("Levene (varyans homojenliği)")
        self.cb_tukey.setChecked(True)
        self.cb_levene.setChecked(True)
        ph_layout.addWidget(self.cb_tukey)
        ph_layout.addWidget(self.cb_levene)
        left_layout.addWidget(posthoc_group)
        
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
        anova_widget = QWidget()
        anova_layout = QVBoxLayout(anova_widget)
        self.anova_summary_label = QLabel("")
        self.anova_summary_label.setWordWrap(True)
        anova_layout.addWidget(self.anova_summary_label)
        self.anova_table = QTableView()
        anova_layout.addWidget(self.anova_table)
        self.anova_model = QStandardItemModel()
        self.anova_table.setModel(self.anova_model)
        right.addTab(anova_widget, "ANOVA")
        posthoc_widget = QWidget()
        posthoc_layout = QVBoxLayout(posthoc_widget)
        posthoc_layout.addWidget(QLabel("Levene Testi (Varyans Homojenliği):"))
        self.levene_table = QTableView()
        self.levene_model = QStandardItemModel()
        self.levene_table.setModel(self.levene_model)
        posthoc_layout.addWidget(self.levene_table)
        posthoc_layout.addWidget(QLabel("Tukey HSD:"))
        self.tukey_table = QTableView()
        self.tukey_model = QStandardItemModel()
        self.tukey_table.setModel(self.tukey_model)
        posthoc_layout.addWidget(self.tukey_table)
        posthoc_layout.addStretch()
        right.addTab(posthoc_widget, "Post-Hoc")
        main_effects_widget = QWidget()
        self.main_effects_layout = QVBoxLayout(main_effects_widget)
        right.addTab(main_effects_widget, "Main Effects")
        self.dist_container = QWidget()
        self.dist_layout = QVBoxLayout(self.dist_container)
        self.dist_layout.addWidget(MplCanvas())
        right.addTab(self.dist_container, "Dağılım")
        warn_widget = QWidget()
        warn_layout = QVBoxLayout(warn_widget)
        self.warnings_browser = QTextBrowser()
        warn_layout.addWidget(self.warnings_browser)
        right.addTab(warn_widget, "Uyarılar")
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
            resp_default = (self._column_roles.get("response", []) if self._column_roles else [])[:1]
            factor_default = (
                [c for c in self._column_roles.get("categorical_factors", []) if c in df.columns]
                + [c for c in self._column_roles.get("numeric_factors", []) if c in df.columns]
            ) if self._column_roles else []
            self.response_combo.clear()
            self.response_combo.addItems(resp_opts or ["(yok)"])
            if resp_default and resp_default[0] in resp_opts:
                self.response_combo.setCurrentText(resp_default[0])
            self.factor1_combo.clear()
            self.factor1_combo.addItems(factor_opts or ["(yok)"])
            self.factor2_combo.clear()
            self.factor2_combo.addItems(factor_opts or ["(yok)"])
            if factor_default:
                if factor_default[0] in factor_opts:
                    self.factor1_combo.setCurrentText(factor_default[0])
                if len(factor_default) > 1 and factor_default[1] in factor_opts:
                    self.factor2_combo.setCurrentText(factor_default[1])
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        response = self.response_combo.currentText()
        f1 = self.factor1_combo.currentText()
        f2 = self.factor2_combo.currentText()
        if response not in self._df.columns or f1 not in self._df.columns or f2 not in self._df.columns:
            self.status_label.setText("Hata: Kolon bulunamadı.")
            return
        self.run_btn.setEnabled(False)
        try:
            result = run_two_way_anova(
                self._df, response, f1, f2,
                interaction=self.cb_interaction.isChecked(),
            )
            self._results = result
            anova_df = result["anova_df"]
            r2 = result.get("r_squared")
            partial_eta = result.get("partial_eta_squared", {})
            summary_lines = []
            if r2 is not None and r2 == r2:
                summary_lines.append(f"R² = {r2:.4f}")
            if partial_eta:
                for k, v in partial_eta.items():
                    if v is not None and v == v:
                        summary_lines.append(f"Partial η² ({k}) = {v:.4f}")
            self.anova_summary_label.setText("  |  ".join(summary_lines) if summary_lines else "")
            aw = anova_df.reset_index()
            self.anova_model.setRowCount(len(aw))
            self.anova_model.setColumnCount(len(aw.columns))
            self.anova_model.setHorizontalHeaderLabels([str(c) for c in aw.columns])
            for i in range(len(aw)):
                for j, c in enumerate(aw.columns):
                    val = aw.iloc[i, j]
                    self.anova_model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))
            if self.cb_levene.isChecked():
                lev_rows = []
                for fac in [f1, f2]:
                    lev = levene_test(self._df, response, fac)
                    if "error" not in lev:
                        lev_rows.append({"Faktor": fac, "İstatistik": lev.get("statistic"), "p-değeri": lev.get("pvalue"), "Varyanslar Homojen": "Evet" if lev.get("equal_var") else "Hayır"})
                if lev_rows:
                    self._fill_table_model(self.levene_model, pd.DataFrame(lev_rows))
                else:
                    self.levene_model.setRowCount(0)
                    self.levene_model.setColumnCount(0)
            else:
                self.levene_model.setRowCount(0)
                self.levene_model.setColumnCount(0)
            if self.cb_tukey.isChecked():
                tukey_dfs = []
                for fac in [f1, f2]:
                    tuk = tukey_hsd(self._df, response, fac)
                    if "error" not in tuk and "result" in tuk and hasattr(tuk["result"], "_results_table") and tuk["result"]._results_table is not None:
                        res = tuk["result"]
                        df = pd.DataFrame(data=res._results_table.data[1:], columns=res._results_table.data[0])
                        df.insert(0, "Faktor", fac)
                        tukey_dfs.append(df)
                if tukey_dfs:
                    tukey_df = pd.concat(tukey_dfs, ignore_index=True)
                    self._fill_table_model(self.tukey_model, tukey_df)
                else:
                    self.tukey_model.setRowCount(0)
                    self.tukey_model.setColumnCount(0)
            else:
                self.tukey_model.setRowCount(0)
                self.tukey_model.setColumnCount(0)
            fig_dist = plot_distribution_panel(self._df[response], f"Dağılım: {response}")
            self._set_canvas(self.dist_layout, fig_dist)
            warnings_list = generate_warnings(model=result.get("model"), anova_df=anova_df, n_obs=len(self._df))
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
            fig_me = plot_main_effects(self._df, [f1, f2], response)
            self._set_canvas(self.main_effects_layout, fig_me)
            self.status_label.setText("Analiz tamamlandı.")
        except Exception as e:
            self.warning_banner.setVisible(False)
            self.status_label.setText(f"Hata: {str(e)}")
        finally:
            self.run_btn.setEnabled(True)
    
    def _fill_table_model(self, model: QStandardItemModel, df: pd.DataFrame) -> None:
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
