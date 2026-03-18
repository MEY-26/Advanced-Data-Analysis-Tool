"""
Analiz 2 — Degisim Analizi sekmesi.
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
    QListWidget,
    QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont

from gui.widgets import MplCanvas
from utils import format_number, replace_scientific_notation
from analysis.delta import compute_delta, group_summary, run_delta_rsm
from analysis.rsm import NUMERIC_FACTORS
from plots import (
    plot_delta_distribution,
    plot_delta_boxplot_by_group,
    plot_3d_surface,
    plot_contour,
    plot_main_effects,
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class Analysis2Tab(QWidget):
    """Analiz 2 (Degisim) arayuzu."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._df: pd.DataFrame | None = None
        self._delta_df: pd.DataFrame | None = None
        self._results = {}
        self._column_roles = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        # Oncesi / Sonrasi
        before_after_group = QGroupBox("Öncesi / Sonrasi")
        ba_layout = QVBoxLayout(before_after_group)
        ba_layout.addWidget(QLabel("Öncesi (Before):"))
        self.before_combo = QComboBox()
        self.before_combo.addItems(["oncesi"])
        ba_layout.addWidget(self.before_combo)
        ba_layout.addWidget(QLabel("Sonrasi (After):"))
        self.after_combo = QComboBox()
        self.after_combo.addItems(["sonrasi"])
        ba_layout.addWidget(self.after_combo)
        left_layout.addWidget(before_after_group)
        
        # Degisim metrigi
        metric_group = QGroupBox("Değişim Metriği")
        metric_layout = QVBoxLayout(metric_group)
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["absolute", "percent", "improvement"])
        self.metric_combo.setCurrentText("absolute")
        metric_layout.addWidget(QLabel("Metrik:"))
        metric_layout.addWidget(self.metric_combo)
        left_layout.addWidget(metric_group)
        
        # Iyilesme yonu
        dir_group = QGroupBox("Iyilesme Yonu")
        dir_layout = QVBoxLayout(dir_group)
        self.rb_smaller = QRadioButton("Kucuk daha iyi")
        self.rb_larger = QRadioButton("Buyuk daha iyi")
        self.rb_smaller.setChecked(True)
        dir_layout.addWidget(self.rb_smaller)
        dir_layout.addWidget(self.rb_larger)
        left_layout.addWidget(dir_group)
        
        # Oncesi=0
        zero_group = QGroupBox("Öncesi=0 İşlemi")
        zero_layout = QVBoxLayout(zero_group)
        self.zero_combo = QComboBox()
        self.zero_combo.addItems(["nan", "0"])
        zero_layout.addWidget(self.zero_combo)
        left_layout.addWidget(zero_group)
        
        # Duplikat
        dup_group = QGroupBox("Duplikat İşleme")
        dup_layout = QVBoxLayout(dup_group)
        self.rb_keep_all = QRadioButton("Hepsini tut")
        self.rb_avg = QRadioButton("Ortalama ile birleştir")
        self.rb_keep_all.setChecked(True)
        dup_layout.addWidget(self.rb_keep_all)
        dup_layout.addWidget(self.rb_avg)
        left_layout.addWidget(dup_group)
        
        # Faktorler (numerik) - ayri ayri secim
        factor_group = QGroupBox("Faktörler (numerik)")
        factor_layout = QVBoxLayout(factor_group)
        factor_layout.addWidget(QLabel("Çoklu seçim:"))
        self.factor_list = QListWidget()
        self.factor_list.setSelectionMode(self.factor_list.SelectionMode.MultiSelection)
        self.factor_list.setMinimumHeight(140)
        factor_layout.addWidget(self.factor_list)
        left_layout.addWidget(factor_group)
        
        # RSM ayarlari (Analiz 1 ile ayni)
        rsm_group = QGroupBox("RSM Terimleri")
        rsm_layout = QVBoxLayout(rsm_group)
        self.cb_interactions = QCheckBox("Etkileşimler")
        self.cb_interactions.setChecked(True)
        self.cb_quadratic = QCheckBox("Karesel")
        self.cb_quadratic.setChecked(True)
        self.cb_delik = QCheckBox("Delik")
        self.cb_olcum = QCheckBox("Ölçüm")
        rsm_layout.addWidget(self.cb_interactions)
        rsm_layout.addWidget(self.cb_quadratic)
        rsm_layout.addWidget(self.cb_delik)
        rsm_layout.addWidget(self.cb_olcum)
        left_layout.addWidget(rsm_group)
        
        # Surface
        surf_group = QGroupBox("Surface")
        surf_layout = QVBoxLayout(surf_group)
        surf_layout.addWidget(QLabel("Faktör 1:"))
        self.factor1_combo = QComboBox()
        self.factor1_combo.addItems(["devir", "feed", "paso"])
        surf_layout.addWidget(self.factor1_combo)
        surf_layout.addWidget(QLabel("Faktor 2:"))
        self.factor2_combo = QComboBox()
        self.factor2_combo.addItems(["devir", "feed", "paso"])
        surf_layout.addWidget(self.factor2_combo)
        left_layout.addWidget(surf_group)
        
        self.run_btn = QPushButton("Analizi Calistir")
        self.run_btn.clicked.connect(self._run_analysis)
        left_layout.addWidget(self.run_btn)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        right = QTabWidget()
        self.summary_browser = QTextBrowser()
        self.summary_browser.setFont(QFont("Consolas", 9))
        self.summary_browser.setStyleSheet("font-family: Consolas, 'Courier New', monospace;")
        right.addTab(self.summary_browser, "Model Özeti")
        self.anova_table = QTableView()
        self.anova_model = QStandardItemModel()
        self.anova_table.setModel(self.anova_model)
        right.addTab(self.anova_table, "ANOVA")
        self.group_table = QTableView()
        self.group_model = QStandardItemModel()
        self.group_table.setModel(self.group_model)
        right.addTab(self.group_table, "Grup Özeti")
        self.delta_container = QWidget()
        self.delta_layout = QVBoxLayout(self.delta_container)
        self.delta_layout.addWidget(MplCanvas())
        right.addTab(self.delta_container, "Delta Dağılımı")
        self.surface_container = QWidget()
        self.surface_layout = QVBoxLayout(self.surface_container)
        self.surface_layout.addWidget(MplCanvas())
        right.addTab(self.surface_container, "Surface")
        main_effects_widget = QWidget()
        self.main_effects_layout = QVBoxLayout(main_effects_widget)
        right.addTab(main_effects_widget, "Main Effects")
        
        left.setMinimumWidth(240)
        scroll = QScrollArea()
        scroll.setWidget(left)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(scroll, 1)
        layout.addWidget(right, 3)
    
    def set_data(self, df: pd.DataFrame | None) -> None:
        self._df = df
        self._update_combos()
    
    def set_column_roles(self, roles: dict | None) -> None:
        self._column_roles = roles
        self._update_combos()
    
    def _update_combos(self) -> None:
        """Before/After combo'larını günceller. Tüm numerik kolonlar, roller varsayılan seçili."""
        if self._df is None or self._df.empty:
            return
        df = self._df
        all_numeric = df.select_dtypes(include=["number"]).columns.tolist()
        opts = all_numeric or list(df.columns)
        resp_default = (self._column_roles.get("response", []) if self._column_roles else [])[:2]
        self.before_combo.clear()
        self.after_combo.clear()
        self.before_combo.addItems(opts)
        self.after_combo.addItems(opts)
        factor_default = [c for c in (self._column_roles.get("numeric_factors", []) if self._column_roles else NUMERIC_FACTORS) if c in df.columns]
        self.factor_list.clear()
        self.factor_list.addItems(opts or ["(yok)"])
        for c in factor_default:
            for i in range(self.factor_list.count()):
                if self.factor_list.item(i).text() == c:
                    self.factor_list.item(i).setSelected(True)
                    break
        self.factor1_combo.clear()
        self.factor2_combo.clear()
        self.factor1_combo.addItems(opts)
        self.factor2_combo.addItems(opts)
        if factor_default:
            if factor_default[0] in opts:
                self.factor1_combo.setCurrentText(factor_default[0])
            if len(factor_default) > 1 and factor_default[1] in opts:
                self.factor2_combo.setCurrentText(factor_default[1])
        if resp_default:
            if len(resp_default) >= 1 and resp_default[0] in opts:
                self.before_combo.setCurrentText(resp_default[0])
            if len(resp_default) >= 2 and resp_default[1] in opts:
                self.after_combo.setCurrentText(resp_default[1])
            elif "sonrasi" in opts:
                self.after_combo.setCurrentText("sonrasi")
        else:
            if "oncesi" in opts:
                self.before_combo.setCurrentText("oncesi")
            if "sonrasi" in opts:
                self.after_combo.setCurrentText("sonrasi")
    
    def _run_analysis(self) -> None:
        if self._df is None or self._df.empty:
            self.status_label.setText("Hata: Veri yüklenmedi.")
            return
        df = self._df.copy()
        before_col = self.before_combo.currentText()
        after_col = self.after_combo.currentText()
        if before_col not in df.columns or after_col not in df.columns:
            self.status_label.setText("Hata: Öncesi/Sonrasi (veya Response) kolonları gerekli.")
            self.summary_browser.setText("Öncesi ve Sonrasi kolonları gerekli.")
            return
        
        self.run_btn.setEnabled(False)
        self.status_label.setText("Analiz calisiyor...")
        self.status_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        QApplication.processEvents()
        
        try:
            if self.rb_avg.isChecked():
                key_cols = [i.text() for i in self.factor_list.selectedItems() if i.text() in df.columns]
                if not key_cols:
                    key_cols = (self._column_roles.get("numeric_factors", []) + self._column_roles.get("categorical_factors", []) + (self._column_roles.get("block", []) or [])) if self._column_roles else ["numune", "delik", "devir", "feed", "paso", "olcum"]
                key_cols = [c for c in key_cols if c in df.columns]
                if key_cols:
                    agg_dict = {before_col: "mean", after_col: "mean"}
                    df = df.groupby(key_cols, dropna=False).agg(agg_dict).reset_index()
            
            direction = "smaller_better" if self.rb_smaller.isChecked() else "larger_better"
            metric = self.metric_combo.currentText()
            zero_handling = self.zero_combo.currentText()
            
            df = compute_delta(df, before_col=before_col, after_col=after_col, metric=metric, direction=direction, zero_handling=zero_handling)
            self._delta_df = df.dropna(subset=["Delta"])
            
            if self._delta_df.empty:
                self.status_label.setText("Hata: Geçerli veri kalmadı.")
                self.summary_browser.setText("Delta hesaplandıktan sonra geçerli veri kalmadı.")
                return
            
            categoricals = []
            if self.cb_delik.isChecked() and "delik" in df.columns:
                categoricals.append("delik")
            if self.cb_olcum.isChecked() and "olcum" in df.columns:
                categoricals.append("olcum")
            
            factors = [i.text() for i in self.factor_list.selectedItems() if i.text() in df.columns]
            if not factors:
                factors = (self._column_roles.get("numeric_factors", []) if self._column_roles else None) or [f for f in NUMERIC_FACTORS if f in df.columns]
            results = run_delta_rsm(
                df,
                factors=factors,
                include_interactions=self.cb_interactions.isChecked(),
                include_quadratic=self.cb_quadratic.isChecked(),
                categoricals=categoricals if categoricals else None,
                anova_type="3",
            )
            
            grp_cols = (factors + categoricals) if factors or categoricals else None
            self._results = {
                "delta_df": df,
                "group_summary": group_summary(df, groupby_cols=grp_cols),
                **results,
            }
            
            summary_text = results["summary"].get("summary_text", "")
            summary_text = replace_scientific_notation(summary_text)
            html_content = f'<pre style="font-family: Consolas, \'Courier New\', monospace; font-size: 10pt; margin: 0;">{html.escape(summary_text)}</pre>'
            self.summary_browser.setHtml(html_content)
            
            # ANOVA (kaynak + sutunlar)
            anova_df = results["anova"]
            anova_with_index = anova_df.reset_index()
            if anova_with_index.columns[0] == "index":
                anova_with_index = anova_with_index.rename(columns={"index": "Kaynak"})
            self.anova_model.setRowCount(len(anova_with_index))
            self.anova_model.setColumnCount(len(anova_with_index.columns))
            self.anova_model.setHorizontalHeaderLabels([str(c) for c in anova_with_index.columns])
            for i in range(len(anova_with_index)):
                for j, c in enumerate(anova_with_index.columns):
                    val = anova_with_index.iloc[i, j]
                    self.anova_model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))
            
            # Grup ozeti
            grp_cols = (factors + categoricals) if factors or categoricals else None
            grp = results.get("group_summary", group_summary(df, groupby_cols=grp_cols))
            if not grp.empty:
                self.group_model.setRowCount(len(grp))
                self.group_model.setColumnCount(len(grp.columns))
                self.group_model.setHorizontalHeaderLabels([str(c) for c in grp.columns])
                for i in range(len(grp)):
                    for j, c in enumerate(grp.columns):
                        val = grp.iloc[i, j]
                        self.group_model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))
            
            # Delta dagilimi
            if "delik" in df.columns:
                fig_delta = plot_delta_boxplot_by_group(df, "delik")
            else:
                fig_delta = plot_delta_distribution(df, kind="hist")
            self._set_container_canvas(self.delta_layout, fig_delta)
            
            # Surface
            model = results["model"]
            f1 = self.factor1_combo.currentText()
            f2 = self.factor2_combo.currentText()
            factors = [f for f in NUMERIC_FACTORS if f in df.columns]
            fixed = {}
            for f in factors:
                if f != f1 and f != f2:
                    fixed[f] = float(df[f].median())
            try:
                fig_surf = plot_3d_surface(model, df, f1, f2, fixed)
                self._set_container_canvas(self.surface_layout, fig_surf)
            except Exception:
                try:
                    fig_cont = plot_contour(model, df, f1, f2, fixed)
                    self._set_container_canvas(self.surface_layout, fig_cont)
                except Exception:
                    pass
            
            fig_me = plot_main_effects(df, factors, "Delta")
            self._set_container_canvas(self.main_effects_layout, fig_me)
            
            self.status_label.setText("Analiz tamamlandı.")
            self.status_label.setStyleSheet("color: #008800; font-weight: bold;")
        except Exception as e:
            err_msg = str(e)
            if "constraint matrix" in err_msg.lower() or "singular" in err_msg.lower():
                err_msg = "Filtrelenmiş veri bu model için yetersiz. Daha fazla veri kullanın veya kategorik blokları azaltın."
            self.status_label.setText(f"Hata: {err_msg[:80]}")
            self.status_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            self.summary_browser.setText(f"Model hatası:\n\n{err_msg}")
        finally:
            self.run_btn.setEnabled(True)
    
    def _set_container_canvas(self, layout: QVBoxLayout, fig) -> None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        layout.addWidget(FigureCanvasQTAgg(fig))
    
    def get_results(self) -> dict:
        return self._results
