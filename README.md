# Advanced Data Analysis Tool

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)

A professional desktop application for statistical analysis and Design of Experiments (DOE). Perform ANOVA, MANOVA, Response Surface Methodology, Gray Relational Analysis, Discriminant Function Analysis, and Multiple Regression Analysis — all from an intuitive PySide6 interface with Excel import/export and interactive surface plots.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Launching the Application](#launching-the-application)
  - [Importing Data](#importing-data)
  - [Running Statistical Analyses](#running-statistical-analyses)
  - [Visualising Results](#visualising-results)
  - [Exporting Results](#exporting-results)
- [Supported Analyses](#supported-analyses)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Six statistical methods** — ANOVA, MANOVA, RSM, GRA, DFA, and MRA available from a single workspace.
- **Excel import** — Load `.xlsx` / `.xls` datasets directly; column headers are detected automatically.
- **Interactive surface plots** — 3-D response-surface and contour plots rendered with Matplotlib, rotatable in real time.
- **Results export** — Save analysis reports and plots to Excel or PDF with one click.
- **Clean Qt-based GUI** — Built with PySide6 for a native look and feel on Windows, macOS, and Linux.
- **Powered by industry-standard libraries** — statsmodels for statistical modelling, scikit-learn for preprocessing and machine-learning helpers.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9 or later |
| pip | 22 or later (bundled with Python ≥ 3.9) |

Optional but recommended:

- A virtual environment manager such as `venv` (built-in) or `conda`.

---

## Installation

### 1 — Clone the repository

```bash
git clone https://github.com/MEY-26/Advanced-Data-Analysis-Tool.git
cd Advanced-Data-Analysis-Tool
```

### 2 — Create and activate a virtual environment

```bash
# Using venv (recommended)
python -m venv .venv

# Activate — Windows
.venv\Scripts\activate

# Activate — macOS / Linux
source .venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` file includes:

```
PySide6>=6.6
statsmodels>=0.14
scikit-learn>=1.4
pandas>=2.1
openpyxl>=3.1
matplotlib>=3.8
```

### 4 — Verify the installation

```bash
python -c "import PySide6, statsmodels, sklearn; print('All dependencies installed successfully.')"
```

---

## Usage

### Launching the Application

```bash
python main.py
```

The main window opens with a sidebar listing each available analysis and a central workspace for data and results.

### Importing Data

1. Click **File → Open Dataset** (or press `Ctrl+O`).
2. Select an Excel file (`.xlsx` or `.xls`).
3. The spreadsheet is previewed in the **Data** tab; column headers are imported as variable names.
4. Assign independent variables (factors) and dependent variables (responses) using the column-assignment panel on the right.

### Running Statistical Analyses

Select an analysis from the sidebar and configure it in the settings panel:

**Example — One-Way ANOVA**

```
Analysis      : ANOVA
Response      : Yield
Factor        : Treatment (3 levels: A, B, C)
Alpha (α)     : 0.05
```

Click **Run Analysis**. The ANOVA table, F-statistic, and p-value are displayed in the **Results** tab.

**Example — Multiple Regression Analysis (MRA)**

```
Analysis      : MRA
Response      : Hardness
Predictors    : Temperature, Pressure, Time
```

Click **Run Analysis** to obtain regression coefficients, R², adjusted R², and residual diagnostics.

**Example — Response Surface Methodology (RSM)**

```
Analysis      : RSM
Response      : Yield
Factors       : Temperature (coded: −1 to +1), Pressure (coded: −1 to +1)
Design        : Central Composite Design (CCD)
```

After fitting the model, click **Plot Surface** to open an interactive 3-D response-surface chart.

### Visualising Results

- **Surface Plot** — 3-D mesh or filled-contour map of any two-factor response surface. Drag to rotate; use the toolbar to zoom or save the figure.
- **Residual Plots** — Residuals vs. fitted values, normal Q-Q plot, and scale-location plot for regression diagnostics.
- **Main Effects / Interaction Plots** — Generated automatically for ANOVA and MANOVA designs.

### Exporting Results

| Action | Menu path | Keyboard shortcut |
|---|---|---|
| Export results table to Excel | **File → Export → Excel** | `Ctrl+E` |
| Save current plot as PNG / PDF | **File → Export → Plot** | `Ctrl+Shift+S` |
| Generate full PDF report | **File → Export → PDF Report** | `Ctrl+P` |

---

## Supported Analyses

| Code | Full Name | Typical Use Case |
|---|---|---|
| **ANOVA** | Analysis of Variance | Compare means across two or more groups |
| **MANOVA** | Multivariate Analysis of Variance | Compare multiple response variables simultaneously |
| **RSM** | Response Surface Methodology | Optimise a process with two or more continuous factors |
| **GRA** | Gray Relational Analysis | Rank and compare multi-criteria alternatives under uncertainty |
| **DFA** | Discriminant Function Analysis | Classify observations into predefined groups |
| **MRA** | Multiple Regression Analysis | Model relationships between a response and several predictors |

---

## Project Structure

```
Advanced-Data-Analysis-Tool/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
├── README.md                # This file
├── src/
│   ├── gui/                 # PySide6 windows, dialogs, and widgets
│   ├── analysis/            # Statistical analysis modules
│   │   ├── anova.py
│   │   ├── manova.py
│   │   ├── rsm.py
│   │   ├── gra.py
│   │   ├── dfa.py
│   │   └── mra.py
│   ├── data/                # Data import, validation, and export helpers
│   └── plots/               # Matplotlib surface and diagnostic plots
└── tests/                   # Unit and integration tests
```

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and add tests where appropriate.
3. Ensure all tests pass:
   ```bash
   python -m pytest tests/
   ```
4. Open a pull request describing what you changed and why.

Please follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines and add docstrings to any new public functions or classes.

---

## License

This project is licensed under the [MIT License](LICENSE).
