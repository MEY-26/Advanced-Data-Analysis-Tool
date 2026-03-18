"""
One-Way ANOVA sekmesi.
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
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont

from gui.widgets import MplCanvas
from utils import format_number
from analysis.one_way_anova import run_one_way_anova
from analysis.posthoc import tukey_hsd, levene_test
from analysis.common import format_significance, generate_warnings, warnings_to_text
from analysis.lack_of_fit import compute_lack_of_fit
from plots import plot_distribution_panel, plot_main_effects
from gui.tabs.base_analysis_tab import BaseAnalysisTab

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class OneWayTab(BaseAnalysisTab):
    """One-Way ANOVA arayüzü."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        self.warning_banner = QLabel("")
        self.warning_banner.setVisible(False)
        self.warning_banner.setWordWrap(True)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        resp_group = QGroupBox("Response")
        resp_layout = QVBoxLayout(resp_group)
        self.response_combo = QComboBox()
        resp_layout.addWidget(self.response_combo)
        left_layout.addWidget(resp_group)
        
        factor_group = QGroupBox("Faktör")
        factor_layout = QVBoxLayout(factor_group)
        self.factor_combo = QComboBox()
        factor_layout.addWidget(self.factor_combo)
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
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        right_container = QWidget()
        right_main_layout = QVBoxLayout(right_container)
        right_main_layout.setContentsMargins(0, 0, 0, 0)
        right_main_layout.addWidget(self.warning_banner)
        right = QTabWidget()
        self.summary_browser = QTextBrowser()
        self.summary_browser.setFont(QFont("Consolas", 9))
        right.addTab(self.summary_browser, "Özet")
        self.anova_table = QTableView()
        self.anova_model = QStandardItemModel()
        self.anova_table.setModel(self.anova_model)
        right.addTab(self.anova_table, "ANOVA")
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
            factor_opts = [c for c in all_cols if c not in all_numeric or df[c].nunique() < 20] or all_cols
            resp_default = (self._column_roles.get("response", []) if self._column_roles else [])[:1]
            factor_default = (
                [c for c in self._column_roles.get("categorical_factors", []) if c in df.columns]
                + [c for c in self._column_roles.get("numeric_factors", []) if c in df.columns]
            ) if self._column_roles else []
            self.response_combo.clear()
            self.response_combo.addItems(resp_opts or ["(yok)"])
            if resp_default and resp_default[0] in resp_opts:
                self.response_combo.setCurrentText(resp_default[0])
            self.factor_combo.clear()
            self.factor_combo.addItems(factor_opts or ["(yok)"])
            if factor_default and factor_default[0] in factor_opts:
                self.factor_combo.setCurrentText(factor_default[0])
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        
        response = self.response_combo.currentText()
        factor = self.factor_combo.currentText()
        if response not in self._df.columns or factor not in self._df.columns:
            self.status_label.setText("Hata: Response veya Faktör kolonu yok.")
            return
        
        self.run_btn.setEnabled(False)
        self.status_label.setText("Analiz çalışıyor...")
        QApplication.processEvents()
        
        try:
            result = run_one_way_anova(self._df, response, factor)
            self._results = result
            
            anova_df = result.get("anova_df")
            model = result.get("model")
            group_means = result.get("group_means")
            
            summary_parts = []
            summary_parts.append(f"One-Way ANOVA: {response} ~ {factor}")
            summary_parts.append(f"F = {result.get('f_stat', 'N/A'):.4f}")
            summary_parts.append(f"p = {result.get('p_value', 'N/A'):.6f}")
            r2 = result.get("r_squared") or result.get("eta_squared")
            if r2 is not None and r2 == r2:
                summary_parts.append(f"R² (eta-squared) = {r2:.4f}")
            summary_parts.append(format_significance(result.get("p_value", 1)))
            if group_means is not None:
                summary_parts.append("\nGrup Ortalamaları:")
                summary_parts.append(group_means.to_string())
            self.summary_browser.setText("\n".join(summary_parts))
            
            if anova_df is not None:
                aw = anova_df.reset_index()
                # LOF ekle (model varsa ve replika varsa)
                if model is not None:
                    lof = compute_lack_of_fit(model, self._df, [factor], response)
                    if lof.get("has_replicates") and lof.get("warning") is None:
                        lof_row = pd.DataFrame([{
                            "sum_sq": lof["ss_lof"], "df": lof["df_lof"],
                            "F": lof["f_lof"], "PR(>F)": lof["p_value"],
                        }], index=["Lack of Fit"])
                        pure_row = pd.DataFrame([{
                            "sum_sq": lof["ss_pure_error"], "df": lof["df_pure_error"],
                        }], index=["Pure Error"])
                        anova_ext = anova_df.copy()
                        if "Residual" in anova_ext.index:
                            anova_ext = anova_ext.drop("Residual")
                        anova_ext = pd.concat([anova_ext, lof_row, pure_row])
                        aw = anova_ext.reset_index()
                    elif lof.get("warning"):
                        summary_parts.append(f"\nLOF: {lof['warning']}")
                        self.summary_browser.setText("\n".join(summary_parts))
                self.anova_model.setRowCount(len(aw))
                self.anova_model.setColumnCount(len(aw.columns))
                self.anova_model.setHorizontalHeaderLabels([str(c) for c in aw.columns])
                for i in range(len(aw)):
                    for j, c in enumerate(aw.columns):
                        val = aw.iloc[i, j]
                        self.anova_model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))
            
            if self.cb_levene.isChecked():
                lev = levene_test(self._df, response, factor)
                if "error" not in lev:
                    levene_df = pd.DataFrame([{
                        "İstatistik": lev.get("statistic"),
                        "p-değeri": lev.get("pvalue"),
                        "BF İstatistik": lev.get("bf_statistic", ""),
                        "BF p-değeri": lev.get("bf_pvalue", ""),
                        "Varyanslar Homojen": "Evet" if lev.get("equal_var") else "Hayır",
                    }])
                    self._fill_table_model(self.levene_model, levene_df)
                else:
                    self.levene_model.setRowCount(0)
                    self.levene_model.setColumnCount(0)
            else:
                self.levene_model.setRowCount(0)
                self.levene_model.setColumnCount(0)
            
            if self.cb_tukey.isChecked():
                tuk = tukey_hsd(self._df, response, factor)
                if "error" not in tuk and "result" in tuk:
                    res = tuk["result"]
                    if hasattr(res, "_results_table") and res._results_table is not None:
                        tukey_df = pd.DataFrame(
                            data=res._results_table.data[1:],
                            columns=res._results_table.data[0]
                        )
                        self._fill_table_model(self.tukey_model, tukey_df)
                    else:
                        self.tukey_model.setRowCount(0)
                        self.tukey_model.setColumnCount(0)
                else:
                    self.tukey_model.setRowCount(0)
                    self.tukey_model.setColumnCount(0)
            else:
                self.tukey_model.setRowCount(0)
                self.tukey_model.setColumnCount(0)
            
            fig_dist = plot_distribution_panel(self._df[response], f"Dağılım: {response}")
            self._set_canvas(self.dist_layout, fig_dist)
            
            warnings_list = generate_warnings(model=model, anova_df=anova_df, n_obs=len(self._df))
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
    
    def _fill_table_model(self, model: QStandardItemModel, df: pd.DataFrame) -> None:
        """DataFrame'i QStandardItemModel'e doldurur."""
        model.setRowCount(len(df))
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels([str(c) for c in df.columns])
        for i in range(len(df)):
            for j, c in enumerate(df.columns):
                val = df.iloc[i, j]
                display = format_number(val) if pd.notna(val) else ""
                model.setItem(i, j, QStandardItem(str(display)))
    
    def _set_canvas(self, layout, fig) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout.addWidget(FigureCanvasQTAgg(fig))
