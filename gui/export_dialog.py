"""
Disa aktarma diyalogu.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QFileDialog,
    QLabel,
    QMessageBox,
)
from utils import replace_scientific_notation
from exporter import export_to_excel, export_to_csv


class ExportDialog(QDialog):
    """Disa aktarma secenekleri ve kaydetme."""
    
    def __init__(
        self,
        parent=None,
        filtered_df=None,
        analysis1_results=None,
        analysis2_results=None,
        extra_results=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Dışa Aktar")
        self._filtered_df = filtered_df
        self._analysis1 = analysis1_results or {}
        self._analysis2 = analysis2_results or {}
        self._extra = extra_results or {}
        self._saved_path = None
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Neleri aktaracaksınız?"))
        self.cb_data = QCheckBox("Filtrelenmiş veri")
        self.cb_data.setChecked(True)
        self.cb_data.setEnabled(self._filtered_df is not None and not self._filtered_df.empty)
        layout.addWidget(self.cb_data)
        
        self.cb_analysis1 = QCheckBox("RSM Sonuçları (Model Özet, ANOVA, VIF, Korelasyon)")
        self.cb_analysis1.setChecked(bool(self._analysis1))
        self.cb_analysis1.setEnabled(bool(self._analysis1))
        layout.addWidget(self.cb_analysis1)
        
        self.cb_analysis2 = QCheckBox("Analiz 2 sonuçları (Delta, Grup özeti)")
        self.cb_analysis2.setChecked(bool(self._analysis2))
        self.cb_analysis2.setEnabled(bool(self._analysis2))
        layout.addWidget(self.cb_analysis2)
        
        self._extra_checkboxes = {}
        for name, res in self._extra.items():
            if res:
                cb = QCheckBox(f"{name} sonuçları")
                cb.setChecked(True)
                layout.addWidget(cb)
                self._extra_checkboxes[name] = cb
        
        layout.addWidget(QLabel("Format:"))
        self.rb_excel = QRadioButton("Excel (.xlsx)")
        self.rb_csv = QRadioButton("CSV")
        self.rb_excel.setChecked(True)
        layout.addWidget(self.rb_excel)
        layout.addWidget(self.rb_csv)
        
        self.path_label = QLabel("Hedef seçilmedi")
        layout.addWidget(self.path_label)
        
        btn_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Konum Seç...")
        self.browse_btn.clicked.connect(self._browse)
        self.save_btn = QPushButton("Kaydet")
        self.save_btn.clicked.connect(self._save)
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.browse_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self._export_path = None
    
    def _browse(self) -> None:
        if self.rb_excel.isChecked():
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Kaydet",
                "",
                "Excel (*.xlsx);;Tum Dosyalar (*)",
            )
        else:
            path = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if path:
            self._export_path = path
            self.path_label.setText(path)
    
    def _save(self) -> None:
        if not self._export_path:
            QMessageBox.warning(self, "Uyarı", "Önce konum seçin.")
            return
        
        data_dict = {}
        
        if self.cb_data.isChecked() and self._filtered_df is not None:
            data_dict["Filtered_Data"] = self._filtered_df
        
        if self.cb_analysis1.isChecked() and self._analysis1:
            a1 = self._analysis1
            if "formula" in a1 and a1["formula"]:
                data_dict["RSM_Formula"] = a1["formula"]
            if "summary" in a1 and a1["summary"] and "summary_text" in a1["summary"]:
                txt = a1["summary"]["summary_text"]
                data_dict["RSM_Model_Ozet"] = replace_scientific_notation(txt)
            if "anova" in a1 and a1["anova"] is not None:
                data_dict["RSM_ANOVA"] = a1["anova"]
            if "vif" in a1 and a1["vif"] is not None:
                data_dict["RSM_VIF"] = a1["vif"]
            if "correlation" in a1 and a1["correlation"] is not None:
                data_dict["RSM_Korelasyon"] = a1["correlation"]
        
        if self.cb_analysis2.isChecked() and self._analysis2:
            a2 = self._analysis2
            if "delta_df" in a2 and a2["delta_df"] is not None:
                data_dict["Analiz2_Delta_Data"] = a2["delta_df"]
            if "group_summary" in a2 and a2["group_summary"] is not None:
                data_dict["Analiz2_Grup_Ozeti"] = a2["group_summary"]
            if "anova" in a2 and a2["anova"] is not None:
                data_dict["Analiz2_ANOVA"] = a2["anova"]
        
        for name, cb in self._extra_checkboxes.items():
            if cb.isChecked() and name in self._extra:
                ex = self._extra[name]
                if ex:
                    prefix = name.replace("-", "").replace(" ", "_")[:20]
                    if "anova_df" in ex and ex["anova_df"] is not None:
                        data_dict[f"{prefix}_ANOVA"] = ex["anova_df"]
                    if "group_means" in ex and ex["group_means"] is not None:
                        data_dict[f"{prefix}_GroupMeans"] = ex["group_means"]
                    if "ranking" in ex and ex["ranking"] is not None:
                        data_dict[f"{prefix}_Ranking"] = ex["ranking"]
                    if "summary" in ex:
                        s = ex.get("summary", "")
                        raw = s if isinstance(s, str) else str(s)
                        data_dict[f"{prefix}_Summary"] = replace_scientific_notation(raw)
                    if "result" in ex and hasattr(ex["result"], "summary"):
                        data_dict[f"{prefix}_Result"] = replace_scientific_notation(str(ex["result"].summary()))
                    if "confusion_matrix" in ex and ex["confusion_matrix"] is not None:
                        data_dict[f"{prefix}_ConfusionMatrix"] = ex["confusion_matrix"]
                    if "coefficients" in ex and ex["coefficients"] is not None:
                        data_dict[f"{prefix}_Coefficients"] = ex["coefficients"]
                    if "discriminant_scores" in ex and ex["discriminant_scores"] is not None:
                        data_dict[f"{prefix}_DiscriminantScores"] = ex["discriminant_scores"]
                    if "classification_report" in ex and ex["classification_report"]:
                        data_dict[f"{prefix}_ClassificationReport"] = replace_scientific_notation(ex["classification_report"])
                    if "summary_text" in ex and ex["summary_text"]:
                        data_dict[f"{prefix}_ModelOzet"] = replace_scientific_notation(ex["summary_text"])
                    if "vif" in ex and ex["vif"] is not None:
                        data_dict[f"{prefix}_VIF"] = ex["vif"]
                    if name == "DOE":
                        if "coded" in ex and ex["coded"] is not None:
                            data_dict["DOE_Tasarim_Kodlanmis"] = ex["coded"]
                        if "real" in ex and ex["real"] is not None:
                            data_dict["DOE_Tasarim_Gercek"] = ex["real"]
        
        if not data_dict:
            QMessageBox.warning(self, "Uyarı", "Aktarılacak veri seçilmedi.")
            return
        
        try:
            path = Path(self._export_path)
            if self.rb_excel.isChecked():
                if not str(path).lower().endswith(".xlsx"):
                    path = path / "export.xlsx"
                export_to_excel(str(path), data_dict)
                self._saved_path = str(path)
            else:
                folder = path if path.is_dir() else path.parent
                export_to_csv(str(folder), data_dict)
                self._saved_path = str(folder)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme hatası: {e}")
    
    def get_saved_path(self) -> str | None:
        return self._saved_path
