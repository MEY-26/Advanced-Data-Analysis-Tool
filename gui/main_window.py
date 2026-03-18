"""
Ana pencere. Menu, dosya yukleme, sekme yonetimi.
"""

import pandas as pd
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QComboBox,
    QLabel,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QMenuBar,
    QMenu,
    QApplication,
    QDialog,
    QGroupBox,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QIcon

from gui.widgets import FilterBar
from utils import get_icon_path
from gui.data_view import DataView
from gui.analysis1_tab import Analysis1Tab
from gui.analysis2_tab import Analysis2Tab
from gui.tabs.oneway_tab import OneWayTab
from gui.tabs.twoway_tab import TwoWayTab
from gui.tabs.manova_tab import ManovaTab
from gui.tabs.ancova_tab import AncovaTab
from gui.tabs.gra_tab import GraTab
from gui.tabs.dfa_tab import DfaTab
from gui.tabs.mra_tab import MraTab
from gui.tabs.doe_tab import DoeTab
from gui.help_tab import HelpTab
from gui.export_dialog import ExportDialog
from gui.column_dialog import ColumnDialog
from data_loader import (
    load_excel_raw,
    get_excel_sheets,
    clean_data,
    validate_data,
)


class MainWindow(QMainWindow):
    """Ana uygulama penceresi."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Analysis")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        
        # Veri state
        self._raw_df: pd.DataFrame | None = None
        self._cleaned_df: pd.DataFrame | None = None
        self._issues_df: pd.DataFrame | None = None
        self._filtered_df: pd.DataFrame | None = None
        self._current_file_path: str | None = None
        self._column_roles: dict | None = None
        
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
        self._update_status("Veri yüklenmedi. Dosya > Aç ile Excel seçin.")
    
    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Sol panel: açılır kapanır, Dosya + Filtre (sabit başlıklar, açılır liste değil)
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(200)
        self.left_panel.setMaximumWidth(320)
        self.left_panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)
        
        # Dosya (sabit bölüm, açılır değil)
        file_group = QGroupBox("Dosya")
        file_layout = QVBoxLayout(file_group)
        self.load_btn = QPushButton("Excel Dosyası Seç")
        self.load_btn.clicked.connect(self._on_load_file)
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(QLabel("Sayfa:"))
        self.sheet_combo = QComboBox()
        self.sheet_combo.setEnabled(False)
        self.sheet_combo.currentTextChanged.connect(self._on_sheet_changed)
        file_layout.addWidget(self.sheet_combo)
        self.edit_columns_btn = QPushButton("Sütunları Düzenle")
        self.edit_columns_btn.setToolTip("Yüklü verideki sütun rollerini değiştir (Response, Faktör vb.)")
        self.edit_columns_btn.setEnabled(False)
        self.edit_columns_btn.clicked.connect(self._on_edit_columns)
        file_layout.addWidget(self.edit_columns_btn)
        left_layout.addWidget(file_group)
        
        # Filtreler (sabit bölüm, açılır değil)
        filter_group = QGroupBox("Filtreler")
        filter_layout = QVBoxLayout(filter_group)
        self.filter_bar = FilterBar()
        filter_layout.addWidget(self.filter_bar)
        left_layout.addWidget(filter_group)
        
        left_layout.addStretch()
        
        # Sag: Sekmeler
        self.tabs = QTabWidget()
        self.data_view = DataView()
        self.oneway_tab = OneWayTab()
        self.twoway_tab = TwoWayTab()
        self.manova_tab = ManovaTab()
        self.ancova_tab = AncovaTab()
        self.gra_tab = GraTab()
        self.dfa_tab = DfaTab()
        self.mra_tab = MraTab()
        self.doe_tab = DoeTab()
        self.analysis1_tab = Analysis1Tab()
        self.analysis2_tab = Analysis2Tab()
        self.tabs.addTab(self.data_view, "Veri")
        self.tabs.addTab(self.oneway_tab, "One-Way ANOVA")
        self.tabs.addTab(self.twoway_tab, "Two-Way ANOVA")
        self.tabs.addTab(self.manova_tab, "MANOVA")
        self.tabs.addTab(self.ancova_tab, "ANCOVA")
        self.tabs.addTab(self.gra_tab, "GRA")
        self.tabs.addTab(self.dfa_tab, "DFA")
        self.tabs.addTab(self.mra_tab, "MRA")
        self.tabs.addTab(self.doe_tab, "DOE")
        self.tabs.addTab(self.analysis1_tab, "RSM")
        self.tabs.addTab(self.analysis2_tab, "Delta")
        self.tabs.addTab(HelpTab(), "Parametre Açıklamaları")
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.tabs)
        self.splitter.setSizes([260, 940])
        self.splitter.setCollapsible(0, True)
        self._left_panel_visible = True
        
        # Panel aç/kapa butonu - her zaman görünür (panel dışında)
        self.panel_toggle_btn = QPushButton("◀")
        self.panel_toggle_btn.setToolTip("Sol paneli gizle")
        self.panel_toggle_btn.setFixedSize(22, 80)
        self.panel_toggle_btn.setStyleSheet(
            "QPushButton { background: #e0e0e0; border: 1px solid #ccc; border-radius: 2px; font-size: 10pt; } "
            "QPushButton:hover { background: #d0d0d0; }"
        )
        self.panel_toggle_btn.clicked.connect(self._toggle_left_panel)
        
        main_h = QHBoxLayout()
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)
        main_h.addWidget(self.panel_toggle_btn)
        main_h.addWidget(self.splitter)
        layout.addLayout(main_h)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def _setup_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Dosya")
        open_action = QAction("Aç...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_load_file)
        file_menu.addAction(open_action)
        export_action = QAction("Disa Aktar...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        exit_action = QAction("Çıkış", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("Görünüm")
        self.panel_toggle_action = QAction("Sol paneli gizle", self)
        self.panel_toggle_action.triggered.connect(self._toggle_left_panel)
        view_menu.addAction(self.panel_toggle_action)

        help_menu = menubar.addMenu("Yardım")
        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self) -> None:
        self.filter_bar.filter_applied.connect(self._apply_filter)

    def _toggle_left_panel(self) -> None:
        """Sol paneli aç/kapat."""
        if self._left_panel_visible:
            self.splitter.setSizes([0, 10000])
            self.panel_toggle_btn.setText("▶")
            self.panel_toggle_btn.setToolTip("Sol paneli göster")
            self.panel_toggle_action.setText("Sol paneli göster")
            self._left_panel_visible = False
        else:
            self.splitter.setSizes([260, 940])
            self.panel_toggle_btn.setText("◀")
            self.panel_toggle_btn.setToolTip("Sol paneli gizle")
            self.panel_toggle_action.setText("Sol paneli gizle")
            self._left_panel_visible = True
    
    def _update_status(self, msg: str) -> None:
        self.status_bar.showMessage(msg)
    
    def _on_load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel Dosyası Seç",
            "",
            "Excel (*.xlsx *.xls);;Tüm Dosyalar (*)",
        )
        if not path:
            return
        self._load_file(path)
    
    def _select_sheet(self, path: str, sheets: list[str]) -> str | None:
        """Sayfa seçim diyalogu. Seçilen sayfa adını veya iptalde None döndürür."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Sayfa Seçin")
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("Analiz yapmak istediğiniz sayfayı seçin:"))
        combo = QComboBox()
        combo.addItems(sheets)
        layout.addWidget(combo)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Tamam")
        cancel_btn = QPushButton("İptal")
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return combo.currentText()
        return None
    
    def _load_file(self, path: str, sheet_name: str | None = None) -> None:
        try:
            sheets = get_excel_sheets(path)
            if not sheets:
                QMessageBox.warning(self, "Hata", "Excel dosyasinda sayfa yok.")
                return
            
            if sheet_name is None:
                sheet_name = self._select_sheet(path, sheets)
                if sheet_name is None:
                    return
            
            raw_df = load_excel_raw(path, sheet_name)
            
            # Sütun atama diyalogu
            dlg = ColumnDialog(raw_df, self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            
            column_roles = dlg.get_roles()
            self._raw_df = raw_df
            self._cleaned_df, self._issues_df, self._column_roles = clean_data(raw_df, column_roles)
            self._current_file_path = path
            
            self.sheet_combo.blockSignals(True)
            try:
                self.sheet_combo.clear()
                self.sheet_combo.addItems(sheets)
                self.sheet_combo.setCurrentText(sheet_name)
                self.sheet_combo.setEnabled(True)
            finally:
                self.sheet_combo.blockSignals(False)
            self.edit_columns_btn.setEnabled(True)
            
            self._filtered_df = self._cleaned_df.copy()
            self.filter_bar.set_ranges_from_data(self._cleaned_df, self._column_roles)
            self.data_view.set_data(self._cleaned_df, self._issues_df)
            for tab in [self.oneway_tab, self.twoway_tab, self.manova_tab, self.ancova_tab,
                       self.gra_tab, self.dfa_tab, self.mra_tab, self.doe_tab, self.analysis1_tab, self.analysis2_tab]:
                if hasattr(tab, "set_column_roles"):
                    tab.set_column_roles(self._column_roles)
                tab.set_data(self._filtered_df)
            
            warnings = validate_data(self._cleaned_df, self._column_roles)
            msg = f"Yüklendi: {len(self._cleaned_df)} satır"
            if warnings:
                msg += f" | Uyarılar: {'; '.join(warnings[:2])}"
            self._update_status(msg)
            
        except FileNotFoundError:
            QMessageBox.critical(self, "Hata", f"Dosya bulunamadı: {path}")
        except ValueError as e:
            QMessageBox.critical(self, "Hata", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Yükleme hatası: {e}")
    
    def _on_sheet_changed(self, sheet_name: str) -> None:
        if not self._current_file_path or not sheet_name:
            return
        self._load_file(self._current_file_path, sheet_name)
    
    def _on_edit_columns(self) -> None:
        """Yüklü verinin sütun rollerini düzenlemek için diyalog açar."""
        if self._raw_df is None or self._raw_df.empty:
            QMessageBox.warning(self, "Uyarı", "Önce bir veri dosyası yükleyin.")
            return
        dlg = ColumnDialog(self._raw_df, self, initial_roles=self._column_roles)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        column_roles = dlg.get_roles()
        self._cleaned_df, self._issues_df, self._column_roles = clean_data(self._raw_df, column_roles)
        self.filter_bar.set_ranges_from_data(self._cleaned_df, self._column_roles)
        for tab in [self.oneway_tab, self.twoway_tab, self.manova_tab, self.ancova_tab,
                   self.gra_tab, self.dfa_tab, self.mra_tab, self.doe_tab, self.analysis1_tab, self.analysis2_tab]:
            if hasattr(tab, "set_column_roles"):
                tab.set_column_roles(self._column_roles)
        self._apply_filter(self.filter_bar.get_filter_dict())
        warnings = validate_data(self._cleaned_df, self._column_roles)
        msg = f"Sütun roller güncellendi: {len(self._cleaned_df)} satır"
        if warnings:
            msg += f" | Uyarılar: {'; '.join(warnings[:2])}"
        self._update_status(msg)
    
    def _apply_filter(self, filter_dict: dict) -> None:
        if self._cleaned_df is None:
            return
        df = self._cleaned_df.copy()
        col_map = self.filter_bar.get_filter_column_map()
        
        def _col(key: str) -> str:
            return col_map.get(key, key) if col_map else key
        
        if filter_dict.get("delik"):
            c = _col("delik")
            if c in df.columns:
                df = df[df[c] == filter_dict["delik"]]
        if filter_dict.get("olcum"):
            c = _col("olcum")
            if c in df.columns:
                df = df[df[c] == filter_dict["olcum"]]
        if filter_dict.get("numune_min") is not None:
            c = _col("numune")
            if c in df.columns:
                df = df[df[c] >= filter_dict["numune_min"]]
        if filter_dict.get("numune_max") is not None:
            c = _col("numune")
            if c in df.columns:
                df = df[df[c] <= filter_dict["numune_max"]]
        if filter_dict.get("devir_min") is not None:
            c = _col("devir")
            if c in df.columns:
                df = df[df[c] >= filter_dict["devir_min"]]
        if filter_dict.get("devir_max") is not None:
            c = _col("devir")
            if c in df.columns:
                df = df[df[c] <= filter_dict["devir_max"]]
        if filter_dict.get("feed_min") is not None:
            c = _col("feed")
            if c in df.columns:
                df = df[df[c] >= filter_dict["feed_min"]]
        if filter_dict.get("feed_max") is not None:
            c = _col("feed")
            if c in df.columns:
                df = df[df[c] <= filter_dict["feed_max"]]
        if filter_dict.get("paso_min") is not None:
            c = _col("paso")
            if c in df.columns:
                df = df[df[c] >= filter_dict["paso_min"]]
        if filter_dict.get("paso_max") is not None:
            c = _col("paso")
            if c in df.columns:
                df = df[df[c] <= filter_dict["paso_max"]]
        
        self._filtered_df = df
        self.data_view.set_data(df, self._issues_df)
        for tab in [self.oneway_tab, self.twoway_tab, self.manova_tab, self.ancova_tab,
                   self.gra_tab, self.dfa_tab, self.mra_tab, self.doe_tab, self.analysis1_tab, self.analysis2_tab]:
            tab.set_data(df)
        self._update_status(f"Filtrelendi: {len(df)} satır")
    
    def _on_export(self) -> None:
        if self._filtered_df is None or self._filtered_df.empty:
            QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak veri yok.")
            return
        dlg = ExportDialog(
            self,
            filtered_df=self._filtered_df,
            analysis1_results=self.analysis1_tab.get_results(),
            analysis2_results=self.analysis2_tab.get_results(),
            extra_results={
                "One-Way": self.oneway_tab.get_results(),
                "Two-Way": self.twoway_tab.get_results(),
                "MANOVA": self.manova_tab.get_results(),
                "ANCOVA": self.ancova_tab.get_results(),
                "GRA": self.gra_tab.get_results(),
                "DFA": self.dfa_tab.get_results(),
                "MRA": self.mra_tab.get_results(),
                "DOE": self.doe_tab.get_results(),
            },
        )
        if dlg.exec():
            path = dlg.get_saved_path()
            if path:
                self._update_status(f"Kaydedildi: {path}")
    
    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "Hakkında",
            "Data Analysis\n\n"
            "İstatistiksel veri analizi uygulaması. Excel dosyalarından veri yükleyip "
            "sütun ataması ile analiz rollerini tanımlayabilirsiniz.\n\n"
            "Analizler: One-Way ANOVA, Two-Way ANOVA, MANOVA, ANCOVA, "
            "GRA, DFA, MRA, RSM (Yanıt Yüzeyi), Delta (Değişim Analizi)\n\n"
            "Özellikler: Dinamik sütun eşleme, filtreleme, aykırı değer tespiti, "
            "post-hoc testler (Tukey, Levene), VIF, dağılım grafikleri, Excel/CSV dışa aktarma",
        )
    
    def get_filtered_df(self) -> pd.DataFrame | None:
        return self._filtered_df
    
    def get_cleaned_df(self) -> pd.DataFrame | None:
        return self._cleaned_df
