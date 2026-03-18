"""
Gray Relational Analysis (GRA).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def normalize_gra(series: pd.Series, direction: str = "larger_better") -> pd.Series:
    """
    0-1 arası normalizasyon.
    larger_better: x_norm = (x - min) / (max - min)
    smaller_better: x_norm = (max - x) / (max - min)
    """
    clean = series.dropna()
    if len(clean) < 1:
        return series
    mn, mx = clean.min(), clean.max()
    if mx == mn:
        return pd.Series(1.0, index=series.index)
    if direction == "larger_better":
        return (series - mn) / (mx - mn)
    return (mx - series) / (mx - mn)


def run_gra(
    df: pd.DataFrame,
    reference_col: str,
    comparison_cols: List[str],
    distinguishing_coef: float = 0.5,
    direction: str = "larger_better",
) -> Dict[str, Any]:
    """
    Gray Relational Analysis çalıştırır.
    
    Args:
        df: DataFrame
        reference_col: Referans seri kolonu
        comparison_cols: Karşılaştırılacak kolonlar
        distinguishing_coef: xi (0-1)
        direction: "larger_better" veya "smaller_better"
        
    Returns:
        {"normalized_df": DataFrame, "grades": Series, "ranking": DataFrame}
    """
    if reference_col not in df.columns:
        raise ValueError(f"Referans kolonu bulunamadı: {reference_col}")
    
    valid_cols = [c for c in comparison_cols if c in df.columns]
    if not valid_cols:
        raise ValueError("Karşılaştırma kolonu bulunamadı.")
    
    data = df[[reference_col] + valid_cols].dropna()
    if len(data) < 2:
        raise ValueError("Yetersiz veri.")
    
    # Normalizasyon
    norm_df = data.copy()
    norm_df[reference_col] = normalize_gra(data[reference_col], direction)
    for c in valid_cols:
        norm_df[c] = normalize_gra(data[c], direction)
    
    # Gray relational grade (ortalama coefficient) - klasik Deng: global delta min/max
    ref_arr = norm_df[reference_col].values
    all_diffs = np.column_stack([
        np.abs(ref_arr - norm_df[c].values) for c in valid_cols
    ])
    global_min = all_diffs.min()
    global_max = all_diffs.max()

    grades = {}
    coeff_dict = {}
    for c in valid_cols:
        diff = np.abs(ref_arr - norm_df[c].values)
        if global_max == global_min:
            coeffs = np.ones_like(diff)
        else:
            coeffs = (global_min + distinguishing_coef * global_max) / (diff + distinguishing_coef * global_max)
        grades[c] = float(np.mean(coeffs))
        coeff_dict[c] = coeffs
    
    coeff_df = pd.DataFrame(coeff_dict, index=norm_df.index)
    grade_series = pd.Series(grades)
    ranking = grade_series.sort_values(ascending=False).reset_index()
    ranking.columns = ["Seri", "Gray_Relational_Grade"]
    ranking["Sıra"] = range(1, len(ranking) + 1)
    
    return {
        "normalized_df": norm_df,
        "grades": grade_series,
        "ranking": ranking,
        "coefficient_matrix": coeff_df,
    }
