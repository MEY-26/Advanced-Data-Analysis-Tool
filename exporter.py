"""
Dışa aktarma modülü.
Excel, CSV ve grafik PNG olarak kaydetme.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Any
from matplotlib.figure import Figure

from utils import format_number, replace_scientific_notation


def _format_dataframe_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame'deki sayıları bilimsel notasyon olmadan formatlar."""
    df = df.copy()
    for col in df.columns:
        try:
            if df[col].dtype in ("float64", "float32"):
                df[col] = df[col].apply(lambda x: format_number(x) if pd.notna(x) else "")
        except Exception:
            pass
    return df


def export_to_excel(path: str, data_dict: Dict[str, Any]) -> None:
    """
    Veri ve tablolari Excel dosyasina yazar.
    Her key ayri bir sheet olur. DataFrame olmayan degerler string'e cevrilir.
    
    Args:
        path: Hedef .xlsx dosya yolu
        data_dict: {"Sheet Adi": DataFrame veya yazilabilir obje}
        
    Raises:
        IOError: Dosya yazilamazsa
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, data in data_dict.items():
            # Sheet adi Excel icin gecerli olmali (max 31 karakter, ozel karakter yok)
            safe_name = str(sheet_name)[:31].replace("[", "").replace("]", "").replace(":", "").replace("*", "").replace("?", "")
            if not safe_name:
                safe_name = "Sheet"
            
            if isinstance(data, pd.DataFrame):
                data_fmt = _format_dataframe_numbers(data)
                data_fmt.to_excel(writer, sheet_name=safe_name, index=True)
            elif hasattr(data, "to_frame"):
                data.to_frame().to_excel(writer, sheet_name=safe_name, index=True)
            elif isinstance(data, str):
                text = replace_scientific_notation(data.strip())
                lines = text.splitlines()
                if not lines:
                    lines = [text]
                df_lines = pd.DataFrame({"Satır": range(1, len(lines) + 1), "İçerik": lines})
                df_lines.to_excel(writer, sheet_name=safe_name, index=False)
            else:
                pd.DataFrame({"Value": [str(data)]}).to_excel(writer, sheet_name=safe_name, index=False)


def export_to_csv(folder: str, data_dict: Dict[str, Any]) -> None:
    """
    Her veri ayri bir CSV dosyasi olarak kaydedilir.
    
    Args:
        folder: Hedef klasor
        data_dict: {"DosyaAdi": DataFrame veya yazilabilir obje}
        
    Raises:
        IOError: Klasor/dosya olusturulamazsa
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    
    for name, data in data_dict.items():
        safe_name = str(name).replace(" ", "_").replace("/", "-")[:50]
        filepath = folder / f"{safe_name}.csv"
        
        if isinstance(data, pd.DataFrame):
            data_fmt = _format_dataframe_numbers(data)
            data_fmt.to_csv(filepath, index=True, encoding="utf-8-sig")
        elif hasattr(data, "to_frame"):
            data.to_frame().to_csv(filepath, index=True, encoding="utf-8-sig")
        elif isinstance(data, str):
            text = replace_scientific_notation(data.strip())
            lines = text.splitlines()
            if not lines:
                lines = [text]
            df_lines = pd.DataFrame({"Satır": range(1, len(lines) + 1), "İçerik": lines})
            df_lines.to_csv(filepath, index=False, encoding="utf-8-sig")
        else:
            pd.DataFrame({"Value": [str(data)]}).to_csv(filepath, index=False, encoding="utf-8-sig")


def export_figures(folder: str, figures_dict: Dict[str, Figure]) -> None:
    """
    Grafikleri PNG olarak kaydeder.
    
    Args:
        folder: Hedef klasor
        figures_dict: {"DosyaAdi": matplotlib Figure}
        
    Raises:
        IOError: Klasor/dosya olusturulamazsa
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    
    for name, fig in figures_dict.items():
        if fig is None:
            continue
        safe_name = str(name).replace(" ", "_").replace("/", "-")[:50]
        filepath = folder / f"{safe_name}.png"
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        import matplotlib.pyplot as mpl_plt
        mpl_plt.close(fig)
