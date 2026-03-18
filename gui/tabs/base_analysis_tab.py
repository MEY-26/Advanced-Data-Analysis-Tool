"""
Temel analiz sekmesi - ortak yapı.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QComboBox
from PySide6.QtCore import Qt
from typing import Dict, List, Optional


class BaseAnalysisTab(QWidget):
    """Tüm analiz sekmeleri için temel sınıf."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._df = None
        self._column_roles: Optional[Dict[str, List[str]]] = None
        self._results = {}
    
    def set_data(self, df) -> None:
        """Veriyi günceller."""
        self._df = df
    
    def set_column_roles(self, roles: Optional[Dict[str, List[str]]]) -> None:
        """Sütun rollerini günceller."""
        self._column_roles = roles
    
    def get_results(self) -> dict:
        """Analiz sonuçlarını döndürür (export için)."""
        return self._results
