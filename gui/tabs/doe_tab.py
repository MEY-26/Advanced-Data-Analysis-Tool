"""
DOE (Deney Tasarimi) sekmesi.
Faktor tanim tablosu, tasarim olusturma, kodlanmis/gercek matris.
"""

import sys
import pandas as pd
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QLabel,
    QSpinBox,
    QTableView,
    QFileDialog,
    QMessageBox,
    QApplication,
    QStackedWidget,
    QScrollArea,
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

from gui.tabs.base_analysis_tab import BaseAnalysisTab
from analysis.doe import (
    generate_full_factorial,
    generate_fractional_factorial,
    generate_ccd,
    generate_box_behnken,
    generate_d_optimal,
    generate_i_optimal,
    decode_design,
)
from analysis.coding import code_dataframe
from analysis.rsm import NUMERIC_FACTORS
from utils import format_number


class DoeTab(BaseAnalysisTab):
    """DOE tasarim olusturucu arayuzu."""

    DESIGN_TYPES = [
        "Full Factorial",
        "Fractional Factorial",
        "CCD",
        "Box-Behnken",
        "D-Optimal",
        "I-Optimal",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._coded_df: pd.DataFrame | None = None
        self._real_df: pd.DataFrame | None = None
        self._factor_ranges: dict = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        left = QWidget()
        left.setMinimumWidth(280)
        left_layout = QVBoxLayout(left)

        # Tasarim tipi
        design_group = QGroupBox("Tasarim Tipi")
        design_layout = QVBoxLayout(design_group)
        self.design_combo = QComboBox()
        self.design_combo.addItems(self.DESIGN_TYPES)
        self.design_combo.currentTextChanged.connect(self._on_design_type_changed)
        design_layout.addWidget(self.design_combo)
        left_layout.addWidget(design_group)

        # Faktor tanim tablosu
        factor_group = QGroupBox("Faktorler")
        factor_layout = QVBoxLayout(factor_group)
        self.factor_table = QTableWidget()
        self.factor_table.setColumnCount(4)
        self.factor_table.setHorizontalHeaderLabels(["Faktor Adi", "Min", "Max", "Seviye"])
        self.factor_table.horizontalHeader().setStretchLastSection(True)
        factor_layout.addWidget(self.factor_table)
        btn_layout = QHBoxLayout()
        self.add_factor_btn = QPushButton("Faktor Ekle")
        self.add_factor_btn.clicked.connect(self._add_factor_row)
        self.remove_factor_btn = QPushButton("Faktor Sil")
        self.remove_factor_btn.clicked.connect(self._remove_factor_row)
        btn_layout.addWidget(self.add_factor_btn)
        btn_layout.addWidget(self.remove_factor_btn)
        factor_layout.addLayout(btn_layout)
        left_layout.addWidget(factor_group)

        # CCD parametreleri
        self.ccd_group = QGroupBox("CCD Parametreleri")
        ccd_layout = QVBoxLayout(self.ccd_group)
        ccd_layout.addWidget(QLabel("Alpha:"))
        self.alpha_combo = QComboBox()
        self.alpha_combo.addItems(["orthogonal", "rotatable"])
        ccd_layout.addWidget(self.alpha_combo)
        ccd_layout.addWidget(QLabel("Merkez (factorial, star):"))
        ccd_h = QHBoxLayout()
        self.center_fact_spin = QSpinBox()
        self.center_fact_spin.setRange(0, 20)
        self.center_fact_spin.setValue(4)
        self.center_star_spin = QSpinBox()
        self.center_star_spin.setRange(0, 20)
        self.center_star_spin.setValue(4)
        ccd_h.addWidget(self.center_fact_spin)
        ccd_h.addWidget(self.center_star_spin)
        ccd_layout.addLayout(ccd_h)
        left_layout.addWidget(self.ccd_group)

        # D/I-Optimal parametreleri
        self.optimal_group = QGroupBox("D/I-Optimal Parametreleri")
        opt_layout = QVBoxLayout(self.optimal_group)
        opt_layout.addWidget(QLabel("Deney sayisi (n_runs):"))
        self.n_runs_spin = QSpinBox()
        self.n_runs_spin.setRange(4, 500)
        self.n_runs_spin.setValue(20)
        opt_layout.addWidget(self.n_runs_spin)
        left_layout.addWidget(self.optimal_group)

        self.create_btn = QPushButton("Tasarim Olustur")
        self.create_btn.clicked.connect(self._create_design)
        left_layout.addWidget(self.create_btn)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()

        # Sag panel
        right = QTabWidget()
        self.coded_table = QTableView()
        self.coded_model = QStandardItemModel()
        self.coded_table.setModel(self.coded_model)
        right.addTab(self.coded_table, "Tasarim Matrisi (Kodlanmis)")
        self.real_table = QTableView()
        self.real_model = QStandardItemModel()
        self.real_table.setModel(self.real_model)
        right.addTab(self.real_table, "Tasarim Matrisi (Gercek)")
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        self.summary_browser = QLabel("")
        self.summary_browser.setWordWrap(True)
        summary_layout.addWidget(self.summary_browser)
        self.export_excel_btn = QPushButton("Excel'e Aktar")
        self.export_excel_btn.clicked.connect(self._export_to_excel)
        summary_layout.addWidget(self.export_excel_btn)
        right.addTab(summary_widget, "Tasarim Ozeti")
        left.setMinimumWidth(240)
        scroll = QScrollArea()
        scroll.setWidget(left)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(scroll, 1)
        layout.addWidget(right, 3)

        self._on_design_type_changed(self.design_combo.currentText())

    def _on_design_type_changed(self, text: str) -> None:
        is_ccd = text == "CCD"
        is_optimal = text in ("D-Optimal", "I-Optimal")
        self.ccd_group.setVisible(is_ccd)
        self.optimal_group.setVisible(is_optimal)

    def _add_factor_row(self) -> None:
        r = self.factor_table.rowCount()
        self.factor_table.insertRow(r)
        self.factor_table.setItem(r, 0, QTableWidgetItem(""))
        self.factor_table.setItem(r, 1, QTableWidgetItem("0"))
        self.factor_table.setItem(r, 2, QTableWidgetItem("1"))
        self.factor_table.setItem(r, 3, QTableWidgetItem("2"))

    def _remove_factor_row(self) -> None:
        r = self.factor_table.currentRow()
        if r >= 0:
            self.factor_table.removeRow(r)

    def _get_factors_from_table(self) -> list:
        factors = []
        for r in range(self.factor_table.rowCount()):
            name_item = self.factor_table.item(r, 0)
            if name_item and name_item.text().strip():
                factors.append(name_item.text().strip())
        return factors

    def _get_factor_ranges_from_table(self) -> dict:
        ranges = {}
        for r in range(self.factor_table.rowCount()):
            name_item = self.factor_table.item(r, 0)
            min_item = self.factor_table.item(r, 1)
            max_item = self.factor_table.item(r, 2)
            if name_item and name_item.text().strip():
                try:
                    xmin = float(min_item.text()) if min_item else 0.0
                    xmax = float(max_item.text()) if max_item else 1.0
                    ranges[name_item.text().strip()] = (xmin, xmax)
                except ValueError:
                    pass
        return ranges

    def _get_levels_from_table(self) -> dict:
        levels = {}
        for r in range(self.factor_table.rowCount()):
            name_item = self.factor_table.item(r, 0)
            min_item = self.factor_table.item(r, 1)
            max_item = self.factor_table.item(r, 2)
            lev_item = self.factor_table.item(r, 3)
            if name_item and name_item.text().strip():
                try:
                    xmin = float(min_item.text()) if min_item else 0.0
                    xmax = float(max_item.text()) if max_item else 1.0
                    nlev = int(lev_item.text()) if lev_item and lev_item.text().isdigit() else 2
                    if nlev < 2:
                        nlev = 2
                    vals = [xmin + (xmax - xmin) * i / (nlev - 1) for i in range(nlev)]
                    levels[name_item.text().strip()] = vals
                except (ValueError, ZeroDivisionError):
                    levels[name_item.text().strip()] = [xmin, xmax]
        return levels

    def _create_design(self) -> None:
        factors = self._get_factors_from_table()
        if not factors:
            self.status_label.setText("En az bir faktor tanimlayin.")
            return
        factor_ranges = self._get_factor_ranges_from_table()
        if len(factor_ranges) != len(factors):
            self.status_label.setText("Tum faktorler icin Min/Max girin.")
            return

        self.create_btn.setEnabled(False)
        self.status_label.setText("Tasarim olusturuluyor...")
        QApplication.processEvents()

        try:
            design_type = self.design_combo.currentText()
            n = len(factors)

            if design_type == "Full Factorial":
                levels = self._get_levels_from_table()
                real_df_raw = generate_full_factorial(levels)
                for c in real_df_raw.columns:
                    if c not in factor_ranges:
                        factor_ranges[c] = (float(real_df_raw[c].min()), float(real_df_raw[c].max()))
                coded_df = code_dataframe(real_df_raw, factor_ranges)
            elif design_type == "Fractional Factorial":
                coded_df = generate_fractional_factorial(n, factor_names=factors)
            elif design_type == "CCD":
                center = (self.center_fact_spin.value(), self.center_star_spin.value())
                coded_df = generate_ccd(
                    n,
                    center=center,
                    alpha=self.alpha_combo.currentText().lower(),
                    face="circumscribed",
                    factor_names=factors,
                )
            elif design_type == "Box-Behnken":
                coded_df = generate_box_behnken(n, center=3, factor_names=factors)
            elif design_type == "D-Optimal":
                n_runs = self.n_runs_spin.value()
                coded_df = generate_d_optimal(n, n_runs, model_order=2, factor_names=factors)
            elif design_type == "I-Optimal":
                n_runs = self.n_runs_spin.value()
                coded_df = generate_i_optimal(n, n_runs, model_order=2, factor_names=factors)
            else:
                coded_df = generate_full_factorial({f: [-1.0, 1.0] for f in factors})

            self._coded_df = coded_df
            self._factor_ranges = {k: v for k, v in factor_ranges.items() if k in coded_df.columns}
            if design_type == "Full Factorial":
                self._real_df = real_df_raw
            else:
                self._real_df = decode_design(coded_df, self._factor_ranges)
            self._results = {
                "coded": self._coded_df,
                "real": self._real_df,
                "factor_ranges": self._factor_ranges,
                "design_type": design_type,
            }

            self._populate_tables()
            self._populate_summary()
            self.status_label.setText(f"Tasarim olusturuldu: {len(coded_df)} deney.")
        except ImportError as e:
            py_path = getattr(sys, "executable", "python")
            msg = (
                f"{e}\n\n"
                f"Python konumu: {py_path}\n\n"
                f"Bu Python ile kurun:\n"
                f'  "{py_path}" -m pip install pyDOE2'
            )
            self.status_label.setText(f"Hata: {e}")
            QMessageBox.warning(self, "DOE Hatasi", msg)
        except Exception as e:
            self.status_label.setText(f"Hata: {e}")
            QMessageBox.warning(self, "DOE Hatasi", str(e))
        finally:
            self.create_btn.setEnabled(True)

    def _populate_tables(self) -> None:
        for tbl, df, model in [
            (self.coded_table, self._coded_df, self.coded_model),
            (self.real_table, self._real_df, self.real_model),
        ]:
            if df is None or df.empty:
                model.setRowCount(0)
                model.setColumnCount(0)
                continue
            model.setRowCount(len(df))
            model.setColumnCount(len(df.columns))
            model.setHorizontalHeaderLabels([str(c) for c in df.columns])
            for i in range(len(df)):
                for j, c in enumerate(df.columns):
                    val = df.iloc[i, j]
                    model.setItem(i, j, QStandardItem(format_number(val) if pd.notna(val) else ""))

    def _populate_summary(self) -> None:
        if self._coded_df is None:
            return
        lines = [
            f"Tasarim tipi: {self._results.get('design_type', '')}",
            f"Toplam deney sayisi: {len(self._coded_df)}",
            f"Faktor sayisi: {len(self._factor_ranges)}",
            "",
            "Faktor araliklari (gercek):",
        ]
        for name, (mn, mx) in self._factor_ranges.items():
            lines.append(f"  {name}: [{mn}, {mx}]")
        self.summary_browser.setText("\n".join(lines))

    def set_data(self, df: pd.DataFrame | None) -> None:
        super().set_data(df)
        if df is not None and not df.empty:
            factors = [
                c
                for c in (self._column_roles.get("numeric_factors", []) if self._column_roles else NUMERIC_FACTORS)
                if c in df.columns
            ]
            if not factors:
                factors = df.select_dtypes(include=["number"]).columns.tolist()[:5]
            self.factor_table.setRowCount(0)
            for f in factors:
                r = self.factor_table.rowCount()
                self.factor_table.insertRow(r)
                vals = pd.to_numeric(df[f], errors="coerce").dropna()
                xmin = float(vals.min()) if len(vals) > 0 else 0.0
                xmax = float(vals.max()) if len(vals) > 0 else 1.0
                self.factor_table.setItem(r, 0, QTableWidgetItem(str(f)))
                self.factor_table.setItem(r, 1, QTableWidgetItem(str(xmin)))
                self.factor_table.setItem(r, 2, QTableWidgetItem(str(xmax)))
                self.factor_table.setItem(r, 3, QTableWidgetItem("2"))

    def _export_to_excel(self) -> None:
        """Tasarim matrisini Excel'e kaydeder."""
        if self._real_df is None or self._real_df.empty:
            QMessageBox.information(self, "DOE", "Once tasarim olusturun.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Excel'e Kaydet",
            str(Path.home()),
            "Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            with pd.ExcelWriter(path, engine="openpyxl") as w:
                self._coded_df.to_excel(w, sheet_name="Kodlanmis", index=False)
                self._real_df.to_excel(w, sheet_name="Gercek", index=False)
            self.status_label.setText(f"Kaydedildi: {path}")
            QMessageBox.information(self, "DOE", f"Dosya kaydedildi:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "DOE Hatasi", str(e))

    def export_to_excel(self) -> str | None:
        """Tasarim matrisini Excel'e kaydeder (programatik). Dosya yolu dondurur veya None."""
        if self._real_df is None or self._real_df.empty:
            return None
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Excel'e Kaydet",
            str(Path.home()),
            "Excel (*.xlsx)",
        )
        if not path:
            return None
        try:
            with pd.ExcelWriter(path, engine="openpyxl") as w:
                self._coded_df.to_excel(w, sheet_name="Kodlanmis", index=False)
                self._real_df.to_excel(w, sheet_name="Gercek", index=False)
            return path
        except Exception:
            return None

    def get_results(self) -> dict:
        return self._results if hasattr(self, "_results") else {}
