"""
Analiz 1 — RSM/ANOVA sekmesi.
"""

import html
import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QCheckBox,
    QComboBox,
    QRadioButton,
    QPushButton,
    QTextBrowser,
    QTableView,
    QTabWidget,
    QLabel,
    QDoubleSpinBox,
    QApplication,
    QStackedWidget,
    QListWidget,
    QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont

from gui.widgets import MplCanvas
from utils import format_number, replace_scientific_notation
from analysis.rsm import (
    build_formula,
    fit_rsm_model,
    run_anova,
    compute_vif_from_model,
    correlation_matrix,
    get_model_summary,
    NUMERIC_FACTORS,
)
from analysis.outliers import detect_outliers_iqr, detect_outliers_zscore, get_outlier_summary
from analysis.lack_of_fit import compute_lack_of_fit
from analysis.common import generate_warnings
from analysis.coding import code_dataframe, get_factor_ranges_from_df
from plots import (
    plot_residuals_vs_fitted,
    plot_qq,
    plot_3d_surface,
    plot_contour,
    plot_main_effects,
    plot_correlation_heatmap,
    plot_histogram_with_distribution,
    plot_distribution_panel,
    plot_boxplot_outliers,
)
import matplotlib.pyplot as plt


class Analysis1Tab(QWidget):
    """Analiz 1 (RSM) arayuzu."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._df: pd.DataFrame | None = None
        self._model = None
        self._results = {}
        self._column_roles = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        
        # Sol panel: Ayarlar
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        # Response
        resp_group = QGroupBox("Response")
        resp_layout = QVBoxLayout(resp_group)
        self.response_combo = QComboBox()
        self.response_combo.addItems(["oncesi"])
        resp_layout.addWidget(self.response_combo)
        left_layout.addWidget(resp_group)
        
        # Faktorler (numerik) - ayri ayri secim
        factor_group = QGroupBox("Faktörler (numerik)")
        factor_layout = QVBoxLayout(factor_group)
        factor_layout.addWidget(QLabel("Çoklu seçim:"))
        self.factor_list = QListWidget()
        self.factor_list.setSelectionMode(self.factor_list.SelectionMode.MultiSelection)
        self.factor_list.setMinimumHeight(140)
        factor_layout.addWidget(self.factor_list)
        left_layout.addWidget(factor_group)
        
        # Model terimleri
        terms_group = QGroupBox("Model Terimleri")
        terms_layout = QVBoxLayout(terms_group)
        self.cb_main = QCheckBox("Ana etkiler")
        self.cb_main.setChecked(True)
        self.cb_interactions = QCheckBox("İkili etkileşimler")
        self.cb_interactions.setChecked(True)
        self.cb_quadratic = QCheckBox("Karesel terimler")
        self.cb_quadratic.setChecked(True)
        terms_layout.addWidget(self.cb_main)
        terms_layout.addWidget(self.cb_interactions)
        terms_layout.addWidget(self.cb_quadratic)
        left_layout.addWidget(terms_group)
        
        self.cb_coded_values = QCheckBox("Coded Values Kullan")
        self.cb_coded_values.setToolTip("Evrensel kodlama: X_kodlu = (X_gercek - X_orta) / ((X_max - X_min)/2)")
        left_layout.addWidget(self.cb_coded_values)
        
        # Kategorikler
        cat_group = QGroupBox("Kategorik Bloklar")
        cat_layout = QVBoxLayout(cat_group)
        self.cb_delik = QCheckBox("Delik")
        self.cb_olcum = QCheckBox("Ölçüm")
        self.cb_numune = QCheckBox("Numune (block)")
        cat_layout.addWidget(self.cb_delik)
        cat_layout.addWidget(self.cb_olcum)
        cat_layout.addWidget(self.cb_numune)
        left_layout.addWidget(cat_group)
        
        # Outlier
        outlier_group = QGroupBox("Aykırı Değerler")
        outlier_layout = QVBoxLayout(outlier_group)
        self.cb_exclude_outliers = QCheckBox("Analiz dışında bırak")
        self.outlier_method_combo = QComboBox()
        self.outlier_method_combo.addItems(["IQR", "Z-score"])
        outlier_layout.addWidget(self.cb_exclude_outliers)
        outlier_layout.addWidget(QLabel("Yöntem:"))
        outlier_layout.addWidget(self.outlier_method_combo)
        left_layout.addWidget(outlier_group)
        
        # ANOVA tipi
        anova_group = QGroupBox("ANOVA Tipi")
        anova_layout = QVBoxLayout(anova_group)
        self.rb_type2 = QRadioButton("Type II")
        self.rb_type3 = QRadioButton("Type III")
        self.rb_type2.setChecked(True)
        anova_layout.addWidget(self.rb_type2)
        anova_layout.addWidget(self.rb_type3)
        left_layout.addWidget(anova_group)
        
        # Surface grafik
        surf_group = QGroupBox("Surface/Contour")
        surf_layout = QVBoxLayout(surf_group)
        surf_layout.addWidget(QLabel("Faktör 1:"))
        self.factor1_combo = QComboBox()
        self.factor1_combo.addItems(["devir", "feed", "paso"])
        self.factor1_combo.setMinimumWidth(120)
        surf_layout.addWidget(self.factor1_combo)
        surf_layout.addWidget(QLabel("Faktör 2:"))
        self.factor2_combo = QComboBox()
        self.factor2_combo.addItems(["devir", "feed", "paso"])
        self.factor2_combo.setMinimumWidth(120)
        surf_layout.addWidget(self.factor2_combo)
        surf_layout.addWidget(QLabel("Sabit faktör (3.):"))
        self.fixed_spin = QDoubleSpinBox()
        self.fixed_spin.setRange(-1e9, 1e9)
        self.fixed_spin.setValue(0)
        self.fixed_spin.setMinimumWidth(120)
        surf_layout.addWidget(self.fixed_spin)
        left_layout.addWidget(surf_group)
        
        self.run_btn = QPushButton("Analizi Çalıştır")
        self.run_btn.clicked.connect(self._run_analysis)
        left_layout.addWidget(self.run_btn)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        left.setMinimumWidth(240)
        scroll = QScrollArea()
        scroll.setWidget(left)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Sag panel: Sonuclar
        self.warning_banner = QLabel("")
        self.warning_banner.setVisible(False)
        self.warning_banner.setWordWrap(True)
        right_container = QWidget()
        right_main_layout = QVBoxLayout(right_container)
        right_main_layout.setContentsMargins(0, 0, 0, 0)
        right_main_layout.addWidget(self.warning_banner)
        right = QTabWidget()
        self.summary_browser = QTextBrowser()
        self.summary_browser.setFont(QFont("Consolas", 9))
        self.summary_browser.setStyleSheet("font-family: Consolas, 'Courier New', monospace;")
        right.addTab(self.summary_browser, "Model Özeti")
        self.anova_table = QTableView()
        self.anova_model = QStandardItemModel()
        self.anova_table.setModel(self.anova_model)
        right.addTab(self.anova_table, "ANOVA")
        self.vif_table = QTableView()
        self.vif_model = QStandardItemModel()
        self.vif_table.setModel(self.vif_model)
        right.addTab(self.vif_table, "VIF")
        self.residual_container = QWidget()
        self.residual_layout = QVBoxLayout(self.residual_container)
        self.residual_layout.addWidget(MplCanvas())
        right.addTab(self.residual_container, "Residual Plots")
        self.surface_container = QWidget()
        self.surface_layout = QVBoxLayout(self.surface_container)
        self.surface_layout.addWidget(MplCanvas())
        right.addTab(self.surface_container, "Surface/Contour")
        self.corr_container = QWidget()
        self.corr_layout = QVBoxLayout(self.corr_container)
        self.corr_layout.addWidget(MplCanvas())
        right.addTab(self.corr_container, "Korelasyon")
        self.main_effects_container = QWidget()
        self.main_effects_layout = QVBoxLayout(self.main_effects_container)
        self.main_effects_layout.addWidget(MplCanvas())
        right.addTab(self.main_effects_container, "Main Effects")
        self.distribution_container = QWidget()
        self.distribution_layout = QVBoxLayout(self.distribution_container)
        self.distribution_layout.addWidget(MplCanvas())
        right.addTab(self.distribution_container, "Dağılım")
        self.coded_data_container = QWidget()
        coded_data_layout = QVBoxLayout(self.coded_data_container)
        self.coded_data_stacked = QStackedWidget()
        self.coded_data_placeholder = QLabel("Coded Values kullanıldığında bu tablolar görünür.")
        self.coded_data_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coded_data_stacked.addWidget(self.coded_data_placeholder)
        self.coded_data_tabs = QTabWidget()
        self.coded_table = QTableView()
        self.coded_table.setModel(QStandardItemModel())
        self.coded_data_tabs.addTab(self.coded_table, "Kodlanmış")
        self.real_table = QTableView()
        self.real_table.setModel(QStandardItemModel())
        self.coded_data_tabs.addTab(self.real_table, "Gerçek")
        self.coded_data_stacked.addWidget(self.coded_data_tabs)
        coded_data_layout.addWidget(self.coded_data_stacked)
        right.addTab(self.coded_data_container, "Coded/Real")
        right_main_layout.addWidget(right)
        layout.addWidget(scroll, 1)
        layout.addWidget(right_container, 3)
    
    def set_data(self, df: pd.DataFrame | None) -> None:
        """Veriyi gunceller."""
        self._df = df
        self._update_combos()
    
    def set_column_roles(self, roles: dict | None) -> None:
        """Sütun rollerini günceller."""
        self._column_roles = roles
        self._update_combos()
    
    def _update_combos(self) -> None:
        """Response ve faktör combo'larını günceller. Tüm kolonlar gösterilir, roller varsayılan seçili."""
        if self._df is None or self._df.empty:
            return
        df = self._df
        all_numeric = df.select_dtypes(include=["number"]).columns.tolist()
        num_opts = all_numeric or list(df.columns)
        resp_default = (self._column_roles.get("response", []) if self._column_roles else [])[:1]
        num_default = [c for c in (self._column_roles.get("numeric_factors", []) if self._column_roles else NUMERIC_FACTORS) if c in df.columns]
        self.response_combo.clear()
        self.response_combo.addItems(num_opts)
        if resp_default and resp_default[0] in num_opts:
            self.response_combo.setCurrentText(resp_default[0])
        elif num_opts and "oncesi" in num_opts:
            self.response_combo.setCurrentText("oncesi")
        self.factor_list.clear()
        self.factor_list.addItems(num_opts or ["(yok)"])
        for c in num_default:
            for i in range(self.factor_list.count()):
                if self.factor_list.item(i).text() == c:
                    self.factor_list.item(i).setSelected(True)
                    break
        for c in [self.factor1_combo, self.factor2_combo]:
            cur = c.currentText()
            c.clear()
            c.addItems(num_opts)
            if num_default and num_default[0] in num_opts:
                c.setCurrentText(num_default[0])
            elif cur in num_opts:
                c.setCurrentText(cur)
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        df = self._df.dropna()
        
        # Outlier tespiti ve opsiyonel filtreleme
        response = self.response_combo.currentText()
        if response in df.columns:
            series = pd.to_numeric(df[response], errors="coerce").dropna()
            if len(series) >= 3:
                method = self.outlier_method_combo.currentText().lower()
                if "z" in method:
                    outlier_mask, _, _ = detect_outliers_zscore(series, threshold=3.0)
                else:
                    outlier_mask, _, _ = detect_outliers_iqr(series, factor=1.5)
                n_outliers = int(outlier_mask.sum())
                if self.cb_exclude_outliers.isChecked() and n_outliers > 0:
                    keep_idx = ~outlier_mask.reindex(df.index).fillna(False)
                    df = df.loc[keep_idx]
                    self._outlier_info = f"{n_outliers} aykırı değer analiz dışında bırakıldı."
                else:
                    self._outlier_info = f"{n_outliers} aykırı değer tespit edildi." if n_outliers > 0 else "Aykırı değer yok."
                    self._outlier_mask = outlier_mask
            else:
                self._outlier_info = ""
                self._outlier_mask = None
        else:
            self._outlier_info = ""
            self._outlier_mask = None
        
        if len(df) < 3:
            self.status_label.setText("Hata: Yeterli veri yok.")
            self.summary_browser.setText("Yeterli veri yok (en az 3 satir gerekli).")
            return
        
        response = self.response_combo.currentText()
        if response not in df.columns:
            self.status_label.setText(f"Hata: {response} kolonu yok.")
            self.summary_browser.setText(f"Response kolonu yok: {response}")
            return
        
        self.run_btn.setEnabled(False)
        self.status_label.setText("Analiz çalışıyor...")
        self.status_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        QApplication.processEvents()
        
        try:
            factors = [i.text() for i in self.factor_list.selectedItems() if i.text() in df.columns]
            if not factors:
                factors = [f for f in (self._column_roles.get("numeric_factors", []) if self._column_roles else NUMERIC_FACTORS) if f in df.columns]
            categoricals = []
            if self.cb_delik.isChecked() and "delik" in df.columns:
                categoricals.append("delik")
            if self.cb_olcum.isChecked() and "olcum" in df.columns:
                categoricals.append("olcum")
            if self.cb_numune.isChecked() and "numune" in df.columns:
                categoricals.append("numune")
            
            formula = build_formula(
                response=response,
                factors=factors,
                include_interactions=self.cb_interactions.isChecked(),
                include_quadratic=self.cb_quadratic.isChecked(),
                categoricals=categoricals if categoricals else None,
            )
            
            df_work = df.copy()
            factor_ranges = {}
            if self.cb_coded_values.isChecked() and factors:
                factor_ranges = get_factor_ranges_from_df(df, factors)
                if factor_ranges:
                    df_work = code_dataframe(df, factor_ranges)
                else:
                    factor_ranges = {}
            
            self._model = fit_rsm_model(df_work, formula)
            anova_type = "3" if self.rb_type3.isChecked() else "2"
            anova_df = run_anova(self._model, anova_type)
            lof_result = compute_lack_of_fit(self._model, df_work, factors, response)
            vif_df = compute_vif_from_model(self._model)
            corr_df = correlation_matrix(df_work, factors, response)
            summary_dict = get_model_summary(self._model)
            
            self._results = {
                "model": self._model,
                "formula": formula,
                "summary": summary_dict,
                "anova": anova_df,
                "lof": lof_result,
                "vif": vif_df,
                "correlation": corr_df,
                "coded_used": bool(factor_ranges),
                "factor_ranges": factor_ranges,
                "df_coded": df_work[factors + [response]].copy() if factor_ranges and factors else None,
                "df_real": df[factors + [response]].copy() if factor_ranges and factors else None,
            }
            
            # ANOVA tablosuna LOF satiri ekle (replika varsa)
            if lof_result.get("has_replicates") and lof_result.get("warning") is None:
                lof_row = pd.DataFrame([{
                    "sum_sq": lof_result["ss_lof"],
                    "df": lof_result["df_lof"],
                    "F": lof_result["f_lof"],
                    "PR(>F)": lof_result["p_value"],
                }], index=["Lack of Fit"])
                pure_row = pd.DataFrame([{
                    "sum_sq": lof_result["ss_pure_error"],
                    "df": lof_result["df_pure_error"],
                }], index=["Pure Error"])
                # Residual satirini cikar, LOF + Pure Error ekle
                anova_display = anova_df.copy()
                if "Residual" in anova_display.index:
                    anova_display = anova_display.drop("Residual")
                anova_display = pd.concat([anova_display, lof_row, pure_row])
            else:
                anova_display = anova_df
                if lof_result.get("warning"):
                    summary_dict["lof_warning"] = lof_result["warning"]
            
            summary_text = summary_dict.get("summary_text", str(self._model.summary()))
            summary_text = replace_scientific_notation(summary_text)
            if factor_ranges:
                range_str = "; ".join(f"{k}: [{v[0]:.4g}, {v[1]:.4g}]" for k, v in factor_ranges.items())
                summary_text = f"Coded Values kullanildi. Faktor araliklari: {range_str}\n\n{summary_text}"
            if summary_dict.get("lof_warning"):
                summary_text = f"Lack of Fit: {summary_dict['lof_warning']}\n\n{summary_text}"
            html_content = f'<pre style="font-family: Consolas, \'Courier New\', monospace; font-size: 10pt; margin: 0;">{html.escape(summary_text)}</pre>'
            self.summary_browser.setHtml(html_content)
            
            # ANOVA tablo (kaynak + sutunlar)
            anova_with_index = anova_display.reset_index()
            if anova_with_index.columns[0] == "index":
                anova_with_index = anova_with_index.rename(columns={"index": "Kaynak"})
            self.anova_model.setRowCount(len(anova_with_index))
            self.anova_model.setColumnCount(len(anova_with_index.columns))
            self.anova_model.setHorizontalHeaderLabels([str(c) for c in anova_with_index.columns])
            for i in range(len(anova_with_index)):
                for j, c in enumerate(anova_with_index.columns):
                    val = anova_with_index.iloc[i, j]
                    self.anova_model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))
            
            # VIF tablosu
            self.vif_model.setRowCount(len(vif_df))
            self.vif_model.setColumnCount(len(vif_df.columns))
            self.vif_model.setHorizontalHeaderLabels([str(c) for c in vif_df.columns])
            for i in range(len(vif_df)):
                for j, c in enumerate(vif_df.columns):
                    val = vif_df.iloc[i, j]
                    self.vif_model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))
            
            # Coded/Real tablolari (coded kullanildiysa)
            if factor_ranges and self._results.get("df_coded") is not None and self._results.get("df_real") is not None:
                self.coded_data_stacked.setCurrentWidget(self.coded_data_tabs)
                for tbl, d in [(self.coded_table, self._results["df_coded"]), (self.real_table, self._results["df_real"])]:
                    m = tbl.model()
                    m.setRowCount(len(d))
                    m.setColumnCount(len(d.columns))
                    m.setHorizontalHeaderLabels([str(c) for c in d.columns])
                    for i in range(len(d)):
                        for j, c in enumerate(d.columns):
                            val = d.iloc[i, j]
                            m.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))
            else:
                self.coded_data_stacked.setCurrentWidget(self.coded_data_placeholder)
            
            # Grafikler
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            
            fig_res = plt.figure(figsize=(10, 4))
            ax1 = fig_res.add_subplot(121)
            ax1.scatter(self._model.fittedvalues, self._model.resid, alpha=0.6)
            ax1.axhline(0, color="red", linestyle="--")
            ax1.set_xlabel("Fitted")
            ax1.set_ylabel("Residuals")
            ax1.set_title("Residual vs Fitted")
            ax2 = fig_res.add_subplot(122)
            from scipy import stats as scipy_stats
            scipy_stats.probplot(self._model.resid, dist="norm", plot=ax2)
            ax2.set_title("Q-Q Plot")
            fig_res.tight_layout()
            self._set_container_canvas(self.residual_layout, fig_res)
            
            f1 = self.factor1_combo.currentText()
            f2 = self.factor2_combo.currentText()
            fixed = {}
            for f in factors:
                if f != f1 and f != f2:
                    fixed[f] = self.fixed_spin.value() if self.fixed_spin.value() != 0 else float(df[f].median())
            plot_df = df_work if factor_ranges else df
            plot_fixed = fixed.copy() if fixed else {}
            if factor_ranges and fixed:
                for k, v in fixed.items():
                    if k in factor_ranges:
                        from analysis.coding import code_value
                        plot_fixed[k] = code_value(v, factor_ranges[k][0], factor_ranges[k][1])
            try:
                fig_surf = plot_3d_surface(self._model, plot_df, f1, f2, plot_fixed)
                self._set_container_canvas(self.surface_layout, fig_surf)
            except Exception:
                try:
                    fig_cont = plot_contour(self._model, plot_df, f1, f2, plot_fixed)
                    self._set_container_canvas(self.surface_layout, fig_cont)
                except Exception:
                    pass
            
            if not corr_df.empty:
                fig_corr = plot_correlation_heatmap(corr_df)
                self._set_container_canvas(self.corr_layout, fig_corr)
            
            fig_me = plot_main_effects(plot_df, factors, response)
            self._set_container_canvas(self.main_effects_layout, fig_me)
            
            # Dağılım grafiği
            fig_dist = plot_distribution_panel(
                self._df[response] if response in self._df.columns else pd.Series(),
                title=f"Dağılım: {response}",
            )
            self._set_container_canvas(self.distribution_layout, fig_dist)
            
            warnings_list = generate_warnings(
                model=self._model, anova_df=anova_df, vif_df=vif_df, n_obs=len(df)
            )
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
            status_text = "Analiz tamamlandı."
            if hasattr(self, "_outlier_info") and self._outlier_info:
                status_text += f" ({self._outlier_info})"
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet("color: #008800; font-weight: bold;")
        except Exception as e:
            self.warning_banner.setVisible(False)
            err_msg = str(e)
            if "constraint matrix" in err_msg.lower() or "singular" in err_msg.lower():
                err_msg = "Filtrelenmiş veri bu model için yetersiz. Daha fazla veri kullanın veya kategorik blokları (Delik, Ölçüm, Numune) azaltın."
            self.status_label.setText(f"Hata: {err_msg[:80]}")
            self.status_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            self.summary_browser.setText(f"Model hatası:\n\n{err_msg}")
        finally:
            self.run_btn.setEnabled(True)
    
    def _set_container_canvas(self, layout: QVBoxLayout, fig) -> None:
        """Layout'taki canvas'i yeni figure ile degistirir."""
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout.addWidget(FigureCanvasQTAgg(fig))
    
    def get_results(self) -> dict:
        """Analiz sonuclarini dondurur (export icin)."""
        return self._results
