"""
Veri tablosu gorunumu, filtreler ve data quality paneli.
"""

import pandas as pd
from utils import format_number
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QLabel,
    QGroupBox,
    QSplitter,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem


class DataView(QWidget):
    """Veri tablosu ve Data Quality paneli."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.model = QStandardItemModel()
        self.table.setModel(self.model)
        layout.addWidget(self.table)
        
        # Data Quality paneli
        quality_group = QGroupBox("Veri Kalitesi")
        quality_layout = QVBoxLayout(quality_group)
        self.quality_label = QLabel("Veri yüklenmedi.")
        quality_layout.addWidget(self.quality_label)
        self.issues_label = QLabel("")
        self.issues_label.setWordWrap(True)
        quality_layout.addWidget(self.issues_label)
        layout.addWidget(quality_group)
    
    def set_data(
        self,
        df: pd.DataFrame | None,
        issues_df: pd.DataFrame | None = None,
    ) -> None:
        """Tabloyu ve kalite bilgisini gunceller."""
        if df is None or df.empty:
            self.model.clear()
            self.model.setColumnCount(0)
            self.model.setRowCount(0)
            self.quality_label.setText("Veri yok.")
            self.issues_label.setText("")
            return
        
        self.model.setRowCount(len(df))
        self.model.setColumnCount(len(df.columns))
        self.model.setHorizontalHeaderLabels([str(c) for c in df.columns])
        
        for i in range(len(df)):
            for j, col in enumerate(df.columns):
                val = df.iloc[i, j]
                if pd.isna(val):
                    item = QStandardItem("")
                else:
                    item = QStandardItem(format_number(val))
                item.setEditable(False)
                self.model.setItem(i, j, item)
        
        self.table.resizeColumnsToContents()
        
        # Kalite ozeti
        missing = df.isnull().sum()
        missing_str = ", ".join([f"{c}: {int(missing[c])}" for c in missing[missing > 0].index]) or "Yok"
        self.quality_label.setText(f"Satir: {len(df)} | Eksik: {missing_str}")
        
        if issues_df is not None and not issues_df.empty:
            ex = str(issues_df.iloc[0].to_dict()) if len(issues_df) > 0 else ""
            self.issues_label.setText(f"Dönüştürülemeyen hücre: {len(issues_df)} adet. Örnek: {ex}")
        else:
            self.issues_label.setText("")
