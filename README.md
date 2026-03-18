# Advanced Data Analysis Tool

**Statistical analysis and DOE desktop application.** ANOVA, MANOVA, RSM, GRA, DFA, MRA. Excel import, surface plots, export. Built with PySide6, statsmodels, and scikit-learn.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **Excel/CSV Import** — Load data from Excel (.xlsx, .xls) with sheet selection and flexible column mapping
- **Dynamic Column Assignment** — Assign columns to roles (Response, Factors, Covariates, Block) via intuitive dialog
- **Data Filtering** — Filter by categorical values (Delik, Olcum) and numeric ranges (Devir, Feed, Paso, Numune)
- **Outlier Detection** — IQR and Z-score methods with visual highlighting
- **Export** — Excel (multi-sheet), CSV, and PNG graphics

---

## Analysis Methods

| Tab | Method | Description |
|-----|--------|-------------|
| **Veri** | Data View | Raw/filtered data table, data quality summary |
| **One-Way ANOVA** | One-way variance analysis | Single categorical factor effect; Tukey HSD, Levene |
| **Two-Way ANOVA** | Two-way variance analysis | Two factors + interaction; Tukey, Levene |
| **MANOVA** | Multivariate ANOVA | Multiple responses; Wilks' Lambda, Pillai, Hotelling, Roy |
| **ANCOVA** | Analysis of covariance | Factor effects with covariate control |
| **GRA** | Gray Relational Analysis | Multi-criteria ranking; reference vs comparison series |
| **DFA** | Discriminant Function Analysis | Group separation; canonical variates |
| **MRA** | Multiple Regression Analysis | Linear regression; coefficients, VIF, diagnostics |
| **DOE** | Design of Experiments | Factorial designs; coding, analysis |
| **RSM** | Response Surface Methodology | 2nd-order polynomial; surface/contour plots, lack-of-fit |
| **Delta** | Change Analysis | Before–after metrics; absolute, percent, improvement |

---

## Installation

### Requirements

- **Python:** 3.9+ (3.10 or 3.11 recommended)
- **Packages:** PySide6, pandas, openpyxl, statsmodels, scipy, numpy, matplotlib, scikit-learn

### Setup

```bash
# Clone the repository
git clone https://github.com/MEY-26/Advanced-Data-Analysis-Tool.git
cd Advanced-Data-Analysis-Tool

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## Usage

### 1. Load Data

- Click **Excel Dosyası Seç** (or **File > Open**, `Ctrl+O`)
- Select an Excel file and choose the sheet
- In the **Column Assignment** dialog, map columns to roles:
  - **Response:** Dependent variable(s)
  - **Numeric Factors:** Devir, Feed, Paso, etc.
  - **Categorical Factors:** Delik, Olcum, etc.
  - **Covariates:** For ANCOVA
  - **Block:** For blocking variables

### 2. Filter Data

Use the left panel filters to restrict data by:
- **Delik** (kafa / flans)
- **Olcum** (oval / silindir / konik)
- **Numune, Devir, Feed, Paso** (min/max ranges)

Click **Filtrele** to apply.

### 3. Run Analyses

Switch between tabs to run different analyses. Each tab has:
- Parameter selection (Response, Factors, etc.)
- Run button
- Result tabs (Summary, ANOVA, Post-Hoc, Plots, Warnings)

### 4. Export

**File > Disa Aktar** (`Ctrl+E`) to export:
- Filtered data
- RSM results (Model Summary, ANOVA, VIF, Correlation)
- Delta results (Group summary)
- One-Way, Two-Way, MANOVA, ANCOVA, GRA, DFA, MRA, DOE results
- Format: **Excel (.xlsx)** or **CSV**
- Graphics: **PNG** (residuals, QQ, surface, contour, boxplot, etc.)

---

## Expected Data Structure

Excel columns (names are case-insensitive):

| Column | Type | Description |
|--------|------|-------------|
| Numune | int | Sample ID |
| Delik | categorical | kafa / flans |
| Devir | numeric | Spindle speed |
| Feed | numeric | Feed rate |
| Paso | numeric | Depth of cut |
| Olcum | categorical | oval / silindir / konik |
| Oncesi | numeric | Before measurement |
| Sonrasi | numeric | After measurement |

---

## Building EXE (Standalone)

For distribution without Python:

```bash
pip install pyinstaller
python build_exe.py
```

Output: `dist/Data_Analysis.exe` — double-click to run, no Python required.

---

## Project Structure

```
Advanced-Data-Analysis-Tool/
├── main.py                 # Entry point
├── requirements.txt
├── build_exe.py            # PyInstaller build script
├── Data_Analysis.spec      # PyInstaller spec
├── data_loader.py          # Excel load, clean, validate
├── exporter.py             # Excel/CSV export
├── plots.py                # Matplotlib plots
├── utils.py
├── analysis/
│   ├── rsm.py              # Response Surface Methodology
│   ├── delta.py            # Change analysis
│   ├── one_way_anova.py
│   ├── two_way_anova.py
│   ├── manova.py
│   ├── ancova.py
│   ├── gra.py              # Gray Relational Analysis
│   ├── dfa.py              # Discriminant Function Analysis
│   ├── mra.py              # Multiple Regression
│   ├── doe.py              # Design of Experiments
│   ├── outliers.py
│   ├── posthoc.py
│   └── ...
└── gui/
    ├── main_window.py
    ├── data_view.py
    ├── analysis1_tab.py    # RSM
    ├── analysis2_tab.py    # Delta
    ├── export_dialog.py
    ├── column_dialog.py
    ├── help_tab.py         # Parameter documentation (TR/EN)
    └── tabs/
        ├── oneway_tab.py
        ├── twoway_tab.py
        ├── manova_tab.py
        ├── ancova_tab.py
        ├── gra_tab.py
        ├── dfa_tab.py
        ├── mra_tab.py
        └── doe_tab.py
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| GUI | PySide6 (Qt for Python) |
| Data | pandas, openpyxl |
| Statistics | statsmodels, scipy |
| Machine Learning | scikit-learn |
| Plots | matplotlib |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+E` | Export |
| `Ctrl+Q` | Quit |

---

## License

MIT License — see [LICENSE](LICENSE).

---

# RSM/ANOVA ve Değişim Analizi GUI Uygulaması

Talaşlı imalat operasyonuna ait ölçüm verilerini Excel'den okuyup, RSM (Yanıt Yüzeyi Yöntemi) / ANOVA ve Değişim Analizi yapan masaüstü GUI uygulaması.

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python main.py
```

## Kullanım Senaryosu

1. **Dosya Yükleme:** "Excel Dosyası Seç" butonu ile Excel dosyasını seçin. Sayfa (sheet) seçimi dropdown'dan yapılır.
2. **Filtreleme:** Veri tablosu görünümünde Numune, Delik, Ölçüm ve Devir/Feed/Paso aralıklarına göre filtre uygulayın.
3. **Analiz 1 (RSM):** Öncesi ölçümünü response olarak kullanarak tezgah parametreleri ile ilişkiyi modelleyin. ANOVA, residual grafikleri, surface/contour grafikleri görüntülenir.
4. **Analiz 2 (Delta):** Sonrası–Öncesi değişim metriklerini (mutlak, yüzdesel, iyileşme) analiz edin. Grup bazlı özet tablolar ve en çok iyileştiren parametre kombinasyonları gösterilir.
5. **Dışa Aktarma:** Dosya > Dışa Aktar ile filtreli veri, analiz sonuçları ve grafikleri Excel veya CSV olarak kaydedin.

## Parametre Açıklamaları

Uygulama içinde **Parametre Açıklamaları** sekmesi tüm analiz yöntemlerini, formülleri ve parametreleri detaylıca açıklar (Türkçe/İngilizce).

## Ek Belgeler

- **KURULUM.md** — Kurulum ve EXE oluşturma kılavuzu
- **KURULUM.txt** — Kısa kurulum notları
