"""
Sütun atama diyalogu - Minitab tarzı.
Kullanıcı Excel sütunlarını Response, Faktör, Kovaryat vb. rollerine atar.
"""

from typing import Dict, List, Optional, Any
import pandas as pd

from data_loader import _normalize_col_name
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QDialogButtonBox,
    QSplitter,
    QFrame,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont


# Rol tipleri
ROLE_RESPONSE = "response"
ROLE_NUMERIC_FACTORS = "numeric_factors"
ROLE_CATEGORICAL_FACTORS = "categorical_factors"
ROLE_COVARIATES = "covariates"
ROLE_BLOCK = "block"

ROLE_LABELS = {
    ROLE_RESPONSE: "Response (bağımlı değişken)",
    ROLE_NUMERIC_FACTORS: "Numerik Faktörler",
    ROLE_CATEGORICAL_FACTORS: "Kategorik Faktörler",
    ROLE_COVARIATES: "Kovaryatlar",
    ROLE_BLOCK: "Blok Değişkenleri",
}


def _infer_column_type(series: pd.Series) -> str:
    """Kolonun sayısal mı kategorik mi olduğunu tahmin eder."""
    numeric_count = pd.to_numeric(series, errors="coerce").notna().sum()
    total = len(series.dropna())
    if total == 0:
        return "numeric"
    if numeric_count / total >= 0.8:
        return "numeric"
    return "categorical"


class ColumnDialog(QDialog):
    """
    Sütun atama diyalogu.
    Sol: Excel sütunları, Sağ: Rol kutuları.
    Çift tıklama veya ok butonları ile atama.
    """
    
    def __init__(self, df: pd.DataFrame, parent=None, initial_roles: Optional[Dict[str, List[str]]] = None):
        super().__init__(parent)
        self._df = df
        self._column_types: Dict[str, str] = {}
        for col in df.columns:
            self._column_types[str(col)] = _infer_column_type(df[col])
        
        self.setWindowTitle("Sütun Ataması")
        self.setMinimumSize(700, 500)
        self.resize(800, 550)
        self._setup_ui()
        self._populate_columns()
        if initial_roles:
            self._apply_initial_roles(initial_roles)
        self.response_list.setFocus()
    
    def _apply_initial_roles(self, roles: Dict[str, List[str]]) -> None:
        """Mevcut rol atamalarini kutulara yukler (duzenleme icin)."""
        role_map = {
            "response": ROLE_RESPONSE,
            "numeric_factors": ROLE_NUMERIC_FACTORS,
            "categorical_factors": ROLE_CATEGORICAL_FACTORS,
            "covariates": ROLE_COVARIATES,
            "block": ROLE_BLOCK,
        }
        # Normalize edilmis kolon adlarini ham df'deki orijinal adlarla eslestir
        norm_to_orig = {_normalize_col_name(c): c for c in self._df.columns}
        for key, role in role_map.items():
            for col in roles.get(key, []):
                orig = norm_to_orig.get(_normalize_col_name(col), col)
                if orig in self._df.columns:
                    self._add_to_role(role, orig)
        self._refresh_columns_list()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        info = QLabel("Excel dosyanızdaki sütunları analiz rollerine atayın. "
                      "Önce hedef rol kutusuna tıklayın (örn. Response), sonra sütuna çift tıklayın veya 'Seçileni ata' kullanın. "
                      "Delta analizi için Response'a hem Öncesi hem Sonrası ekleyin.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol: Mevcut sütunlar
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Mevcut Sütunlar:"))
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.columns_list.itemDoubleClicked.connect(self._on_assign_selected)
        left_layout.addWidget(self.columns_list)
        splitter.addWidget(left)
        
        # Sağ: Rol kutuları
        right = QScrollArea()
        right.setWidgetResizable(True)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Hedef rol: hangi kutuya atama yapılacak (varsayılan: Response)
        self._target_role = ROLE_RESPONSE

        # Response (birden fazla olabilir; Delta için Öncesi+Sonrası gerekir)
        self.response_group = QGroupBox(ROLE_LABELS[ROLE_RESPONSE])
        resp_layout = QVBoxLayout(self.response_group)
        self.response_list = QListWidget()
        self.response_list.setMaximumHeight(120)
        self.response_list.itemDoubleClicked.connect(lambda: self._on_remove_from_role(ROLE_RESPONSE))
        self.response_list.installEventFilter(self)
        resp_layout.addWidget(self.response_list)
        right_layout.addWidget(self.response_group)

        # Numerik Faktörler
        self.numeric_group = QGroupBox(ROLE_LABELS[ROLE_NUMERIC_FACTORS])
        num_layout = QVBoxLayout(self.numeric_group)
        self.numeric_list = QListWidget()
        self.numeric_list.setMaximumHeight(100)
        self.numeric_list.itemDoubleClicked.connect(lambda: self._on_remove_from_role(ROLE_NUMERIC_FACTORS))
        self.numeric_list.installEventFilter(self)
        num_layout.addWidget(self.numeric_list)
        right_layout.addWidget(self.numeric_group)

        # Kategorik Faktörler
        self.categorical_group = QGroupBox(ROLE_LABELS[ROLE_CATEGORICAL_FACTORS])
        cat_layout = QVBoxLayout(self.categorical_group)
        self.categorical_list = QListWidget()
        self.categorical_list.setMaximumHeight(100)
        self.categorical_list.itemDoubleClicked.connect(lambda: self._on_remove_from_role(ROLE_CATEGORICAL_FACTORS))
        self.categorical_list.installEventFilter(self)
        cat_layout.addWidget(self.categorical_list)
        right_layout.addWidget(self.categorical_group)

        # Kovaryatlar
        self.covariates_group = QGroupBox(ROLE_LABELS[ROLE_COVARIATES])
        cov_layout = QVBoxLayout(self.covariates_group)
        self.covariates_list = QListWidget()
        self.covariates_list.setMaximumHeight(80)
        self.covariates_list.itemDoubleClicked.connect(lambda: self._on_remove_from_role(ROLE_COVARIATES))
        self.covariates_list.installEventFilter(self)
        cov_layout.addWidget(self.covariates_list)
        right_layout.addWidget(self.covariates_group)

        # Blok
        self.block_group = QGroupBox(ROLE_LABELS[ROLE_BLOCK])
        block_layout = QVBoxLayout(self.block_group)
        self.block_list = QListWidget()
        self.block_list.setMaximumHeight(80)
        self.block_list.itemDoubleClicked.connect(lambda: self._on_remove_from_role(ROLE_BLOCK))
        self.block_list.installEventFilter(self)
        block_layout.addWidget(self.block_list)
        right_layout.addWidget(self.block_group)
        
        right_layout.addStretch()
        right.setWidget(right_widget)
        splitter.addWidget(right)
        
        splitter.setSizes([250, 450])
        layout.addWidget(splitter)
        
        # Atama butonları
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        assign_btn = QPushButton("Seçileni ata →")
        assign_btn.clicked.connect(self._on_assign_selected)
        btn_row.addWidget(assign_btn)
        layout.addLayout(btn_row)
        
        # Dialog butonları
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self._role_lists = {
            ROLE_RESPONSE: self.response_list,
            ROLE_NUMERIC_FACTORS: self.numeric_list,
            ROLE_CATEGORICAL_FACTORS: self.categorical_list,
            ROLE_COVARIATES: self.covariates_list,
            ROLE_BLOCK: self.block_list,
        }
        self._list_to_role = {lst: role for role, lst in self._role_lists.items()}
    
    def eventFilter(self, obj, event) -> bool:
        """Hedef rol kutusunu güncelle: hangi liste odaklandıysa oraya atama yapılır."""
        if event.type() == QEvent.Type.FocusIn and obj in self._list_to_role:
            self._target_role = self._list_to_role[obj]
        return super().eventFilter(obj, event)

    def _populate_columns(self) -> None:
        """Sütun listesini doldurur."""
        self.columns_list.clear()
        for col in self._df.columns:
            ctype = self._column_types.get(str(col), "?")
            item = QListWidgetItem(f"{col} ({ctype})")
            item.setData(Qt.ItemDataRole.UserRole, str(col))
            self.columns_list.addItem(item)
    
    def _get_assigned_columns(self) -> set:
        """Atanmış tüm sütunları döndürür."""
        assigned = set()
        for lst in self._role_lists.values():
            for i in range(lst.count()):
                item = lst.item(i)
                if item:
                    assigned.add(item.data(Qt.ItemDataRole.UserRole))
        return assigned
    
    def _on_assign_selected(self) -> None:
        """Seçili sütunları hedef role atar (son tıklanan rol kutusu). Varsayılan: Response."""
        selected = [self.columns_list.item(i).data(Qt.ItemDataRole.UserRole)
                    for i in range(self.columns_list.count())
                    if self.columns_list.item(i).isSelected()]
        if not selected:
            return

        assigned = self._get_assigned_columns()
        for col in selected:
            if col in assigned:
                continue
            self._add_to_role(self._target_role, col)
            assigned.add(col)

        self._refresh_columns_list()
    
    def _add_to_role(self, role: str, col: str) -> None:
        lst = self._role_lists[role]
        item = QListWidgetItem(col)
        item.setData(Qt.ItemDataRole.UserRole, col)
        lst.addItem(item)
    
    def _on_remove_from_role(self, role: str) -> None:
        lst = self._role_lists[role]
        row = lst.currentRow()
        if row >= 0:
            lst.takeItem(row)
            self._refresh_columns_list()
    
    def _remove_from_list(self, lst: QListWidget) -> None:
        while lst.count():
            lst.takeItem(0)
    
    def _refresh_columns_list(self) -> None:
        """Atanmamış sütunları gösterir."""
        assigned = self._get_assigned_columns()
        for i in range(self.columns_list.count()):
            item = self.columns_list.item(i)
            col = item.data(Qt.ItemDataRole.UserRole)
            item.setHidden(col in assigned)
    
    def _on_accept(self) -> None:
        """Kabul etmeden önce doğrulama."""
        roles = self.get_roles()
        if not roles.get(ROLE_RESPONSE):
            QMessageBox.warning(
                self,
                "Eksik Atama",
                "En az bir Response (bağımlı değişken) atanmalıdır."
            )
            return
        self.accept()
    
    def get_roles(self) -> Dict[str, List[str]]:
        """Atanmış rollerin sözlüğünü döndürür."""
        result = {
            ROLE_RESPONSE: [],
            ROLE_NUMERIC_FACTORS: [],
            ROLE_CATEGORICAL_FACTORS: [],
            ROLE_COVARIATES: [],
            ROLE_BLOCK: [],
        }
        for role, lst in self._role_lists.items():
            for i in range(lst.count()):
                item = lst.item(i)
                if item:
                    result[role].append(item.data(Qt.ItemDataRole.UserRole))
        return result
