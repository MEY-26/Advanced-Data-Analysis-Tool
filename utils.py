"""
Yardımcı fonksiyonlar.
"""

import math
import os
import re
import sys

import pandas as pd


def resource_path(relative_path: str) -> str:
    """PyInstaller ile paketlendiğinde doğru kaynak yolunu döndürür."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def get_icon_path() -> str | None:
    """L2.png ikonunun yolunu döndürür. assets/L2.png veya ana dizindeki L2.png aranır."""
    if getattr(sys, "frozen", False):
        path = os.path.join(sys._MEIPASS, "assets", "L2.png")
        return path if os.path.exists(path) else None
    base = os.path.dirname(os.path.abspath(__file__))
    for rel in ("assets/L2.png", "L2.png"):
        path = os.path.join(base, rel)
        if os.path.exists(path):
            return path
    return None


def format_number(x) -> str:
    """
    Sayiyi bilimsel notasyon kullanmadan string'e cevirir.
    """
    if pd.isna(x):
        return ""
    if isinstance(x, (int, float)):
        try:
            f = float(x)
            if f == 0:
                return "0"
            if math.isinf(f):
                return "inf" if f > 0 else "-inf"
            if isinstance(x, int) and abs(f) < 1e15:
                return str(int(x))
            if abs(f) >= 1e15:
                return str(int(f)) if f == int(f) else f"{f:.0f}"
            if abs(f) < 1e-4 and abs(f) > 0:
                s = f"{f:.20f}".rstrip("0").rstrip(".")
                return s if s else "0"
            s = f"{f:.10f}".rstrip("0").rstrip(".")
            return s if s else "0"
        except (ValueError, OverflowError):
            return str(x)
    return str(x)


def replace_scientific_notation(text: str) -> str:
    """
    Metindeki bilimsel notasyonlari (1.22e-36, 2e+23 vb.) tam sayiya cevirir.
    """
    def replacer(match):
        try:
            val = float(match.group(0))
            return format_number(val)
        except (ValueError, OverflowError):
            return match.group(0)
    pattern = r"\d+\.?\d*[eE][+-]?\d+"
    return re.sub(pattern, replacer, text)
